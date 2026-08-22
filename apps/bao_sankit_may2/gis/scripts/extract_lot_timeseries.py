"""Tách dữ liệu THEO TỪNG LÔ: 12 lô × mọi ngày có ảnh -> chuỗi thời gian.

Hai chỗ dễ làm sai, xử lý ở đây:

1. LÔ NHỎ HƠN PIXEL. Lô 4 rộng 0,21 ha, ở lưới Sentinel-2 10 m chỉ khoảng 20
   pixel, mà pixel ngoài rìa thì nửa trong nửa ngoài. Đếm "tâm pixel có rơi
   vào lô không" là mất/thêm cả chục phần trăm diện tích. Ở đây mỗi pixel 10 m
   được chia 4×4 ô con 2,5 m, TRỌNG SỐ của pixel với lô = tỉ lệ ô con nằm
   trong lô, rồi lấy trung bình có trọng số. Vành ngoài vì thế đóng góp đúng
   phần diện tích của nó.

2. MÂY KHÔNG PHỦ ĐỀU. Có ngày lô 1 quang mà lô 7 bị che. Bản cũ vứt cả ngày
   khi farm quá mây; ở đây từng lô tự xét: lô nào đủ pixel hợp lệ thì lô đó có
   số liệu ngày đó. Nhờ vậy chuỗi của mỗi lô dày hơn hẳn so với chuỗi chung.

Radar lấy trung bình trên thang tuyến tính rồi mới đổi dB (xem fetch_sentinel1).
"""
import glob
import os
import re

import geopandas as gpd
import numpy as np
import pandas as pd
import rasterio
from rasterio.features import rasterize
from rasterio.transform import from_bounds

BASE = os.path.expanduser("~/Documents/GIS_RiTi_TrangAn")
UTM = "EPSG:32648"
SUB = 4                 # chia mỗi pixel thành SUB x SUB ô con để lấy trọng số
MIN_VALID = 0.60        # lô phải có >=60% diện tích quang mới ghi nhận ngày đó


def lot_weights(lots, transform, H, W):
    """Trọng số diện tích của từng pixel với từng lô (mảng [n_lo, H, W])."""
    minx, maxy = transform.c, transform.f
    res = transform.a
    fine = from_bounds(minx, maxy - H * res, minx + W * res, maxy, W * SUB, H * SUB)
    out = np.zeros((len(lots), H, W), np.float32)
    for i, geom in enumerate(lots.geometry):
        m = rasterize([(geom, 1)], out_shape=(H * SUB, W * SUB), transform=fine,
                      fill=0, dtype="uint8")
        out[i] = m.reshape(H, SUB, W, SUB).mean(axis=(1, 3))
    return out


def main():
    lots = gpd.read_file(f"{BASE}/data/out/lots.geojson").to_crs(UTM)
    lots = lots.sort_values("lo").reset_index(drop=True)
    ids = list(lots["lo_id"])

    f0 = sorted(glob.glob(f"{BASE}/data/out/rasters/s2/s2_*.tif"))
    if not f0:
        raise SystemExit("chưa có raster Sentinel-2 — chạy fetch_sentinel2.py trước")
    with rasterio.open(f0[0]) as src:
        transform, H, W = src.transform, src.height, src.width

    ww = lot_weights(lots, transform, H, W)
    px_ha = (transform.a ** 2) / 1e4
    print("lô   diện tích   pixel S2 quy đổi")
    for i, r in lots.iterrows():
        print(f"{r['lo_id']}  {r['area_ha']:7.4f} ha   {ww[i].sum():6.1f} px "
              f"(= {ww[i].sum()*px_ha:.4f} ha)")

    # --- Sentinel-2 --------------------------------------------------------
    rows = []
    for f in f0:
        day = re.search(r"s2_(\d{4}-\d\d-\d\d)", f).group(1)
        with rasterio.open(f) as src:
            ndvi, ndmi, valid = src.read(1), src.read(2), src.read(3)
        valid = np.nan_to_num(valid) > 0.5
        for i, lid in enumerate(ids):
            w = ww[i]
            tot = w.sum()
            wv = w * valid
            vf = wv.sum() / tot if tot else 0
            if vf < MIN_VALID:
                continue
            sel = wv > 0
            rows.append({
                "date": day, "lo_id": lid,
                "quang_pct": round(100 * vf, 1),
                "ndvi": round(float(np.nansum(wv[sel] * ndvi[sel]) / wv[sel].sum()), 4),
                "ndmi": round(float(np.nansum(wv[sel] * ndmi[sel]) / wv[sel].sum()), 4)})
    s2 = pd.DataFrame(rows).sort_values(["lo_id", "date"])
    s2.to_csv(f"{BASE}/data/out/lot_s2_timeseries.csv", index=False)
    print(f"\nSentinel-2: {len(s2)} bản ghi lô×ngày trên {s2['date'].nunique()} ngày")
    print(s2.groupby("lo_id")["ndvi"].agg(["count", "mean", "min", "max"]).round(3).to_string())

    # --- Sentinel-1 --------------------------------------------------------
    rows = []
    for f in sorted(glob.glob(f"{BASE}/data/out/rasters/s1/s1_*.tif")):
        m = re.search(r"s1_(\d{4}-\d\d-\d\d)_(\w+)", f)
        day, orbit = m.group(1), m.group(2)
        with rasterio.open(f) as src:
            vv, vh = src.read(1), src.read(2)
        ok = np.isfinite(vv) & np.isfinite(vh)
        for i, lid in enumerate(ids):
            w = ww[i] * ok
            if w.sum() / max(ww[i].sum(), 1e-9) < MIN_VALID:
                continue
            sel = w > 0
            mvv = float(np.sum(w[sel] * vv[sel]) / w[sel].sum())
            mvh = float(np.sum(w[sel] * vh[sel]) / w[sel].sum())
            rows.append({"date": day, "orbit": orbit, "lo_id": lid,
                         "vv_db": round(10 * np.log10(mvv), 3),
                         "vh_db": round(10 * np.log10(mvh), 3),
                         "rvi": round(4 * mvh / (mvv + mvh), 4)})
    s1 = pd.DataFrame(rows)
    if len(s1):
        s1 = s1.sort_values(["lo_id", "date"])
        s1.to_csv(f"{BASE}/data/out/lot_s1_timeseries.csv", index=False)
        print(f"\nSentinel-1: {len(s1)} bản ghi lô×ngày trên {s1['date'].nunique()} ngày")

    # --- bảng ngang + tổng hợp theo lô ------------------------------------
    wide = s2.pivot_table(index="date", columns="lo_id", values="ndvi")
    wide.round(4).to_csv(f"{BASE}/data/out/lot_ndvi_wide.csv")

    g = s2.groupby("lo_id")
    summ = pd.DataFrame({
        "so_ngay_s2": g.size(),
        "ndvi_tb": g["ndvi"].mean().round(3),
        "ndvi_min": g["ndvi"].min().round(3),
        "ndvi_max": g["ndvi"].max().round(3),
        "bien_do": (g["ndvi"].max() - g["ndvi"].min()).round(3),
        "ndmi_tb": g["ndmi"].mean().round(3)})
    if len(s1):
        g1 = s1.groupby("lo_id")
        summ["so_ngay_s1"] = g1.size()
        summ["vh_db_tb"] = g1["vh_db"].mean().round(2)
        summ["rvi_tb"] = g1["rvi"].mean().round(3)

    # --- địa hình theo lô --------------------------------------------------
    # DEM 30 m: một lô 0,2 ha chỉ chiếm ~2 pixel nên đọc theo lô lớn là chính.
    # Vẫn dùng trọng số diện tích như trên, chỉ đổi lưới.
    for nm, col in (("dem", "cao_do_m"), ("slope_deg", "do_doc_deg")):
        p = f"{BASE}/data/out/rasters/{nm}.tif"
        if not os.path.exists(p):
            continue
        with rasterio.open(p) as src:
            a, tr, h, w = src.read(1), src.transform, src.height, src.width
        wt = lot_weights(lots, tr, h, w)
        vals = []
        for i in range(len(lots)):
            m = wt[i] * np.isfinite(a)
            vals.append(round(float(np.sum(m * np.nan_to_num(a)) / m.sum()), 2)
                        if m.sum() > 0 else None)
        summ[col] = pd.Series(vals, index=lots["lo_id"])

    summ = lots.set_index("lo_id")[["area_ha", "area_ve_tay_ha", "chenh_pct"]].join(summ)

    def nhan(r):
        """Nhãn suy từ CHUỖI 12 THÁNG, không phải từ một cặp ngày như bản cũ."""
        if r["ndvi_tb"] >= 0.70 and r["bien_do"] <= 0.35:
            return "Cây lâu năm / vườn tán dày quanh năm"
        if r["bien_do"] >= 0.45:
            return "Luân canh rõ — gieo, lớn, thu theo vụ"
        if r["ndvi_tb"] < 0.40:
            return "Che phủ thưa / đất trống, công trình"
        return "Che phủ trung bình, biến động vừa"

    summ["loai"] = summ.apply(nhan, axis=1)
    summ = summ.reset_index()
    summ.to_csv(f"{BASE}/data/out/lots_summary.csv", index=False)
    print("\n" + summ.to_string(index=False))
    print("\nđã ghi: lot_s2_timeseries.csv, lot_s1_timeseries.csv, "
          "lot_ndvi_wide.csv, lots_summary.csv")


if __name__ == "__main__":
    main()
