# -*- coding: utf-8 -*-
"""Dựng giao diện giám sát lô — một file HTML tự chứa, không gọi mạng.

    python3 scripts/dung_ban_do.py       →  web/ban-do.html

Đọc dữ liệu từ data/, ảnh nền vệ tinh từ ../gis/data/raw/.
Đây là BẢN THAM CHIẾU cho đội web — không phải sản phẩm cuối. Xem docs/03.
"""
from __future__ import annotations

import base64
import csv
import io
import json
import math
import sys
from pathlib import Path

GOC = Path(__file__).resolve().parent.parent
GIS = GOC.parent / "gis"                              # …/Sankit/gis
sys.path.insert(0, str(GOC / "scripts"))
from ke_hoach_lo import KE_HOACH  # noqa: E402

try:
    from PIL import Image
except ImportError:
    sys.exit("Cần Pillow. Dùng: ../gis/.venv/bin/python scripts/dung_ban_do.py")

# ═══ 1. Ảnh nền vệ tinh, cắt đúng vùng farm ═══════════════════════════════
B = json.loads((GIS / "data/raw/basemap_meta.json").read_text())
IW0, IH0 = B["size_px"]
bb = B["bounds_lonlat"]
merc = lambda lat: math.log(math.tan(math.pi / 4 + math.radians(lat) / 2))
mN, mS = merc(bb["north"]), merc(bb["south"])

def to_px(lon, lat):
    return ((lon - bb["west"]) / (bb["east"] - bb["west"]) * IW0,
            (mN - merc(lat)) / (mN - mS) * IH0)

geo = json.loads((GOC / "data/that/lo_ranh_gioi.geojson").read_text())
pts = [to_px(*c) for f in geo["features"] for c in f["geometry"]["coordinates"][0]]
xs, ys = [p[0] for p in pts], [p[1] for p in pts]
mx, my = (max(xs) - min(xs)) * 0.13, (max(ys) - min(ys)) * 0.13
L, R = max(0, int(min(xs) - mx)), min(IW0, int(max(xs) + mx))
T, Bt = max(0, int(min(ys) - my)), min(IH0, int(max(ys) + my))
IW, IH = R - L, Bt - T

im = Image.open(GIS / "data/raw/esri_basemap_z18.png").convert("RGB").crop((L, T, R, Bt))
buf = io.BytesIO()
im.save(buf, "JPEG", quality=86, optimize=True, subsampling=0)
ANH = base64.b64encode(buf.getvalue()).decode()
print(f"  ảnh nền {IW}×{IH} px · {IW*B['m_per_px_x']:.0f}×{Bt-T and (Bt-T)*B['m_per_px_y']:.0f} m · {len(ANH)/1024:.0f} KB base64")

POLY = {f["properties"]["lo_id"]: [[round((to_px(*c)[0] - L) / IW * 100, 4),
                                    round((to_px(*c)[1] - T) / IH * 100, 4)]
                                   for c in f["geometry"]["coordinates"][0]]
        for f in geo["features"]}

# ═══ 2. Dữ liệu ═══════════════════════════════════════════════════════════
J = lambda p: json.loads((GOC / p).read_text(encoding="utf-8"))
C = lambda p: list(csv.DictReader((GOC / p).open(encoding="utf-8")))
lo, vu = J("data/that/lo_ho_so.json"), J("data/mo_phong/vu_canh_tac.json")
lh, cb = J("data/mo_phong/lo_hang.json"), J("data/dan_xuat/canh_bao.json")
dc = J("data/dan_xuat/doi_chieu_nhat_ky_ve_tinh.json")
lt, qq = C("data/dan_xuat/lo_thang.csv"), C("data/that/quan_trac_quang.csv")
nk, kh = C("data/mo_phong/nhat_ky_dong_ruong.csv"), C("data/that/khi_hau_thang.csv")
ns = {n["ma"]: n["ten"] for n in J("data/mo_phong/nhan_su.json")}

NHOM = {"CUC": "duoc_lieu", "CCO": "duoc_lieu", "BCA": "duoc_lieu",
        "LAC": "ho_dau", "DAU": "ho_dau", "CHA": "lau_nam", "UOM": "vuon_uom"}
TEN = {"CUC": "Cúc chi", "CCO": "Cúc cổ", "BCA": "Bồ công anh", "LAC": "Lạc",
       "DAU": "Đậu che phủ", "CHA": "Chanh", "UOM": "Ươm giống"}
VIEC = {"lam_dat": ["Làm đất", "cuoc"], "bon_lot": ["Bón lót", "phan"],
        "xuong_giong": ["Xuống giống", "mam"], "bon_thuc": ["Bón thúc", "phan"],
        "lam_co": ["Làm cỏ", "cuoc"], "tuoi": ["Tưới nước", "nuoc"],
        "phong_tru_sinh_hoc": ["Phòng trừ sinh học", "la"],
        "thu_hoach": ["Thu hoạch", "keo"], "cai_tao_dat": ["Cải tạo đất", "cuoc"]}
THANGS = sorted({r["thang"] for r in lt})
F = lambda v: None if v in ("", None) else float(v)

payload = {
    "geo": {"anh_px": [IW, IH], "m_ngang": round(IW * B["m_per_px_x"]), "poly": POLY},
    "thangs": THANGS, "cay_ten": TEN,
    "khi_hau": {r["ym"]: {"mua": float(r["mua"]), "et0": float(r["et0"]),
                          "tmax": float(r["tmax"]), "tmin": float(r["tmin"]),
                          "ngay_mua": int(r["ngay_mua"]),
                          "cb": round(float(r["mua"]) - float(r["et0"]), 1)} for r in kh},
    "lo": {},
}
for l in lo:
    lid, k = l["lo_id"], KE_HOACH[l["lo_id"]]
    rows = {r["thang"]: r for r in lt if r["lo_id"] == lid}
    payload["lo"][lid] = {
        "id": lid, "ten": l["ten"], "ha": l["dien_tich_ha"], "muc_dich": l["muc_dich"],
        "mo_ta": k["mo_ta"], "can_cu": k["can_cu"], "phan_loai": l["phan_loai_tu_anh"],
        "chu_vi": l["chu_vi_m"], "cao": l["cao_do_m"], "doc": l["do_doc_deg"],
        "ndvi_tb": l["ndvi_trung_binh"], "bien_do": l["bien_do_ndvi"],
        "ndvi_min": l["ndvi_min"], "ndvi_max": l["ndvi_max"],
        "ndmi_tb": l["ndmi_trung_binh"], "ngay_quang": l["so_ngay_quang"],
        "ngay_radar": l["so_ngay_radar"], "lech": l["lech_so_voi_farm"],
        "kho": l["ndvi_mua_kho"], "mua": l["ndvi_mua_mua"],
        "chenh_dt": l["chenh_dien_tich_pct"], "dt_ve_tay": l["dien_tich_ve_tay_ha"],
        "thang": {t: {"ndvi": F(rows[t]["ndvi"]), "src": rows[t]["nguon_ndvi"],
                      "ndmi": F(rows[t]["ndmi"]), "vh": F(rows[t]["vh_db"]),
                      "cay": rows[t]["cay_trong"], "vu": rows[t]["vu_id"],
                      "pha": rows[t]["pha_sinh_truong"],
                      "nhom": NHOM.get(next((v["ma_cay_trong"] for v in vu
                                             if v["vu_id"] == rows[t]["vu_id"]), ""), None),
                      "che_phu": F(rows[t]["che_phu_uoc_pct"]), "lst": F(rows[t]["t_be_mat_uoc_c"]),
                      "thieu": F(rows[t]["thieu_nuoc_mm"]), "tuoi": F(rows[t]["nuoc_tuoi_can_m3"]),
                      "etc": F(rows[t]["etc_mm"]), "mua_hq": F(rows[t]["mua_hieu_qua_mm"]),
                      "anh": int(rows[t]["so_ngay_co_anh_quang"])} for t in THANGS},
        "chuoi": [[r["ngay"], round(float(r["ndvi"]), 4)] for r in qq
                  if r["lo_id"] == lid and r["ndvi"] and not r["dang_ngo"]],
        "vu": [{"id": v["vu_id"], "cay": v["ma_cay_trong"], "ten": TEN[v["ma_cay_trong"]],
                "nhom": NHOM[v["ma_cay_trong"]], "gieo": v["ngay_xuong_giong"],
                "het": v["ngay_ket_thuc"], "thu_tu": v["ngay_thu_tu"], "thu_den": v["ngay_thu_den"],
                "ti_le": v["ti_le_gieo"], "so_dot": v["so_dot_thu"], "tin": v["do_tin_ngay_gieo"],
                "dt": v["dien_tich_gieo_ha"], "kho_tan": v["san_luong_kho_du_kien_tan"]}
               for v in vu if v["lo_id"] == lid],
        "canh_bao": sorted([{"luat": c["ma_luat"].split("_")[0], "muc": c["muc_do"],
                             "ngay": c["ngay"], "tieu_de": c["tieu_de"], "chi_tiet": c["chi_tiet"]}
                            for c in cb if c["lo_id"] == lid],
                           key=lambda c: c["ngay"], reverse=True),
        "lo_hang": [{"id": x["id"], "cay": TEN[x["ma_cay_trong"]], "tu": x["ngay_hai_tu"],
                     "den": x["ngay_hai_den"], "tuoi": x["khoi_luong_tuoi_kg"],
                     "kho": x["khoi_luong_kho_kg"], "tt": x["trang_thai"],
                     "bich": x["phan_phoi"]["so_bich_20g"],
                     "ndvi_hai": (x["trang_thai_lo_dat_luc_hai"] or {}).get("ndvi"),
                     "gdd": x["khi_hau_ca_vu"]["gdd_co_so_10c"],
                     "mua_vu": x["khi_hau_ca_vu"]["tong_mua_mm"]}
                    for x in lh if x["lo_dat_id"] == lid],
        "nhat_ky": [{"ngay": r["ngay"], "viec": VIEC.get(r["loai_viec"], [r["loai_viec"], "la"])[0],
                     "icon": VIEC.get(r["loai_viec"], ["", "la"])[1], "mo_ta": r["mo_ta"],
                     "nguoi": ns.get(r["nguoi_thuc_hien"], r["nguoi_thuc_hien"]),
                     "bang_chung": r["bang_chung"].split("|") if r["bang_chung"] else []}
                    for r in nk if r["lo_id"] == lid][::-1][:50],
        "doi_chieu": [{"tu": d["ngay_hai_tu"], "den": d["ngay_hai_den"], "sut": d["sut_ndvi"],
                       "nguong": d["nguong_sut_ap_dung"], "kq": d["ket_qua_tong_hop"],
                       "radar": (d["kiem_bang_radar"] or {}).get("thay_doi_db"),
                       "cay": TEN.get(d["ma_cay_trong"])} for d in dc if d["lo_id"] == lid],
    }
payload["dem"] = {"canh_bao": len(cb), "lo_hang": len(lh), "vu": len(vu),
                  "quang": len([r for r in qq if r["ndvi"]]), "radar": 684, "nhat_ky": len(nk)}

DATA = json.dumps(payload, ensure_ascii=False, separators=(",", ":")).replace("</", "<\\/")
print(f"  dữ liệu {len(DATA)/1024:.0f} KB · {len(payload['lo'])} lô · {len(THANGS)} tháng")

CSS = (GOC / "scripts/_ban_do.css").read_text(encoding="utf-8")
JS = (GOC / "scripts/_ban_do.js").read_text(encoding="utf-8")
HTML = (GOC / "scripts/_ban_do.html").read_text(encoding="utf-8")
out = HTML.replace("/*CSS*/", CSS).replace("/*ANH*/", ANH).replace("/*DATA*/", DATA).replace("/*JS*/", JS)
(GOC / "web/ban-do.html").write_text(out, encoding="utf-8")
print(f"  ✓ web/ban-do.html — {len(out.encode())/1024/1024:.2f} MB")
