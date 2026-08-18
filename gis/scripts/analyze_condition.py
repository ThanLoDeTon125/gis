"""Phân tích tình trạng vùng trồng 12 tháng: chu kỳ canh tác, nước, sức khoẻ lô.

Đây là bước đọc HIỆN TƯỢNG từ số liệu, tách khỏi bước lấy số liệu.

Ràng buộc phải tôn trọng khi đọc: chuỗi quang học có 23 ngày, khoảng cách trung
vị 11 ngày nhưng CÓ MỘT LỖ HỔNG 60 NGÀY (12/01 – 13/03/2026). Một vụ ngắn nằm
gọn trong lỗ đó thì ảnh quang học không thấy. Mọi kết luận về số vụ vì thế phải
kèm cảnh báo cho khoảng này, và phải đối chiếu với radar — nguồn duy nhất có số
liệu liên tục xuyên qua lỗ hổng.

Nội suy chỉ để dò đỉnh, KHÔNG dùng làm số liệu báo cáo: mọi con số in ra đều lấy
từ quan trắc thật.
"""
import os

import numpy as np
import pandas as pd
from scipy.signal import find_peaks

BASE = os.path.expanduser("~/Documents/GIS_RiTi_TrangAn")

MUA_MUA = [5, 6, 7, 8, 9, 10]        # suy từ chính số liệu mưa, xem in ra ở cuối
GAP_CANH_BAO = 35                    # ngày; dài hơn thì không dám khẳng định vụ
PROM = 0.15                          # biên độ tối thiểu để coi là một đỉnh vụ
KHOANG_CACH_DINH = 45                # ngày giữa hai đỉnh


def series_5day(d):
    """Nội suy tuyến tính về lưới 5 ngày để dò đỉnh; không dùng để báo cáo số."""
    d = d.sort_values("date")
    idx = pd.date_range(d["date"].min(), d["date"].max(), freq="5D")
    s = pd.Series(d["ndvi"].values, index=d["date"]).reindex(
        idx.union(d["date"])).interpolate("time").reindex(idx)
    return s


def chu_ky(d):
    """Đỉnh sinh trưởng + đáy đứng trước nó -> một vụ."""
    s = series_5day(d)
    if len(s) < 6:
        return []
    pk, _ = find_peaks(s.values, prominence=PROM,
                       distance=max(2, KHOANG_CACH_DINH // 5))
    obs = d.sort_values("date")
    gaps = obs["date"].diff().dt.days
    out = []
    for i in pk:
        t_peak = s.index[i]
        j = i
        while j > 0 and s.values[j - 1] < s.values[j]:
            j -= 1
        t_low = s.index[j]
        # Đỉnh có đáng tin không: quanh đỉnh có quan trắc thật trong vòng 12 ngày?
        near = (obs["date"] - t_peak).abs().dt.days.min()
        # Đoạn từ đáy tới đỉnh có nằm vắt qua lỗ hổng dài không?
        span = obs[(obs["date"] >= t_low) & (obs["date"] <= t_peak)]
        gmax = gaps[span.index].max() if len(span) else np.nan
        out.append({
            "dinh": t_peak, "ndvi_dinh": round(float(s.values[i]), 3),
            "day": t_low, "ndvi_day": round(float(s.values[j]), 3),
            "so_ngay_len": int((t_peak - t_low).days),
            "cach_quan_trac_that": int(near),
            "lo_hong_lon_nhat": None if not np.isfinite(gmax) else int(gmax),
            "tin_cay": "chắc" if (near <= 12 and (not np.isfinite(gmax)
                                                  or gmax <= GAP_CANH_BAO))
                       else "cần kiểm chứng"})
    return out


def main():
    s2 = pd.read_csv(f"{BASE}/data/out/lot_s2_timeseries.csv", parse_dates=["date"])
    s1 = pd.read_csv(f"{BASE}/data/out/lot_s1_timeseries.csv", parse_dates=["date"])
    cl = pd.read_csv(f"{BASE}/data/out/climate_daily.csv", parse_dates=["date"])
    sm = pd.read_csv(f"{BASE}/data/out/soil_moisture_daily.csv", parse_dates=["date"])
    lots = pd.read_csv(f"{BASE}/data/out/lots_summary.csv")

    # --- 1. lỗ hổng quan trắc ---------------------------------------------
    days = sorted(s2["date"].unique())
    gaps = pd.Series(days).diff().dt.days.dropna()
    big = [(days[i], days[i + 1], int(g)) for i, g in enumerate(gaps.values)
           if g > GAP_CANH_BAO]
    print(f"quang học: {len(days)} ngày, khoảng cách trung vị {gaps.median():.0f} ngày")
    for a, b, g in big:
        n1 = s1[(s1["date"] > a) & (s1["date"] < b)]["date"].nunique()
        print(f"  LỖ HỔNG {g} ngày: {pd.Timestamp(a):%d/%m/%Y} → "
              f"{pd.Timestamp(b):%d/%m/%Y}  (radar có {n1} ngày trong khoảng này)")

    # --- 2. chu kỳ canh tác theo lô ---------------------------------------
    rows = []
    for lid, d in s2.groupby("lo_id"):
        for k, c in enumerate(chu_ky(d), 1):
            rows.append({"lo_id": lid, "vu": k, **c})
    ck = pd.DataFrame(rows)
    ck.to_csv(f"{BASE}/data/out/lot_chu_ky.csv", index=False)
    print(f"\nchu kỳ dò được: {len(ck)} vụ trên {ck['lo_id'].nunique()} lô "
          f"({(ck['tin_cay']=='chắc').sum()} vụ chắc, "
          f"{(ck['tin_cay']!='chắc').sum()} cần kiểm chứng)")

    # --- 3. mùa mưa / mùa khô ---------------------------------------------
    # In theo THÁNG-NĂM chứ không gộp theo số tháng: kỳ dữ liệu có hai tháng 8
    # (cuối 08/2025 và đầu 08/2026), gộp lại sẽ ra một con số không tồn tại.
    mm = cl.groupby(cl["date"].dt.to_period("M"))["precipitation_sum"].sum()
    print("\nmưa theo tháng (mm):",
          " ".join(f"{str(p)[2:]}={v:.0f}" for p, v in mm.items()))
    s2["mua_mua"] = s2["date"].dt.month.isin(MUA_MUA)
    sea = s2.pivot_table(index="lo_id", columns="mua_mua", values="ndvi", aggfunc="mean")
    sea.columns = ["ndvi_mua_kho", "ndvi_mua_mua"]
    sea["chenh_mua"] = (sea["ndvi_mua_mua"] - sea["ndvi_mua_kho"]).round(3)
    sea = sea.round(3)

    # --- 4. lệch so với mặt bằng farm -------------------------------------
    farm = s2.groupby("date")["ndvi"].mean().rename("farm")
    j = s2.join(farm, on="date")
    j["lech"] = j["ndvi"] - j["farm"]
    lech = j.groupby("lo_id")["lech"].agg(["mean", "std"]).round(3)
    lech.columns = ["lech_tb", "lech_do_on_dinh"]

    # --- 5. hiện trạng cuối kỳ --------------------------------------------
    last3 = (s2.sort_values("date").groupby("lo_id").tail(3)
             .groupby("lo_id").agg(ndvi_cuoi=("ndvi", "last"),
                                   ngay_cuoi=("date", "last")))
    xu_huong = []
    for lid, d in s2.sort_values("date").groupby("lo_id"):
        t = d.tail(4)
        if len(t) >= 3:
            x = (t["date"] - t["date"].min()).dt.days.values.astype(float)
            k = np.polyfit(x, t["ndvi"].values, 1)[0] * 30      # NDVI / tháng
        else:
            k = np.nan
        xu_huong.append({"lo_id": lid, "xu_huong_thang": round(float(k), 3)})
    xu_huong = pd.DataFrame(xu_huong).set_index("lo_id")

    # --- 6. ẩm tán lá (NDMI) theo mùa -------------------------------------
    ndmi = s2.pivot_table(index="lo_id", columns="mua_mua", values="ndmi",
                          aggfunc="mean").round(3)
    ndmi.columns = ["ndmi_mua_kho", "ndmi_mua_mua"]

    out = (lots.set_index("lo_id")[["area_ha", "ndvi_tb", "bien_do", "loai"]]
           .join([sea, ndmi, lech, last3, xu_huong]))
    out["so_vu"] = ck.groupby("lo_id").size().reindex(out.index).fillna(0).astype(int)
    out["so_vu_chac"] = (ck[ck["tin_cay"] == "chắc"].groupby("lo_id").size()
                         .reindex(out.index).fillna(0).astype(int))

    def trang_thai(r):
        if r["xu_huong_thang"] >= 0.05:
            return "đang lên xanh"
        if r["xu_huong_thang"] <= -0.05:
            return "đang xuống — thu hoạch hoặc suy giảm"
        return "ổn định"
    out["trang_thai_cuoi_ky"] = out.apply(trang_thai, axis=1)
    out = out.reset_index()
    out.to_csv(f"{BASE}/data/out/lot_tinh_trang.csv", index=False)

    # --- 7. nước ------------------------------------------------------------
    cl["ym"] = cl["date"].dt.to_period("M")
    m = cl.groupby("ym").agg(mua=("precipitation_sum", "sum"),
                             et0=("et0_fao_evapotranspiration", "sum"),
                             tmax=("temperature_2m_max", "max"),
                             tmin=("temperature_2m_min", "min"),
                             ngay_mua=("precipitation_sum", lambda s: int((s >= 1).sum())))
    m["can_bang"] = (m["mua"] - m["et0"]).round(1)
    sm["ym"] = sm["date"].dt.to_period("M")
    m = m.join(sm.groupby("ym")[["sm_nong", "sm_giua", "sm_sau"]].mean().round(3))
    m.round(1).to_csv(f"{BASE}/data/out/nuoc_theo_thang.csv")

    kho = cl["precipitation_sum"] < 1
    run, best, cur = [], (0, None), 0
    for i, v in enumerate(kho.values):
        cur = cur + 1 if v else 0
        if cur > best[0]:
            best = (cur, cl["date"].iloc[i])
    print(f"\nnước: mưa {cl['precipitation_sum'].sum():,.0f} mm | "
          f"ET0 {cl['et0_fao_evapotranspiration'].sum():,.0f} mm | "
          f"cân bằng {cl['precipitation_sum'].sum()-cl['et0_fao_evapotranspiration'].sum():+,.0f} mm")
    print(f"chuỗi ngày khô dài nhất: {best[0]} ngày, kết thúc {best[1]:%d/%m/%Y}")
    thieu = m[m["can_bang"] < 0]
    print(f"số tháng thiếu nước (mưa < ET0): {len(thieu)} — "
          + ", ".join(f"{i} ({v:+.0f} mm)" for i, v in thieu["can_bang"].items()))

    print("\n" + out[["lo_id", "area_ha", "so_vu", "so_vu_chac", "ndvi_mua_kho",
                      "ndvi_mua_mua", "chenh_mua", "lech_tb", "ndvi_cuoi",
                      "xu_huong_thang", "trang_thai_cuoi_ky"]].to_string(index=False))
    print("\nđã ghi: lot_chu_ky.csv, lot_tinh_trang.csv, nuoc_theo_thang.csv")


if __name__ == "__main__":
    main()
