# -*- coding: utf-8 -*-
"""Sinh bộ dữ liệu bàn giao: THẬT (từ GIS) + MÔ PHỎNG (neo vào THẬT) + DẪN XUẤT.

    python3 scripts/sinh_du_lieu.py

Chạy lại luôn ra kết quả y hệt — mọi chỗ ngẫu nhiên đều dùng hạt cố định.
Chỉ ĐỌC từ ../gis/ và ../qr/ — không ghi vào hai mảng đó.
"""
from __future__ import annotations

import csv
import json
import math
import random
import shutil
import sys
from datetime import date, datetime, timedelta
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))
from ke_hoach_lo import (  # noqa: E402
    CAY_TRONG, DOT_HAN_2026_04, KE_HOACH, KY_DU_LIEU, NGAY_DANG_NGO,
)

GOC = Path(__file__).resolve().parent.parent          # …/Sankit/farm-lo
GIS = GOC.parent / "gis" / "data" / "out"             # …/Sankit/gis
QR = GOC.parent / "qr"                                # …/Sankit/qr
RNG = random.Random(20260812)

NGAY_CHOT = date(2026, 8, 12)          # cuối kỳ dữ liệu GIS
NDVI_DAT_TRONG, NDVI_TAN_KIN = 0.15, 0.90   # từ lots_summary: min 0,147 · max 0,905
HE_SO_NHIET_TAN = 9.0                  # °C chênh giữa đất trống và tán kín, giữa trưa

# ------------------------------------------------------------------ tiện ích
def doc_csv(p: Path) -> list[dict]:
    with p.open(encoding="utf-8") as f:
        return list(csv.DictReader(f))

def so(x, mac_dinh=None):
    try:
        return float(x)
    except (TypeError, ValueError):
        return mac_dinh

def ngay(s: str) -> date:
    return datetime.strptime(s, "%Y-%m-%d").date()

def thang(d: date) -> str:
    return f"{d.year:04d}-{d.month:02d}"

def ghi_json(duong_dan: Path, obj) -> None:
    duong_dan.parent.mkdir(parents=True, exist_ok=True)
    duong_dan.write_text(json.dumps(obj, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(f"  ✓ {duong_dan.relative_to(GOC)}")

def ghi_csv(duong_dan: Path, hang: list[dict], cot: list[str]) -> None:
    duong_dan.parent.mkdir(parents=True, exist_ok=True)
    with duong_dan.open("w", encoding="utf-8", newline="") as f:
        w = csv.DictWriter(f, fieldnames=cot)
        w.writeheader()
        w.writerows(hang)
    print(f"  ✓ {duong_dan.relative_to(GOC)}  ({len(hang)} hàng)")

# ---------------------------------------------------- ký tự kiểm tra ISO 7064
BANG_CHU = "0123456789ABCDEFGHIJKLMNOPQRSTUVWXYZ"

def ky_tu_kiem_tra(than: str) -> str:
    """ISO 7064 MOD 37,36 — cùng thuật toán với Sankit/qr/tools/ma_dinh_danh.py."""
    p = 36
    for c in than.replace("-", ""):
        s = (p % 37) + BANG_CHU.index(c)
        s = s % 36 or 36
        p = (2 * s) % 37
    return BANG_CHU[(37 - p) % 36]

def gan_kiem_tra(ma: str) -> str:
    return f"{ma}-{ky_tu_kiem_tra(ma)}"

def ma_lo_hang(giong: str, nam2: int, stt: int) -> str:
    return gan_kiem_tra(f"SK-L-{giong}{nam2:02d}-{stt:02d}")

def ma_bich(giong: str, nam2: int, stt: int) -> str:
    return gan_kiem_tra(f"SK-B-{giong}{nam2:02d}-{stt:04d}")

def ma_cay(giong: str, nam2: int, khu: str, stt: int) -> str:
    return gan_kiem_tra(f"SK-C-{giong}{nam2:02d}-{khu}-{stt:04d}")

# ================================================================== 1. ĐỌC THẬT
print("1. Đọc dữ liệu thật từ ../gis/data/out/")
tom_tat = {r["lo_id"]: r for r in doc_csv(GIS / "lots_summary.csv")}
tinh_trang = {r["lo_id"]: r for r in doc_csv(GIS / "lot_tinh_trang.csv")}
dien_tich = {r["lo_id"]: r for r in doc_csv(GIS / "lots_area.csv")}
chu_ky = doc_csv(GIS / "lot_chu_ky.csv")
s2 = doc_csv(GIS / "lot_s2_timeseries.csv")
s1 = doc_csv(GIS / "lot_s1_timeseries.csv")
khi_hau_ngay = doc_csv(GIS / "climate_daily.csv")
nuoc_thang = {r["ym"]: r for r in doc_csv(GIS / "nuoc_theo_thang.csv")}
tho_nhuong = doc_csv(GIS / "soil_soilgrids.csv")
ranh_gioi = json.loads((GIS / "lots.geojson").read_text(encoding="utf-8"))
LO_IDS = [f"L{i:02d}" for i in range(1, 13)]
print(f"   {len(LO_IDS)} lô · {len(s2)} bản ghi quang · {len(s1)} bản ghi radar · {len(khi_hau_ngay)} ngày khí hậu")

trong_tam = {}
for f in ranh_gioi["features"]:
    vong = f["geometry"]["coordinates"][0]
    trong_tam[f["properties"]["lo_id"]] = (
        round(sum(c[1] for c in vong) / len(vong), 6),
        round(sum(c[0] for c in vong) / len(vong), 6),
    )

# ============================================================ 2. THẬT → data/that
print("\n2. Xuất lớp THẬT")
THAT = GOC / "data" / "that"
shutil.copyfile(GIS / "lots.geojson", THAT / "lo_ranh_gioi.geojson")
print(f"  ✓ {(THAT / 'lo_ranh_gioi.geojson').relative_to(GOC)}")

ho_so_lo = []
for lid in LO_IDS:
    t, tt, dt, kh = tom_tat[lid], tinh_trang[lid], dien_tich[lid], KE_HOACH[lid]
    lat, lon = trong_tam[lid]
    ho_so_lo.append({
        "lo_id": lid,
        "ten": kh["ten"],
        "muc_dich": kh["muc_dich"],
        "dien_tich_ha": so(t["area_ha"]),
        "dien_tich_ve_tay_ha": so(t["area_ve_tay_ha"]),
        "chenh_dien_tich_pct": so(t["chenh_pct"]),
        "chu_vi_m": so(dt["perimeter_m"]),
        "trong_tam": {"lat": lat, "lon": lon},
        "cao_do_m": so(t["cao_do_m"]),
        "do_doc_deg": so(t["do_doc_deg"]),
        "ndvi_trung_binh": so(t["ndvi_tb"]),
        "ndvi_min": so(t["ndvi_min"]),
        "ndvi_max": so(t["ndvi_max"]),
        "bien_do_ndvi": so(t["bien_do"]),
        "ndmi_trung_binh": so(t["ndmi_tb"]),
        "vh_db_trung_binh": so(t["vh_db_tb"]),
        "so_ngay_quang": int(so(t["so_ngay_s2"], 0)),
        "so_ngay_radar": int(so(t["so_ngay_s1"], 0)),
        "phan_loai_tu_anh": t["loai"],
        "ndvi_mua_kho": so(tt["ndvi_mua_kho"]),
        "ndvi_mua_mua": so(tt["ndvi_mua_mua"]),
        "lech_so_voi_farm": so(tt["lech_tb"]),
        "xu_huong_thang_cuoi_ky": so(tt["xu_huong_thang"]),
        "trang_thai_cuoi_ky": tt["trang_thai_cuoi_ky"],
        "so_vu_do_duoc": int(so(tt["so_vu"], 0)),
        "so_vu_chac": int(so(tt["so_vu_chac"], 0)),
        "nguon": "that",
    })
ghi_json(THAT / "lo_ho_so.json", ho_so_lo)

quang = []
for r in s2:
    quang.append({
        "ngay": r["date"], "lo_id": r["lo_id"],
        "ndvi": so(r["ndvi"]), "ndmi": so(r["ndmi"]),
        "quang_pct": so(r["quang_pct"]),
        "dang_ngo": NGAY_DANG_NGO.get(r["date"], {}).get("ly_do", ""),
        "nguon": "that",
    })
quang.sort(key=lambda x: (x["ngay"], x["lo_id"]))
ghi_csv(THAT / "quan_trac_quang.csv", quang, ["ngay", "lo_id", "ndvi", "ndmi", "quang_pct", "dang_ngo", "nguon"])

radar = [{"ngay": r["date"], "lo_id": r["lo_id"], "huong_bay": r["orbit"],
          "vv_db": so(r["vv_db"]), "vh_db": so(r["vh_db"]), "rvi": so(r["rvi"]), "nguon": "that"} for r in s1]
radar.sort(key=lambda x: (x["ngay"], x["lo_id"], x["huong_bay"]))
ghi_csv(THAT / "quan_trac_radar.csv", radar, ["ngay", "lo_id", "huong_bay", "vv_db", "vh_db", "rvi", "nguon"])

shutil.copyfile(GIS / "climate_daily.csv", THAT / "khi_hau_ngay.csv")
print(f"  ✓ {(THAT / 'khi_hau_ngay.csv').relative_to(GOC)}")
shutil.copyfile(GIS / "nuoc_theo_thang.csv", THAT / "khi_hau_thang.csv")
print(f"  ✓ {(THAT / 'khi_hau_thang.csv').relative_to(GOC)}")
shutil.copyfile(GIS / "lot_chu_ky.csv", THAT / "chu_ky_ndvi.csv")
print(f"  ✓ {(THAT / 'chu_ky_ndvi.csv').relative_to(GOC)}")

dat = {}
for r in tho_nhuong:
    dat.setdefault(r["property"], {})[r["depth"]] = so(r["value"])
ghi_json(THAT / "tho_nhuong.json", {
    "nguon": "SoilGrids v2.0 (ISRIC)", "do_phan_giai_m": 250,
    "canh_bao": "Cả 12 lô nằm trong CÙNG MỘT ô 250 m — nguồn này không phân biệt được lô với lô.",
    "chi_tieu": dat, "nguon_du_lieu": "that",
})

# ================================== 3. TỔNG HỢP THÁNG × LÔ (thật, có gắn cờ nghi)
print("\n3. Tổng hợp quan trắc theo tháng × lô")
DS_THANG = []
d = date(2025, 8, 1)
while d <= date(2026, 8, 1):
    DS_THANG.append(thang(d))
    d = date(d.year + (d.month == 12), (d.month % 12) + 1, 1)

ndvi_thang, ndmi_thang, ngay_quang_thang, vh_thang = {}, {}, {}, {}
for r in s2:
    if r["date"] in NGAY_DANG_NGO:
        continue
    k = (r["lo_id"], thang(ngay(r["date"])))
    if so(r["ndvi"]) is not None:
        ndvi_thang.setdefault(k, []).append(so(r["ndvi"]))
        ndmi_thang.setdefault(k, []).append(so(r["ndmi"]))
        ngay_quang_thang.setdefault(k, set()).add(r["date"])
for r in s1:
    k = (r["lo_id"], thang(ngay(r["date"])))
    vh_thang.setdefault(k, []).append(10 ** (so(r["vh_db"]) / 10.0))   # trung bình trên thang tuyến tính

def tb(xs):
    return round(sum(xs) / len(xs), 4) if xs else None

def ndvi_noi_suy(lid: str, ym: str) -> tuple[float | None, str]:
    """NDVI tháng; nếu tháng đó không có ảnh quang thì nội suy tuyến tính hai tháng kề."""
    v = tb(ndvi_thang.get((lid, ym), []))
    if v is not None:
        return v, "quan_trac"
    i = DS_THANG.index(ym)
    truoc = next((tb(ndvi_thang.get((lid, DS_THANG[j]), [])) for j in range(i - 1, -1, -1)
                  if ndvi_thang.get((lid, DS_THANG[j]))), None)
    sau = next((tb(ndvi_thang.get((lid, DS_THANG[j]), [])) for j in range(i + 1, len(DS_THANG))
                if ndvi_thang.get((lid, DS_THANG[j]))), None)
    if truoc is not None and sau is not None:
        return round((truoc + sau) / 2, 4), "noi_suy"
    v = truoc if truoc is not None else sau
    return (round(v, 4), "noi_suy") if v is not None else (None, "khong_co")

# ======================================================== 4. MÔ PHỎNG: mùa vụ
print("\n4. Sinh mùa vụ (mô phỏng, neo vào chu kỳ NDVI thật)")

def pha_sinh_truong(v: dict, m_dau: date, m_cuoi: date) -> str | None:
    """Pha của vụ trong tháng [m_dau, m_cuoi]: ini | dev | mid | end | None."""
    g, t1, t2 = ngay(v["gieo"]), ngay(v["thu_tu"]), ngay(v["thu_den"])
    if m_cuoi < g or m_dau > t2:
        return None
    if m_dau <= t2 and m_cuoi >= t1:
        return "end"
    tong = max((t1 - g).days, 1)
    q = ((m_dau + (m_cuoi - m_dau) / 2) - g).days / tong
    if q < 0.22:
        return "ini"
    if q < 0.55:
        return "dev"
    return "mid"

# Một VỤ = một chu kỳ trồng (gieo → kết thúc). Một vụ có thể có NHIỀU ĐỢT THU:
# cúc chi hái nhiều lượt vì hoa nở dần, bồ công anh cắt nhiều lứa trên cùng gốc,
# chanh lưu niên thu quả năm này qua năm khác. Gộp hai khái niệm này làm một là
# chỗ mô hình gãy — trình kiểm tra bắt được bằng bất biến I4.
def ma_vu(lid: str, v: dict) -> str:
    return f"{lid}-{v['gieo'][:4]}-{v['cay']}"

vu_ban_ghi, dot_ban_ghi = [], []
for lid in LO_IDS:
    kh = KE_HOACH[lid]
    dt_lo = so(tom_tat[lid]["area_ha"])
    nhom = {}
    for v in kh["vu"]:
        nhom.setdefault(ma_vu(lid, v), []).append(v)
    for vu_id, ds in nhom.items():
        v0 = ds[0]
        c = CAY_TRONG[v0["cay"]]
        ti_le = v0.get("ti_le_gieo", kh["ti_le_gieo"])
        dt_gieo = round(dt_lo * ti_le, 4)
        het = max(ngay(x["thu_den"]) for x in ds)
        # Cây lưu niên KHÔNG mặc nhiên chiếm lô mãi mãi: nếu lô đã được gieo thứ khác
        # sau đợt thu cuối thì vụ đó đã kết thúc. Bỏ điều kiện này là hai vụ chồng nhau
        # trên cùng một lô — bất biến I4 bắt được.
        gieo_sau = [x for x in kh["vu"] if ngay(x["gieo"]) > het]
        dang_chay = het >= NGAY_CHOT or (c["luu_nien"] and not gieo_sau)
        vu_ban_ghi.append({
            "vu_id": vu_id, "lo_id": lid,
            "ma_cay_trong": v0["cay"], "ten_cay_trong": c["ten"], "ten_khoa_hoc": c["ten_khoa_hoc"],
            "nhom_cay": c["nhom"], "luu_nien": c["luu_nien"],
            "ngay_xuong_giong": v0["gieo"],
            "do_tin_ngay_gieo": ("tu_ho_so_that" if vu_id in ("L01-2025-CUC", "L02-2025-CUC", "L03-2026-CUC")
                                 else "khong_kiem_duoc" if ngay(v0["gieo"]) < ngay(KY_DU_LIEU["tu"])
                                 else "suy_tu_ndvi"),
            "ngay_ket_thuc": None if dang_chay else het.isoformat(),
            "ngay_thu_tu": min(x["thu_tu"] for x in ds),
            "ngay_thu_den": max(x["thu_den"] for x in ds),
            "so_dot_thu": len(ds),
            "trang_thai": ("dang_sinh_truong" if ngay(min(x["thu_tu"] for x in ds)) > NGAY_CHOT
                           else "dang_thu_hoach" if dang_chay else "da_thu_hoach"),
            "dien_tich_gieo_ha": dt_gieo,
            "ti_le_gieo": ti_le,
            "phu_kin_lo": ti_le >= 0.60,
            "san_luong_tuoi_du_kien_tan": round(dt_gieo * c["nang_suat_tuoi_tan_ha"] * len(ds), 3),
            "san_luong_kho_du_kien_tan": round(dt_gieo * c["nang_suat_tuoi_tan_ha"] * len(ds) * c["ti_le_thu_hoi"], 3),
            "kc_fao56": c["kc"],
            "neo_ndvi": v0["neo"],
            "ghi_chu": v0["ghi_chu"],
            "nguon": "mau",
        })
        for x in ds:
            t2 = ngay(x["thu_den"])
            dot_ban_ghi.append({
                "dot_id": x["ma"], "vu_id": vu_id, "lo_id": lid,
                "ma_cay_trong": x["cay"],
                "ngay_thu_tu": x["thu_tu"], "ngay_thu_den": x["thu_den"],
                "trang_thai": ("da_thu_hoach" if t2 < NGAY_CHOT
                               else "dang_thu_hoach" if ngay(x["thu_tu"]) <= NGAY_CHOT
                               else "chua_toi"),
                "dien_tich_gieo_ha": dt_gieo,
                "san_luong_tuoi_du_kien_tan": round(dt_gieo * c["nang_suat_tuoi_tan_ha"], 3),
                "san_luong_kho_du_kien_tan": round(dt_gieo * c["nang_suat_tuoi_tan_ha"] * c["ti_le_thu_hoi"], 3),
                "neo_ndvi": x["neo"],
                "ghi_chu": x["ghi_chu"],
                "nguon": "mau",
            })
ghi_json(GOC / "data" / "mo_phong" / "dot_thu_hoach.json", dot_ban_ghi)
ghi_json(GOC / "data" / "mo_phong" / "vu_canh_tac.json", vu_ban_ghi)
print(f"   {len(vu_ban_ghi)} vụ · {len(dot_ban_ghi)} đợt thu trên {len([l for l in LO_IDS if KE_HOACH[l]['vu']])} lô")

# hồ sơ cây trồng (Kc, năng suất tham chiếu) — rule-engine cần bảng này
ghi_json(GOC / "data" / "mo_phong" / "cay_trong.json", [
    {"ma": k, **v, "nguon": "mau",
     "ghi_chu_kc": "Kc theo FAO-56 Irrigation and Drainage Paper 56, bảng 12."}
    for k, v in CAY_TRONG.items()
])

# =============================================== 5. DẪN XUẤT: bảng lô × tháng
print("\n5. Dựng bảng dẫn xuất lô × tháng")
lo_thang = []
for lid in LO_IDS:
    kh = KE_HOACH[lid]
    for ym in DS_THANG:
        y, mo = int(ym[:4]), int(ym[5:])
        m_dau = date(y, mo, 1)
        m_cuoi = date(y + (mo == 12), (mo % 12) + 1, 1) - timedelta(days=1)
        kh_th = nuoc_thang.get(ym, {})

        ndvi, nguon_ndvi = ndvi_noi_suy(lid, ym)
        ndmi = tb(ndmi_thang.get((lid, ym), []))
        vh = vh_thang.get((lid, ym), [])
        vh_db = round(10 * math.log10(sum(vh) / len(vh)), 2) if vh else None

        vu_dang, pha = None, None
        for v in kh["vu"]:
            p = pha_sinh_truong(v, m_dau, m_cuoi)
            if p:
                vu_dang, pha = v, p
                break

        c = CAY_TRONG[vu_dang["cay"]] if vu_dang else None
        kc = c["kc"]["mid" if pha in ("mid", "dev") else pha] if c and pha else (0.0 if kh["muc_dich"] == "cong_trinh" else 0.30)

        mua = so(kh_th.get("mua"), 0.0)
        et0 = so(kh_th.get("et0"), 0.0)
        tmax = so(kh_th.get("tmax"))
        tmin = so(kh_th.get("tmin"))
        mua_hq = round(mua * (125 - 0.2 * mua) / 125, 1) if mua < 250 else round(125 + 0.1 * mua, 1)
        etc = round(kc * et0, 1)
        thieu = round(max(0.0, etc - mua_hq), 1)

        if ndvi is not None and tmax is not None:
            fvc = min(1.0, max(0.0, (ndvi - NDVI_DAT_TRONG) / (NDVI_TAN_KIN - NDVI_DAT_TRONG))) ** 2
            lst = round(tmax + HE_SO_NHIET_TAN * (1 - fvc), 1)
        else:
            fvc = lst = None

        lo_thang.append({
            "lo_id": lid, "thang": ym,
            "muc_dich": kh["muc_dich"],
            "vu_id": ma_vu(lid, vu_dang) if vu_dang else "",
            "dot_thu_id": vu_dang["ma"] if vu_dang and pha == "end" else "",
            "cay_trong": c["ten"] if c else ("Công trình" if kh["muc_dich"] == "cong_trinh" else "Đất trống / nghỉ"),
            "pha_sinh_truong": pha or "",
            "ndvi": ndvi, "nguon_ndvi": nguon_ndvi,
            "ndmi": ndmi,
            "so_ngay_co_anh_quang": len(ngay_quang_thang.get((lid, ym), set())),
            "vh_db": vh_db,
            "che_phu_uoc_pct": round(fvc * 100, 1) if fvc is not None else None,
            "t_khong_khi_max_c": tmax, "t_khong_khi_min_c": tmin,
            "t_be_mat_uoc_c": lst,
            "mua_mm": mua, "mua_hieu_qua_mm": mua_hq,
            "et0_mm": et0, "kc": round(kc, 2), "etc_mm": etc,
            "thieu_nuoc_mm": thieu,
            "nuoc_tuoi_can_m3": round(thieu * 10 * so(tom_tat[lid]["area_ha"]) * kh["ti_le_gieo"], 1),
            "nguon_khi_hau": "that", "nguon_cay_trong": "mau",
        })
COT_LT = list(lo_thang[0].keys())
ghi_csv(GOC / "data" / "dan_xuat" / "lo_thang.csv", lo_thang, COT_LT)

# ================================================ 6. MÔ PHỎNG: nhân sự + nhật ký
print("\n6. Sinh nhật ký đồng ruộng (mô phỏng)")
NHAN_SU = [
    {"ma": "NS-01", "ten": "Trần Văn Đức", "vai_tro": "To truong dong ruong", "vai_tro_vi": "Tổ trưởng đồng ruộng"},
    {"ma": "NS-02", "ten": "Phạm Thị Lan", "vai_tro": "Ky thuat vien", "vai_tro_vi": "Kỹ thuật viên canh tác"},
    {"ma": "NS-03", "ten": "Nguyễn Văn Hoà", "vai_tro": "Van hanh say", "vai_tro_vi": "Vận hành máy sấy"},
    {"ma": "NS-04", "ten": "Lê Thị Nhung", "vai_tro": "Thu hai", "vai_tro_vi": "Tổ thu hái"},
    {"ma": "NS-05", "ten": "Đinh Văn Sơn", "vai_tro": "Thu hai", "vai_tro_vi": "Tổ thu hái"},
    {"ma": "NS-06", "ten": "Bùi Thị Hạnh", "vai_tro": "QA ho so", "vai_tro_vi": "QA · hồ sơ lô"},
]
for n in NHAN_SU:
    n["nhan_vat_hu_cau"] = True
    n["nguon"] = "mau"
ghi_json(GOC / "data" / "mo_phong" / "nhan_su.json", NHAN_SU)

VAT_TU = {
    "bon_lot": ("Phân chuồng hoai + trấu hun", "tấn", 8.0),
    "bon_thuc": ("Phân hữu cơ vi sinh", "kg", 320.0),
    "phong_tru_sinh_hoc": ("Chế phẩm nấm đối kháng Trichoderma", "kg", 12.0),
    "voi": ("Vôi bột nông nghiệp", "kg", 500.0),
}
nhat_ky, stt_nk, vu_da_gieo = [], 0, set()

def them_nk(lid, vu_id, d: date, loai, mo_ta, nguoi, vat_tu=None, luong=None, dv=None, bc=None, ghi_chu=None):
    """Bỏ qua mọi mốc SAU ngày chốt — việc chưa làm thì không có bản ghi nhật ký."""
    global stt_nk
    if d > NGAY_CHOT:
        return
    stt_nk += 1
    nhat_ky.append({
        "nk_id": f"NK-{stt_nk:04d}", "lo_id": lid, "vu_id": vu_id or "",
        "ngay": d.isoformat(), "loai_viec": loai, "mo_ta": mo_ta,
        "nguoi_thuc_hien": nguoi, "vat_tu": vat_tu or "", "luong": luong if luong is not None else "",
        "don_vi": dv or "", "bang_chung": "|".join(bc or []),
        "ghi_chu": ghi_chu or "", "nguon": "mau",
    })

for lid in LO_IDS:
    kh = KE_HOACH[lid]
    for m in kh.get("moc_dac_biet", []):
        them_nk(lid, "", ngay(m["ngay"]), "cai_tao_dat", m["viec"], "NS-01", bc=["ẢNH", "GPS"], ghi_chu=m["can_cu"])
    for v in kh["vu"]:
        dt_gieo_lo = so(tom_tat[lid]["area_ha"]) * v.get("ti_le_gieo", kh["ti_le_gieo"])
        c, g = CAY_TRONG[v["cay"]], ngay(v["gieo"])
        t1, t2 = ngay(v["thu_tu"]), ngay(v["thu_den"])
        vid = ma_vu(lid, v)
        lan_dau = vid not in vu_da_gieo
        vu_da_gieo.add(vid)
        if g >= ngay(KY_DU_LIEU["tu"]) and lan_dau:
            them_nk(lid, vid, g - timedelta(days=12), "lam_dat",
                    "Cày ải, lên luống, rải vôi điều chỉnh pH", "NS-01",
                    *VAT_TU["voi"][:1], round(VAT_TU["voi"][2] * dt_gieo_lo), VAT_TU["voi"][1],
                    ["ẢNH", "GPS"], "pH đất SoilGrids 5,9 — dưới ngưỡng tối ưu 6,0–6,5")
            them_nk(lid, vid, g - timedelta(days=7), "bon_lot",
                    "Bón lót phân chuồng hoai mục", "NS-02",
                    VAT_TU["bon_lot"][0], round(VAT_TU["bon_lot"][2] * dt_gieo_lo, 1), VAT_TU["bon_lot"][1],
                    ["CÂN", "ẢNH", "DUYỆT"])
            them_nk(lid, vid, g, "xuong_giong",
                    f"Xuống giống {c['ten']} — {round(dt_gieo_lo, 3)} ha", "NS-01",
                    bc=["GPS", "ẢNH", "DUYỆT"], ghi_chu=v["ghi_chu"])
            for k, ngay_them in enumerate((30, 60, 90)):
                d = g + timedelta(days=ngay_them)
                if d < t1:
                    them_nk(lid, vid, d, "bon_thuc", f"Bón thúc đợt {k + 1}", "NS-02",
                            VAT_TU["bon_thuc"][0], round(VAT_TU["bon_thuc"][2] * dt_gieo_lo), VAT_TU["bon_thuc"][1],
                            ["CÂN", "ẢNH"])
            for ngay_them in (25, 55):
                d = g + timedelta(days=ngay_them)
                if d < t1:
                    them_nk(lid, vid, d, "lam_co", "Làm cỏ thủ công, không dùng thuốc diệt cỏ", "NS-04",
                            bc=["ẢNH"], ghi_chu="Canh tác hữu cơ TCVN 11041 — không hoạt chất tổng hợp")
        # tưới: theo VỤ (không theo đợt thu), chỉ vào tháng mà số liệu THẬT cho thấy thiếu nước
        t2_vu = max(ngay(x["thu_den"]) for x in kh["vu"] if ma_vu(lid, x) == vid)
        for r in lo_thang if lan_dau else []:
            if r["lo_id"] != lid or r["vu_id"] != vid or r["thieu_nuoc_mm"] <= 5:
                continue
            y, mo = int(r["thang"][:4]), int(r["thang"][5:])
            for tuan, ngay_trong_thang in enumerate((8, 18, 27)):
                if r["thieu_nuoc_mm"] < 15 * (tuan + 1):
                    break
                d = date(y, mo, ngay_trong_thang)
                if g <= d <= t2_vu:
                    them_nk(lid, vid, d, "tuoi",
                            f"Tưới bù — thiếu {r['thieu_nuoc_mm']} mm trong tháng", "NS-01",
                            "Nước giếng khoan", round(r["nuoc_tuoi_can_m3"] / 3, 1), "m³",
                            ["ĐỒNG HỒ NƯỚC"],
                            f"ET0 {r['et0_mm']} mm × Kc {r['kc']} = {r['etc_mm']} mm; mưa hiệu quả {r['mua_hieu_qua_mm']} mm (khí hậu THẬT)")
        if c["nang_suat_tuoi_tan_ha"] > 0 and t1 <= NGAY_CHOT:
            them_nk(lid, vid, t1 - timedelta(days=3), "phong_tru_sinh_hoc",
                    "Phun chế phẩm sinh học phòng nấm trước thu hái", "NS-02",
                    *VAT_TU["phong_tru_sinh_hoc"][:1], round(VAT_TU["phong_tru_sinh_hoc"][2] * dt_gieo_lo, 1),
                    VAT_TU["phong_tru_sinh_hoc"][1], ["ẢNH", "DUYỆT"],
                    "Không có thời gian cách ly bắt buộc — chế phẩm sinh học")
        d = t1
        while d <= min(t2, NGAY_CHOT):
            them_nk(lid, vid, d, "thu_hoach",
                    f"Thu hái {c['ten']} — hái tay lúc sáng sớm", RNG.choice(["NS-04", "NS-05"]),
                    bc=["CÂN", "GPS", "ẢNH", "QUÉT MÃ CÂY"])
            d += timedelta(days=1)

# --- hai bản ghi LỆCH CỐ Ý, để giao diện cảnh báo có nội dung mà dựng
LECH_CO_Y = [
    {"nk_id": None, "ly_do": "R5 — thu hoạch khai trên lô KHÔNG canh tác (L06 là khu công trình)"},
    {"nk_id": None, "ly_do": "R5 — thu hoạch khai ngày 10/02/2026 trên L09 nhưng NDVI không hề tụt"},
]
them_nk("L06", "", date(2026, 5, 14), "thu_hoach",
        "Thu hái bồ công anh (bản ghi SAI — cắm để kiểm thử cảnh báo)", "NS-05",
        bc=["CÂN"], ghi_chu="LỆCH CỐ Ý: L06 là khu công trình, không có vụ nào.")
LECH_CO_Y[0]["nk_id"] = nhat_ky[-1]["nk_id"]
them_nk("L09", "L09-2026-DAU", date(2026, 2, 10), "thu_hoach",
        "Thu hái đậu che phủ (bản ghi SAI — cắm để kiểm thử cảnh báo)", "NS-05",
        bc=["CÂN"], ghi_chu="LỆCH CỐ Ý: NDVI L09 tháng 2–3/2026 không tụt, và vụ đậu mãi 20/05/2026 mới gieo.")
LECH_CO_Y[1]["nk_id"] = nhat_ky[-1]["nk_id"]

nhat_ky.sort(key=lambda r: (r["ngay"], r["lo_id"], r["nk_id"]))
ghi_csv(GOC / "data" / "mo_phong" / "nhat_ky_dong_ruong.csv", nhat_ky, list(nhat_ky[0].keys()))
ghi_json(GOC / "data" / "mo_phong" / "lech_co_y.json", {
    "vi_sao": "Lịch canh tác mô phỏng được SUY TỪ đường NDVI, nên phép đối chiếu nhật ký ↔ vệ tinh "
              "tất nhiên khớp — không có gì để hiển thị. Hai bản ghi dưới đây được cắm SAI có chủ ý "
              "để đội web dựng được màn hình cảnh báo. Xoá chúng đi là bảng cảnh báo còn 0 hàng loại R5.",
    "ban_ghi": LECH_CO_Y,
})

# ==================================================== 7. MÔ PHỎNG: cây có tem
print("\n7. Sinh cá thể cây có tem")
CAY_THAT = [
    {"id": "SK-C-CUC25-L01-0007-P", "lo_id": "L01", "so": 7, "nam": 25, "giong": "CUC"},
    {"id": "SK-C-CUC25-L01-0008-N", "lo_id": "L01", "so": 8, "nam": 25, "giong": "CUC"},
    {"id": "SK-C-CUC25-L02-0003-3", "lo_id": "L02", "so": 3, "nam": 25, "giong": "CUC"},
    {"id": "SK-C-CUC26-L03-0011-B", "lo_id": "L03", "so": 11, "nam": 26, "giong": "CUC"},
]
# lô -> (số tem, chỉ số vụ mà tem gắn vào)
SO_TEM = {"L01": (14, 0), "L02": (10, 0), "L03": (12, 2), "L04": (8, 0), "L05": (8, 0),
          "L07": (12, 0), "L10": (8, 0), "L11": (8, 0), "L12": (12, 0)}
cay_ban_ghi, cay_theo_lo = [], {}
for lid, (n, i_vu) in SO_TEM.items():
    vu_dau = KE_HOACH[lid]["vu"][i_vu]
    giong = "CHA" if vu_dau["cay"] == "CHA" else "CUC"
    nam2 = int(vu_dau["gieo"][2:4]) if vu_dau["cay"] != "CHA" else 25
    if ngay(vu_dau["gieo"]) < ngay(KY_DU_LIEU["tu"]):
        nam2 = 25
    if lid == "L03":
        nam2 = 26
    ds = []
    for i in range(1, n + 1):
        mid = ma_cay(giong, nam2, lid, i)
        that = next((c for c in CAY_THAT if c["lo_id"] == lid and c["so"] == i), None)
        ds.append(that["id"] if that else mid)
        cay_ban_ghi.append({
            "id": that["id"] if that else mid,
            "giong": giong, "ten_thuong": CAY_TRONG[vu_dau["cay"]]["ten"],
            "lo_id": lid, "so_trong_lo": i,
            "toa_do_uoc": {"lat": trong_tam[lid][0], "lon": trong_tam[lid][1]},
            "do_chinh_xac_toa_do": "trong_tam_lo (±%.0f m)" % (math.sqrt(so(tom_tat[lid]["area_ha"]) * 10000) / 2),
            "vu_id": ma_vu(lid, vu_dau),
            "ngay_xuong_giong": vu_dau["gieo"],
            "co_ho_so_that_trong_Sankit": bool(that),
            "nguon": "that" if that else "mau",
        })
    cay_theo_lo[lid] = ds
ghi_json(GOC / "data" / "mo_phong" / "cay_ca_the.json", cay_ban_ghi)
print(f"   {len(cay_ban_ghi)} cây ({sum(1 for c in cay_ban_ghi if c['nguon'] == 'that')} đã có hồ sơ thật trong Sankit/qr)")

# ============================================ 8. MÔ PHỎNG: lô hàng (tem B2B)
print("\n8. Sinh lô hàng")
CUA_SO_GOM = {"CUC": 2, "CCO": 4, "BCA": 5, "LAC": 3, "CHA": 10}
CHE_BIEN = {
    "CUC": ("Sấy lạnh, không phơi nắng", "20 – 35 °C", 42),
    "CCO": ("Sấy lạnh, không phơi nắng", "20 – 35 °C", 46),
    "BCA": ("Sấy lạnh hai giai đoạn", "35 – 45 °C", 30),
    "LAC": ("Phơi nắng + sấy hoàn thiện", "40 – 50 °C", 18),
    "CHA": (None, None, None),
}
kh_ngay_map = {r["date"]: r for r in khi_hau_ngay}

def khi_hau_trong_vu(g: date, t2: date) -> dict:
    mua = et0 = gdd = 0.0
    ngay_mua = 0
    tmaxs, tmins = [], []
    d = g
    while d <= min(t2, NGAY_CHOT):
        r = kh_ngay_map.get(d.isoformat())
        if r:
            p = so(r["precipitation_sum"], 0.0)
            mua += p
            ngay_mua += p >= 1.0
            et0 += so(r["et0_fao_evapotranspiration"], 0.0)
            gdd += max(0.0, so(r["temperature_2m_mean"], 0.0) - 10.0)
            tmaxs.append(so(r["temperature_2m_max"]))
            tmins.append(so(r["temperature_2m_min"]))
        d += timedelta(days=1)
    return {
        "tong_mua_mm": round(mua, 1), "so_ngay_mua": ngay_mua,
        "tong_et0_mm": round(et0, 1), "can_bang_nuoc_mm": round(mua - et0, 1),
        "gdd_co_so_10c": round(gdd), "t_max_cao_nhat_c": max(tmaxs) if tmaxs else None,
        "t_min_thap_nhat_c": min(tmins) if tmins else None,
        "so_ngay_theo_doi": len(tmaxs), "nguon": "that",
    }

s2_theo_lo = {}
for r in s2:
    if so(r["ndvi"]) is not None and r["date"] not in NGAY_DANG_NGO:
        s2_theo_lo.setdefault(r["lo_id"], []).append((ngay(r["date"]), so(r["ndvi"]), so(r["ndmi"])))
for v in s2_theo_lo.values():
    v.sort()

def ndvi_gan_nhat(lid: str, d: date):
    ds = s2_theo_lo.get(lid, [])
    if not ds:
        return None
    q, ndvi, ndmi = min(ds, key=lambda x: abs((x[0] - d).days))
    return {"ngay_anh": q.isoformat(), "lech_ngay": (q - d).days, "ndvi": ndvi, "ndmi": ndmi, "nguon": "that"}

def trang_thai_lo(t2: date) -> str:
    n = (NGAY_CHOT - t2).days
    for nguong, tt in ((120, "da_giao"), (60, "da_niem_ho_so"), (30, "cho_kiem_nghiem"),
                       (14, "dang_dong_goi"), (7, "dang_phan_loai"), (2, "dang_say")):
        if n > nguong:
            return tt
    return "dang_thu_hoach"

lo_hang, dem = [], {}
for v in dot_ban_ghi:
    c = CAY_TRONG[v["ma_cay_trong"]]
    if c["nang_suat_tuoi_tan_ha"] <= 0:
        continue
    t1, t2 = ngay(v["ngay_thu_tu"]), min(ngay(v["ngay_thu_den"]), NGAY_CHOT)
    if t1 > NGAY_CHOT:
        continue
    cua_so = CUA_SO_GOM[v["ma_cay_trong"]]
    tong_ngay = (t2 - t1).days + 1
    n_lo = max(1, math.ceil(tong_ngay / cua_so))
    tuoi_tong = v["san_luong_tuoi_du_kien_tan"] * 1000 * min(1.0, tong_ngay / max(1, (ngay(v["ngay_thu_den"]) - t1).days + 1))
    giong_ma = "CUC" if v["ma_cay_trong"] in ("CUC", "CCO") else v["ma_cay_trong"]
    for i in range(n_lo):
        h1 = t1 + timedelta(days=i * cua_so)
        h2 = min(h1 + timedelta(days=cua_so - 1), t2)
        nam2 = h2.year % 100
        khoa = (giong_ma, nam2)
        dem[khoa] = dem.get(khoa, 9) + 1          # 01–09 để dành cho mã Sankit đã có
        tuoi = round(tuoi_tong / n_lo * RNG.uniform(0.88, 1.12), 1)
        cn, dai, gio = CHE_BIEN[v["ma_cay_trong"]]
        thu_hoi = c["ti_le_thu_hoi"] * RNG.uniform(0.95, 1.05)
        kho = round(tuoi * thu_hoi, 1)
        b2c_kg = round(kho * 0.30, 1) if v["ma_cay_trong"] in ("CUC", "CCO") else 0.0
        lo_hang.append({
            "id": ma_lo_hang(giong_ma, nam2, dem[khoa]),
            "ten": f"Lô {CAY_TRONG[v['ma_cay_trong']]['ten']} · {KE_HOACH[v['lo_id']]['ten']} · {h1.strftime('%d/%m/%Y')}",
            "lo_dat_id": v["lo_id"], "vu_id": v["vu_id"], "dot_thu_id": v["dot_id"],
            "ma_cay_trong": v["ma_cay_trong"], "ten_cay_trong": CAY_TRONG[v["ma_cay_trong"]]["ten"],
            "ngay_hai_tu": h1.isoformat(), "ngay_hai_den": h2.isoformat(),
            "khoi_luong_tuoi_kg": tuoi,
            "che_bien": {"cong_nghe": cn, "dai_nhiet": dai, "thoi_gian_gio": gio,
                         "nhat_ky_nhiet_so_hoa": False, "nguon": "mau"},
            "khoi_luong_kho_kg": kho if cn else None,
            "ti_le_thu_hoi": round(thu_hoi, 3) if cn else None,
            "phan_phoi": {"b2b_si_kg": round(kho - b2c_kg, 1) if cn else tuoi,
                          "b2c_le_kg": b2c_kg,
                          "so_bich_20g": int(b2c_kg * 1000 // 20) if b2c_kg else 0},
            "trang_thai": trang_thai_lo(h2),
            "kiem_nghiem": None,
            "ly_do_kiem_nghiem_rong": "Chưa có phiếu kiểm nghiệm thật. Không dựng phiếu giả — "
                                      "xem Sankit/qr/docs/02_MO_HINH_DU_LIEU.md, trường `nguon`.",
            "nguon_cay": cay_theo_lo.get(v["lo_id"], [])[:6],
            "trang_thai_lo_dat_luc_hai": ndvi_gan_nhat(v["lo_id"], h2),
            "khi_hau_ca_vu": khi_hau_trong_vu(ngay(next(x["ngay_xuong_giong"] for x in vu_ban_ghi if x["vu_id"] == v["vu_id"])), h2),
            "nguon": "mau",
        })
print(f"   {len(lo_hang)} lô hàng")
ghi_json(GOC / "data" / "mo_phong" / "lo_hang.json", lo_hang)

# ================================================= 9. MÔ PHỎNG: bịch (tem B2C)
print("\n9. Sinh bịch thành phẩm (chỉ 3 lô gần nhất — phần còn lại chỉ giữ số đếm)")
GIOI_HAN_BICH = 40
bich, dem_bich = [], {}
ung_vien = sorted([l for l in lo_hang if l["phan_phoi"]["so_bich_20g"] > 0],
                  key=lambda l: l["ngay_hai_den"], reverse=True)[:3]
for l in ung_vien:
    d_dong = ngay(l["ngay_hai_den"]) + timedelta(days=21)
    nam2 = d_dong.year % 100
    for _ in range(min(GIOI_HAN_BICH, l["phan_phoi"]["so_bich_20g"])):
        dem_bich[nam2] = dem_bich.get(nam2, 999) + 1     # 0001–0999 để dành cho mã đã có
        bich.append({
            "id": ma_bich("CUC", nam2, dem_bich[nam2]),
            "lo_hang_id": l["id"], "lo_dat_id": l["lo_dat_id"], "vu_id": l["vu_id"],
            "quy_cach": {"khoi_luong": "20 g", "dang": "trà nguyên bông"},
            "ngay_dong_goi": d_dong.isoformat(),
            "han_su_dung": date(d_dong.year + 2, d_dong.month, d_dong.day).isoformat(),
            "nguon_cay": l["nguon_cay"],
            "nguon": "mau",
        })
ghi_json(GOC / "data" / "mo_phong" / "bich.json", bich)
print(f"   {len(bich)} bịch có hồ sơ đầy đủ / {sum(l['phan_phoi']['so_bich_20g'] for l in lo_hang)} bịch theo số đếm")

# ============================ 10. DẪN XUẤT: đối chiếu nhật ký ↔ ảnh vệ tinh
print("\n10. Đối chiếu nhật ký ↔ ảnh vệ tinh")
dot_map = {d["dot_id"]: d for d in dot_ban_ghi}
thu_hoach_theo_lo = {}
for r in nhat_ky:
    if r["loai_viec"] == "thu_hoach":
        khoa = next((d["dot_id"] for d in dot_ban_ghi
                     if d["lo_id"] == r["lo_id"] and d["ngay_thu_tu"] <= r["ngay"] <= d["ngay_thu_den"]), "")
        thu_hoach_theo_lo.setdefault((r["lo_id"], khoa), []).append(ngay(r["ngay"]))

# Ngưỡng theo cây: thu hoạch lấy đi bao nhiêu tán thì NDVI mới phải tụt bấy nhiêu.
# Hái quả trên cây lưu niên KHÔNG đụng tới tán — luật không áp dụng, để tránh báo động giả.
NGUONG_SUT = {"LAC": -0.25, "CUC": -0.20, "CCO": -0.08, "BCA": -0.08, "UOM": -0.05,
              "DAU": -0.15, "CHA": None}
CUA_SO_DOI_CHIEU = 45   # ngày, mỗi phía

doi_chieu = []
for (lid, vid), ds in sorted(thu_hoach_theo_lo.items()):
    t1, t2 = min(ds), max(ds)
    obs = s2_theo_lo.get(lid, [])
    ma_cay = dot_map[vid]["ma_cay_trong"] if vid in dot_map else None
    nguong = NGUONG_SUT.get(ma_cay, -0.15)
    # đỉnh trước thu hoạch và đáy sau thu hoạch — đọc đúng cách người ta đọc đường cong
    truoc = [o for o in obs if t1 - timedelta(days=CUA_SO_DOI_CHIEU) <= o[0] <= t1]
    sau = [o for o in obs if t2 <= o[0] <= t2 + timedelta(days=CUA_SO_DOI_CHIEU)]
    o_t = max(truoc, key=lambda o: o[1]) if truoc else None
    o_s = min(sau, key=lambda o: o[1]) if sau else None
    if nguong is None:
        kq, delta = "khong_ap_dung", (round(o_s[1] - o_t[1], 4) if o_t and o_s else None)
    elif not truoc or not sau:
        kq, delta = "khong_du_du_lieu", None
    else:
        delta = round(o_s[1] - o_t[1], 4)
        kq = "khop" if delta <= nguong else "khong_thay_doi_tren_anh"
    # radar bù: VH tụt khi sinh khối bị lấy đi. Sentinel-1 có 57/57 lượt dùng được,
    # nên khi ảnh quang thủng thì đây là nguồn duy nhất còn nói được gì.
    def vh_tb(t_tu: date, t_den: date):
        xs = [10 ** (so(r["vh_db"]) / 10.0) for r in s1
              if r["lo_id"] == lid and t_tu <= ngay(r["date"]) <= t_den]
        return round(10 * math.log10(sum(xs) / len(xs)), 2) if xs else None
    vh_t = vh_tb(t1 - timedelta(days=30), t1)
    vh_s = vh_tb(t2, t2 + timedelta(days=30))
    if vh_t is not None and vh_s is not None:
        d_vh = round(vh_s - vh_t, 2)
        radar_kq = {"vh_truoc_db": vh_t, "vh_sau_db": vh_s, "thay_doi_db": d_vh,
                 "ket_qua": "khop" if d_vh <= -0.5 else "khong_thay_doi",
                    "ghi_chu": "Ngưỡng −0,5 dB. Radar nhiễu đốm nhiều, chỉ đọc được xu hướng."}
    else:
        radar_kq = None

    doi_chieu.append({
        "lo_id": lid, "dot_thu_id": vid or None,
        "vu_id": dot_map[vid]["vu_id"] if vid in dot_map else None, "ma_cay_trong": ma_cay,
        "so_ngay_hai_khai_bao": len(ds),
        "ngay_hai_tu": t1.isoformat(), "ngay_hai_den": t2.isoformat(),
        "nguong_sut_ap_dung": nguong,
        "anh_dinh_truoc": {"ngay": o_t[0].isoformat(), "ndvi": o_t[1]} if o_t else None,
        "anh_day_sau": {"ngay": o_s[0].isoformat(), "ndvi": o_s[1]} if o_s else None,
        "sut_ndvi": delta,
        "ket_qua": kq,
        "kiem_bang_radar": radar_kq,
        "ket_qua_tong_hop": (
            "xac_nhan" if kq == "khop" else
            "khong_ap_dung" if kq == "khong_ap_dung" else
            "xac_nhan_bang_radar" if radar_kq and radar_kq["ket_qua"] == "khop" else
            "can_nguoi_xac_minh" if kq == "khong_thay_doi_tren_anh" else
            "chua_ket_luan_duoc"),
        "dien_giai": {
            "khop": "NDVI tụt đúng mức mà một lần thu hoạch loại này phải tạo ra.",
            "khong_thay_doi_tren_anh": "Nhật ký khai thu hoạch nhưng tán không giảm đủ — cần người xác minh.",
            "khong_du_du_lieu": f"Thiếu ảnh quang ở ít nhất một phía trong cửa sổ ±{CUA_SO_DOI_CHIEU} ngày.",
            "khong_ap_dung": "Hái quả trên cây lưu niên không lấy đi tán — ảnh vệ tinh không kiểm được việc này. "
                             "Phải dựa vào cân tại vườn và ảnh chụp có GPS.",
        }[kq],
    })
ghi_json(GOC / "data" / "dan_xuat" / "doi_chieu_nhat_ky_ve_tinh.json", doi_chieu)
print("   " + " · ".join(f"{k}: {sum(1 for d in doi_chieu if d['ket_qua'] == k)}"
                        for k in ("khop", "khong_thay_doi_tren_anh", "khong_du_du_lieu", "khong_ap_dung")))
print("   tổng hợp cả radar → " + " · ".join(
    f"{k}: {sum(1 for d in doi_chieu if d['ket_qua_tong_hop'] == k)}"
    for k in ("xac_nhan", "xac_nhan_bang_radar", "can_nguoi_xac_minh", "chua_ket_luan_duoc", "khong_ap_dung")))

# ================================================== 11. DẪN XUẤT: cảnh báo
print("\n11. Chạy luật cảnh báo trên số liệu thật")
canh_bao, stt_cb = [], 0

def them_cb(ma_luat, muc, lid, ngay_cb, tieu_de, chi_tiet, bang_chung):
    global stt_cb
    stt_cb += 1
    canh_bao.append({
        "cb_id": f"CB-{stt_cb:04d}", "ma_luat": ma_luat, "muc_do": muc,
        "lo_id": lid, "pham_vi": "farm" if lid is None else "lo",
        "ngay": ngay_cb, "tieu_de": tieu_de,
        "chi_tiet": chi_tiet, "bang_chung": bang_chung,
        "nguon_du_lieu": "that",
    })

# R1 — thiếu nước, tính trên CỬA SỔ TRƯỢT 15 NGÀY của khí hậu NGÀY.
# Gộp theo tháng thì một đợt hạn 18 ngày vắt qua hai tháng bị chia đôi và biến mất;
# đúng chuyện đã xảy ra ngày 30/03–16/04/2026. Mưa dưới 5 mm/ngày coi như bốc hơi hết.
CUA_SO_HAN, NGUONG_HAN = 15, 25.0
kc_theo_thang = {(r["lo_id"], r["thang"]): (r["kc"], r["cay_trong"], r["muc_dich"]) for r in lo_thang}
ds_ngay = sorted(kh_ngay_map)
for lid in LO_IDS:
    if KE_HOACH[lid]["muc_dich"] == "cong_trinh":
        continue
    dot, dang_mo = [], None
    for i in range(len(ds_ngay) - CUA_SO_HAN + 1):
        cua_so = ds_ngay[i:i + CUA_SO_HAN]
        etc = p_eff = 0.0
        for d in cua_so:
            kc, _, _ = kc_theo_thang.get((lid, d[:7]), (0.30, "", ""))
            etc += kc * so(kh_ngay_map[d]["et0_fao_evapotranspiration"], 0.0)
            mua_d = so(kh_ngay_map[d]["precipitation_sum"], 0.0)
            p_eff += mua_d if mua_d >= 5.0 else 0.0
        thieu = etc - p_eff
        if thieu >= NGUONG_HAN:
            if dang_mo is None:
                dang_mo = {"tu": cua_so[0], "den": cua_so[-1], "thieu_max": thieu, "etc": etc, "p": p_eff}
            else:
                dang_mo["den"] = cua_so[-1]
                if thieu > dang_mo["thieu_max"]:
                    dang_mo.update(thieu_max=thieu, etc=etc, p=p_eff)
        elif dang_mo:
            dot.append(dang_mo); dang_mo = None
    if dang_mo:
        dot.append(dang_mo)
    for e in dot:
        kc, cay, _ = kc_theo_thang.get((lid, e["tu"][:7]), (0.30, "—", ""))
        dt_tuoi = so(tom_tat[lid]["area_ha"]) * KE_HOACH[lid]["ti_le_gieo"]
        them_cb("R1_THIEU_NUOC", "cao" if e["thieu_max"] >= 45 else "trung_binh",
                lid, e["den"],
                f"Hụt nước {e['thieu_max']:.0f} mm trong 15 ngày ({e['tu']} → {e['den']})",
                f"ETc dồn {e['etc']:.0f} mm (Kc {kc} cho {cay}) so với mưa hiệu quả {e['p']:.0f} mm. "
                f"Cần bù khoảng {e['thieu_max'] * 10 * dt_tuoi:.0f} m³ cho {dt_tuoi:.2f} ha đang gieo.",
                {"nguon": "Open-Meteo ERA5 (THẬT) + Kc FAO-56", "tu": e["tu"], "den": e["den"],
                 "cua_so_ngay": CUA_SO_HAN, "nguong_mm": NGUONG_HAN})

# R6 — chuỗi ngày không mưa, mức farm
chuoi, bd = 0, None
for d in ds_ngay:
    if so(kh_ngay_map[d]["precipitation_sum"], 0.0) < 1.0:
        bd = bd or d
        chuoi += 1
    else:
        if chuoi >= 14:
            them_cb("R6_CHUOI_NGAY_KHONG_MUA", "cao" if chuoi >= 18 else "trung_binh", None, d,
                    f"{chuoi} ngày liên tiếp mưa dưới 1 mm ({bd} → {d})",
                    "Cả vùng, không riêng lô nào. Đây là nền của mọi cảnh báo thiếu nước cùng kỳ.",
                    {"tu": bd, "so_ngay": chuoi})
        chuoi, bd = 0, None

# R2 — NDVI sụt bất thường, không có thu hoạch kèm theo
ngay_thu_moi_lo = {}
for r in nhat_ky:
    if r["loai_viec"] in ("thu_hoach", "cai_tao_dat"):
        ngay_thu_moi_lo.setdefault(r["lo_id"], []).append(ngay(r["ngay"]))
for lid, obs in s2_theo_lo.items():
    for (d0, v0, _), (d1, v1, _) in zip(obs, obs[1:]):
        if v1 - v0 > -0.20 or (d1 - d0).days > 45:
            continue
        if any(d0 - timedelta(days=10) <= t <= d1 + timedelta(days=10) for t in ngay_thu_moi_lo.get(lid, [])):
            continue
        trung_han = ngay(DOT_HAN_2026_04["tu"]) - timedelta(days=10) <= d1 <= ngay(DOT_HAN_2026_04["den"]) + timedelta(days=10)
        them_cb("R2_SUT_NDVI_KHONG_RO_LY_DO", "cao" if v1 - v0 <= -0.35 and not trung_han else "trung_binh",
                lid, d1.isoformat(),
                f"NDVI tụt {v0:.3f} → {v1:.3f} ({v1 - v0:+.3f}) mà nhật ký không ghi việc gì",
                f"Giữa {d0} và {d1} ({(d1 - d0).days} ngày). Không có bản ghi thu hoạch hay cải tạo đất "
                f"nào trong cửa sổ ±10 ngày."
                + (f" TRÙNG đợt hạn {DOT_HAN_2026_04['tu']}–{DOT_HAN_2026_04['den']} — nhiều khả năng "
                   f"là stress nước chứ không phải việc của người." if trung_han else ""),
                {"anh_truoc": str(d0), "anh_sau": str(d1), "ndvi_truoc": v0, "ndvi_sau": v1,
                 "trung_dot_han": trung_han})

# R3 — mất dấu quang học. Lỗ hổng mây gần như luôn phủ cả farm, nên gộp về mức farm
# khi từ 8/12 lô trở lên cùng dính; chỉ báo riêng lô nào thủng lệch với mặt bằng.
lo_hong = {}
for lid, obs in s2_theo_lo.items():
    for (d0, _, _), (d1, _, _) in zip(obs, obs[1:]):
        if (d1 - d0).days >= 30:
            lo_hong.setdefault((d0, d1), []).append(lid)
so_luot_radar_khoang = {}
for (d0, d1) in lo_hong:
    so_luot_radar_khoang[(d0, d1)] = len({r["date"] for r in s1 if d0 < ngay(r["date"]) < d1})
for (d0, d1), ds_lo in sorted(lo_hong.items()):
    n_radar = so_luot_radar_khoang[(d0, d1)]
    du = n_radar >= 4
    if len(ds_lo) >= 8:
        them_cb("R3_MAT_DAU_QUANG_HOC", "thap" if du else "trung_binh", None, d1.isoformat(),
                f"Cả farm mất ảnh quang học {(d1 - d0).days} ngày ({len(ds_lo)}/12 lô)",
                f"Từ {d0} tới {d1}. Trong khoảng đó có {n_radar} ngày radar Sentinel-1 — "
                f"{'đủ để bám xu hướng' if du else 'chưa đủ để kết luận'}. "
                f"Lỗ hổng mây phủ cả vùng, không phải vấn đề của một lô.",
                {"tu": str(d0), "den": str(d1), "so_ngay_radar": n_radar, "cac_lo": ds_lo})
    else:
        for lid in ds_lo:
            them_cb("R3_MAT_DAU_QUANG_HOC", "trung_binh", lid, d1.isoformat(),
                    f"Riêng lô này mất ảnh quang học {(d1 - d0).days} ngày",
                    f"Từ {d0} tới {d1}, trong khi {12 - len(ds_lo)} lô khác vẫn có ảnh. "
                    f"Có {n_radar} ngày radar bù trong khoảng đó.",
                    {"tu": str(d0), "den": str(d1), "so_ngay_radar": n_radar})

# R4 — lô kém mặt bằng farm kéo dài
trung_vi_ngay = {}
for r in s2:
    if so(r["ndvi"]) is not None and r["date"] not in NGAY_DANG_NGO:
        trung_vi_ngay.setdefault(r["date"], []).append(so(r["ndvi"]))
trung_vi_ngay = {k: sorted(v)[len(v) // 2] for k, v in trung_vi_ngay.items()}
for lid, obs in s2_theo_lo.items():
    chuoi = []
    for d, v, _ in obs:
        if v - trung_vi_ngay.get(d.isoformat(), v) <= -0.15:
            chuoi.append((d, v))
        else:
            chuoi = []
        if len(chuoi) == 3:
            them_cb("R4_KEM_MAT_BANG_FARM", "trung_binh", lid, chuoi[-1][0].isoformat(),
                    f"3 lần quan trắc liên tiếp thấp hơn mặt bằng farm ≥ 0,15",
                    f"Từ {chuoi[0][0]} tới {chuoi[-1][0]}. "
                    f"Lệch trung bình cả kỳ của lô này: {tinh_trang[lid]['lech_tb']}.",
                    {"cac_ngay": [str(d) for d, _ in chuoi]})
            chuoi = []

# R5 — nhật ký khai thu hoạch mà ảnh không thấy
for d in doi_chieu:
    if d["ket_qua_tong_hop"] == "xac_nhan_bang_radar":
        them_cb("R5_NHAT_KY_KHONG_KHOP_ANH", "thap", d["lo_id"], d["ngay_hai_den"],
                "Ảnh quang không thấy đợt thu hoạch, nhưng radar thấy",
                f"NDVI thay đổi {d['sut_ndvi'] if d['sut_ndvi'] is not None else 'n/a'} — không đạt ngưỡng. "
                f"Nhưng VH radar đổi {d['kiem_bang_radar']['thay_doi_db']} dB, đủ ngưỡng −0,5. "
                f"Cách giải thích khớp nhất: cây chỉ chiếm một phần lô, nên trung bình NDVI cả lô không nhúc nhích.",
                {"dot_thu_id": d["dot_thu_id"], "vu_id": d["vu_id"], "sut_ndvi": d["sut_ndvi"],
                 "vh_thay_doi_db": d["kiem_bang_radar"]["thay_doi_db"]})
    if d["ket_qua_tong_hop"] == "can_nguoi_xac_minh":
        them_cb("R5_NHAT_KY_KHONG_KHOP_ANH", "cao", d["lo_id"], d["ngay_hai_den"],
                "Khai thu hoạch nhưng ảnh vệ tinh không thấy tán giảm",
                f"{d['so_ngay_hai_khai_bao']} ngày thu hoạch khai từ {d['ngay_hai_tu']} tới {d['ngay_hai_den']}. "
                f"NDVI đỉnh {d['anh_dinh_truoc']['ndvi']} ({d['anh_dinh_truoc']['ngay']}) → đáy "
                f"{d['anh_day_sau']['ndvi']} ({d['anh_day_sau']['ngay']}), thay đổi {d['sut_ndvi']:+.3f} "
                f"— không đạt ngưỡng {d['nguong_sut_ap_dung']:+.2f} của {d['ma_cay_trong']}. "
                f"Radar cũng không thấy đổi ({d['kiem_bang_radar']['thay_doi_db'] if d['kiem_bang_radar'] else 'n/a'} dB).",
                {"vu_id": d["vu_id"], "sut_ndvi": d["sut_ndvi"]})
    if d["ket_qua_tong_hop"] == "chua_ket_luan_duoc":
        them_cb("R5_NHAT_KY_KHONG_KHOP_ANH", "thap", d["lo_id"], d["ngay_hai_den"],
                "Không đủ dữ liệu để kiểm chứng đợt thu hoạch",
                "Thiếu ảnh quang ở ít nhất một phía của mốc thu hoạch, và radar cũng không đổi đủ để kết luận.",
                {"dot_thu_id": d["dot_thu_id"], "vu_id": d["vu_id"]})

canh_bao.sort(key=lambda c: (c["ngay"], c["lo_id"] or "", c["ma_luat"]))
for i, c in enumerate(canh_bao, 1):
    c["cb_id"] = f"CB-{i:04d}"
ghi_json(GOC / "data" / "dan_xuat" / "canh_bao.json", canh_bao)
theo_luat = {}
for c in canh_bao:
    theo_luat[c["ma_luat"]] = theo_luat.get(c["ma_luat"], 0) + 1
print("   " + " · ".join(f"{k}: {v}" for k, v in sorted(theo_luat.items())))

# ============================================== 12. TỔNG HỢP + BẢNG THẬT/MẪU
print("\n12. Tổng hợp")
tong_ket = {
    "sinh_luc": None,   # điền ngoài script để chạy lại vẫn ra file y hệt
    "ky_du_lieu": KY_DU_LIEU,
    "ngay_chot": NGAY_CHOT.isoformat(),
    "vung": {
        "ten": "RiTi Organic Farm — Trường Yên, Hoa Lư, Ninh Bình",
        "toa_do_tham_chieu": {"lat": 20.2579952, "lon": 105.854332},
        "so_lo": 12,
        "tong_dien_tich_ha": round(sum(so(tom_tat[l]["area_ha"]) for l in LO_IDS), 4),
        "sai_so_ranh_gioi_m": 2.9,
        "he_toa_do": "EPSG:4326 lưu trữ · EPSG:32648 tính diện tích",
    },
    "dem": {
        "lo_dat": len(LO_IDS),
        "vu_canh_tac": len(vu_ban_ghi),
        "dot_thu_hoach": len(dot_ban_ghi),
        "quan_trac_quang": len(quang),
        "quan_trac_radar": len(radar),
        "ngay_khi_hau": len(khi_hau_ngay),
        "dong_lo_thang": len(lo_thang),
        "nhat_ky": len(nhat_ky),
        "lo_hang": len(lo_hang),
        "bich_co_ho_so": len(bich),
        "bich_theo_so_dem": sum(l["phan_phoi"]["so_bich_20g"] for l in lo_hang),
        "cay_co_tem": len(cay_ban_ghi),
        "canh_bao": len(canh_bao),
    },
    "san_luong_mo_phong": {
        "hoa_cuc_kho_kg": round(sum(l["khoi_luong_kho_kg"] or 0 for l in lo_hang
                                    if l["ma_cay_trong"] in ("CUC", "CCO")), 1),
        "bo_cong_anh_kho_kg": round(sum(l["khoi_luong_kho_kg"] or 0 for l in lo_hang
                                        if l["ma_cay_trong"] == "BCA"), 1),
        "lac_kho_kg": round(sum(l["khoi_luong_kho_kg"] or 0 for l in lo_hang
                                if l["ma_cay_trong"] == "LAC"), 1),
        "chanh_tuoi_kg": round(sum(l["khoi_luong_tuoi_kg"] for l in lo_hang
                                   if l["ma_cay_trong"] == "CHA"), 1),
    },
    "kiem_chung_cheo": {
        "phat_hien": "Ngày thu hái ghi trong hồ sơ cây THẬT của Sankit (SK-C-CUC25-L01-0007-P, "
                     "khu L01, thu hái 18/11/2025) rơi đúng vào đoạn NDVI của lô L01 tụt "
                     "0,738 (04/10/2025) → 0,307 (23/11/2025).",
        "nghia_la": "Lô L01 trong GIS và khu L01 trong hồ sơ cây là CÙNG MỘT mảnh đất, và mốc "
                    "thời gian hai bên khớp nhau. Đây là cơ sở để ghép hai hệ thống bằng khoá lo_id.",
        "khong_nghia_la": "KHÔNG phải bằng chứng nhân quả. Ba cây có tem chỉ cho 1,24 kg hoa tươi — "
                          "không đủ làm đổi NDVI của cả lô 1,7496 ha. Cái tụt đó là thu hoạch quy mô lô.",
        "nguon": "that",
    },
    "dot_han_kiem_chung": DOT_HAN_2026_04,
    "ngay_dang_ngo": NGAY_DANG_NGO,
    "phan_dinh_nguon": [
        {"lop": "Ranh giới lô, diện tích, địa hình", "nguon": "that", "goc": "PDF chủ farm + Copernicus DEM + Esri World Imagery"},
        {"lop": "NDVI / NDMI / radar theo lô theo ngày", "nguon": "that", "goc": "Sentinel-2 L2A + Sentinel-1 RTC"},
        {"lop": "Khí hậu ngày và tháng", "nguon": "that", "goc": "Open-Meteo (ERA5)"},
        {"lop": "Thổ nhưỡng", "nguon": "that", "goc": "SoilGrids v2.0 — 250 m, KHÔNG phân biệt được lô"},
        {"lop": "Chu kỳ NDVI dò tự động", "nguon": "that", "goc": "analyze_condition.py trên chuỗi 12 tháng"},
        {"lop": "Cây trồng của từng lô, ngày gieo, ngày thu", "nguon": "mau", "goc": "suy từ dạng chuỗi NDVI — xem scripts/ke_hoach_lo.py"},
        {"lop": "Nhật ký đồng ruộng, nhân sự, vật tư", "nguon": "mau", "goc": "dựng theo lịch nông vụ + tháng thiếu nước THẬT"},
        {"lop": "Lô hàng, bịch, sản lượng", "nguon": "mau", "goc": "năng suất tham chiếu × diện tích gieo THẬT"},
        {"lop": "Nhiệt độ bề mặt theo lô", "nguon": "dan_xuat", "goc": "t_max THẬT + hệ số che phủ từ NDVI THẬT; công thức trong docs/05"},
        {"lop": "Nhu cầu nước theo lô", "nguon": "dan_xuat", "goc": "ET0 THẬT × Kc FAO-56 − mưa hiệu quả THẬT"},
        {"lop": "Cảnh báo", "nguon": "dan_xuat", "goc": "luật R1–R5 chạy trên quan trắc THẬT"},
        {"lop": "Phiếu kiểm nghiệm", "nguon": "khong_co", "goc": "CỐ Ý để trống — không dựng phiếu giả"},
    ],
}
ghi_json(GOC / "data" / "tong_ket.json", tong_ket)

print(f"""
    Lô đất        {len(LO_IDS):>5}         Quan trắc quang {len(quang):>5}
    Vụ canh tác   {len(vu_ban_ghi):>5}         Quan trắc radar {len(radar):>5}
    Lô × tháng    {len(lo_thang):>5}         Nhật ký         {len(nhat_ky):>5}
    Lô hàng       {len(lo_hang):>5}         Cây có tem      {len(cay_ban_ghi):>5}
    Cảnh báo      {len(canh_bao):>5}         Bịch có hồ sơ   {len(bich):>5}
""")
print("Xong.")
