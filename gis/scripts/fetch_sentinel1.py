"""Chuỗi Sentinel-1 radar 12 tháng — nguồn dữ liệu KHÔNG BỊ MÂY CHẶN.

Vì sao cần: ở Ninh Bình mùa mưa, ảnh quang học Sentinel-2 mất trắng hàng tháng.
Radar bước sóng C xuyên mây, nên mỗi lượt bay đều dùng được, không lượt nào bỏ.

Nguồn: Microsoft Planetary Computer, collection `sentinel-1-rtc` — đã hiệu chỉnh
bức xạ và NẮN THEO ĐỊA HÌNH, ra thẳng gamma0 trên lưới UTM 10 m. Bản GRD thô
trên AWS thì rẻ hơn nhưng còn ở hình học nghiêng, phải tự nắn bằng GCP và tự
hiệu chỉnh bức xạ mới so sánh được giữa các ngày — RTC bỏ hẳn cả hai bước đó.
Ký URL bằng planetary_computer.sign(), không cần tài khoản.

Đọc radar khác đọc ảnh quang:

  * gamma0 lưu ở thang TUYẾN TÍNH (công suất). Trung bình phải lấy trên thang
    tuyến tính rồi mới đổi sang dB; lấy trung bình thẳng trên dB là sai vì dB
    là hàm log — sai lệch tới vài phần mười dB với ruộng không đồng nhất.

  * PHẢI TÁCH THEO HƯỚNG BAY. Cùng một thửa, lượt bay lên (ascending) và lượt
    bay xuống (descending) soi từ hai phía khác nhau nên lệch nhau cả dB. Trộn
    chung sẽ ra một chuỗi răng cưa giả, không phải cây trồng thay đổi.

  * NHIỄU ĐỐM (speckle) là bản chất của radar. Trung bình theo lô trên vài chục
    pixel đã dập phần lớn, nhưng chuỗi vẫn nhiễu hơn NDVI — đọc theo xu hướng.
"""
import csv
import json
import os
from concurrent.futures import ThreadPoolExecutor

import geopandas as gpd
import numpy as np
import planetary_computer as pc
import rasterio
from pystac_client import Client
from rasterio.enums import Resampling
from rasterio.features import geometry_mask
from rasterio.transform import from_bounds
from rasterio.windows import from_bounds as window_from_bounds

BASE = os.path.expanduser("~/Documents/GIS_RiTi_TrangAn")
MPC = "https://planetarycomputer.microsoft.com/api/stac/v1"
UTM = "EPSG:32648"
RES = 10.0
DATE_RANGE = "2025-08-12/2026-08-12"
WORKERS = 4


def read_to_grid(href, bounds, shape):
    with rasterio.open(href) as src:
        win = window_from_bounds(*bounds, transform=src.transform)
        a = src.read(1, window=win, out_shape=shape, resampling=Resampling.bilinear,
                     boundless=True, fill_value=np.nan).astype(np.float32)
    return a


def main():
    os.makedirs(f"{BASE}/data/out/rasters/s1", exist_ok=True)

    aoi = gpd.read_file(f"{BASE}/data/out/aoi_riti.geojson").to_crs(UTM)
    bbox_ll = gpd.read_file(f"{BASE}/data/out/aoi_bbox.geojson")
    minx, miny, maxx, maxy = bbox_ll.to_crs(UTM).total_bounds
    minx, miny = np.floor(minx / RES) * RES, np.floor(miny / RES) * RES
    maxx, maxy = np.ceil(maxx / RES) * RES, np.ceil(maxy / RES) * RES
    W, H = int((maxx - minx) / RES), int((maxy - miny) / RES)
    bounds = (minx, miny, maxx, maxy)
    transform = from_bounds(*bounds, W, H)
    farm = ~geometry_mask(aoi.geometry, out_shape=(H, W), transform=transform,
                          invert=False)

    cat = Client.open(MPC)
    items = list(cat.search(
        collections=["sentinel-1-rtc"],
        intersects=json.loads(bbox_ll.to_json())["features"][0]["geometry"],
        datetime=DATE_RANGE).items())
    items.sort(key=lambda it: it.properties["datetime"])
    print(f"{len(items)} lượt bay Sentinel-1 RTC trong {DATE_RANGE}")
    orb = {}
    for it in items:
        orb[it.properties.get("sat:orbit_state", "?")] = \
            orb.get(it.properties.get("sat:orbit_state", "?"), 0) + 1
    print("theo hướng bay:", orb, "\n")

    prof = dict(driver="GTiff", height=H, width=W, count=2, dtype="float32",
                crs=UTM, transform=transform, nodata=np.nan, compress="deflate")

    def one(it):
        day = it.properties["datetime"][:10]
        orbit = it.properties.get("sat:orbit_state", "?")
        tag = f"{day}_{orbit[:3]}"
        try:
            s = pc.sign(it)
            vv = read_to_grid(s.assets["vv"].href, bounds, (H, W))
            vh = read_to_grid(s.assets["vh"].href, bounds, (H, W))
            ok = np.isfinite(vv) & np.isfinite(vh) & (vv > 0) & (vh > 0) & farm
            if ok.sum() < 10:
                return {"date": day, "orbit": orbit, "scene": it.id, "px": int(ok.sum())}

            with rasterio.open(f"{BASE}/data/out/rasters/s1/s1_{tag}.tif",
                               "w", **prof) as dst:
                dst.write(np.where(ok, vv, np.nan).astype(np.float32), 1)
                dst.write(np.where(ok, vh, np.nan).astype(np.float32), 2)
                dst.descriptions = ("vv_gamma0", "vh_gamma0")

            # Trung bình trên thang tuyến tính rồi mới đổi dB
            mvv, mvh = float(vv[ok].mean()), float(vh[ok].mean())
            rvi = 4 * mvh / (mvv + mvh)      # chỉ số thực vật radar, 0..~1
            return {"date": day, "orbit": orbit, "scene": it.id, "px": int(ok.sum()),
                    "vv_db": round(10 * np.log10(mvv), 3),
                    "vh_db": round(10 * np.log10(mvh), 3),
                    "vh_vv_db": round(10 * np.log10(mvh / mvv), 3),
                    "rvi": round(rvi, 4)}
        except Exception as e:
            return {"date": day, "orbit": orbit, "scene": it.id,
                    "loi": f"{type(e).__name__}: {e}"[:120]}

    rows = []
    with ThreadPoolExecutor(WORKERS) as ex:
        for i, r in enumerate(ex.map(one, items), 1):
            rows.append(r)
            msg = r.get("loi") or (f"VV {r['vv_db']:6.2f} dB  VH {r['vh_db']:6.2f} dB  "
                                   f"RVI {r['rvi']:.3f}" if "vv_db" in r else "ít pixel")
            print(f"[{i:3d}/{len(items)}] {r['date']} {r['orbit'][:4]:4s} {msg}")

    rows.sort(key=lambda r: (r["date"], r["orbit"]))
    keys = ["date", "orbit", "scene", "px", "vv_db", "vh_db", "vh_vv_db", "rvi", "loi"]
    with open(f"{BASE}/data/out/s1_scenes.csv", "w", newline="") as f:
        w = csv.DictWriter(f, fieldnames=keys, extrasaction="ignore")
        w.writeheader()
        w.writerows(rows)

    ok = [r for r in rows if "vv_db" in r]
    print(f"\n{len(ok)}/{len(rows)} lượt bay dùng được (radar không bị mây loại)")
    print("đã ghi: data/out/s1_scenes.csv, data/out/rasters/s1/s1_*.tif")


if __name__ == "__main__":
    main()
