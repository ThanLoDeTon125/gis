# -*- coding: utf-8 -*-
"""Kiểm tra bộ dữ liệu: JSON Schema + 10 bất biến + ký tự kiểm tra mã Sankit.

    python3 scripts/kiem_tra.py

Thoát mã 1 nếu có lỗi — cắm thẳng vào CI được.
Cần: jsonschema (dùng ../gis/.venv/bin/python nếu chưa cài toàn cục).
"""
from __future__ import annotations

import csv
import json
import sys
from collections import defaultdict
from pathlib import Path

GOC = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(GOC.parent / "qr" / "tools"))   # …/Sankit/qr

loi: list[str] = []


def bao(dieu_kien: bool, thong_diep: str) -> None:
    if not dieu_kien:
        loi.append(thong_diep)


def doc(p: str):
    return json.loads((GOC / p).read_text(encoding="utf-8"))


def doc_csv(p: str):
    with (GOC / p).open(encoding="utf-8") as f:
        return list(csv.DictReader(f))


lo_dat = doc("data/that/lo_ho_so.json")
vu = doc("data/mo_phong/vu_canh_tac.json")
dot = doc("data/mo_phong/dot_thu_hoach.json")
lo_hang = doc("data/mo_phong/lo_hang.json")
bich = doc("data/mo_phong/bich.json")
cay = doc("data/mo_phong/cay_ca_the.json")
canh_bao = doc("data/dan_xuat/canh_bao.json")
lo_thang = doc_csv("data/dan_xuat/lo_thang.csv")
nhat_ky = doc_csv("data/mo_phong/nhat_ky_dong_ruong.csv")

LO_IDS = {l["lo_id"] for l in lo_dat}
cay_theo_lo = defaultdict(set)
for c in cay:
    cay_theo_lo[c["lo_id"]].add(c["id"])
vu_map = {v["vu_id"]: v for v in vu}

print("Kiểm tra bộ dữ liệu sankit-farm-lo\n")

# ── JSON Schema ────────────────────────────────────────────────────────────
try:
    import warnings

    warnings.filterwarnings("ignore")
    from jsonschema import Draft202012Validator

    S = doc("schema/sankit-farm-lo.schema.json")
    Draft202012Validator.check_schema(S)
    for ten, ds in (("lo_dat", lo_dat), ("vu", vu), ("lo_hang", lo_hang),
                    ("canh_bao", canh_bao), ("cay_ca_the", cay), ("bich", bich), ("dot_thu", dot)):
        v = Draft202012Validator({"$ref": f"#/$defs/{ten}", **S})
        n = sum(len(list(v.iter_errors(x))) for x in ds)
        bao(n == 0, f"schema {ten}: {n} lỗi")
        print(f"  {'✓' if not n else '✗'} schema {ten:<12} {len(ds):>4} bản ghi")
except ImportError:
    print("  ~ bỏ qua JSON Schema (thiếu jsonschema)")

# ── ký tự kiểm tra ISO 7064, dùng chính trình của Sankit ───────────────────
try:
    import ma_dinh_danh as md

    xau = [x["id"] for x in lo_hang + bich + cay if not md.hop_le(x["id"])]
    bao(not xau, f"mã sai ký tự kiểm tra: {xau[:5]}")
    print(f"  {'✓' if not xau else '✗'} mã ISO 7064      {len(lo_hang) + len(bich) + len(cay):>4} mã")
except ImportError:
    print("  ~ bỏ qua ký tự kiểm tra (không thấy Sankit/qr/tools)")

# ── bất biến ───────────────────────────────────────────────────────────────
print()
n = sum(1 for l in lo_hang if not set(l["nguon_cay"]) <= cay_theo_lo[l["lo_dat_id"]])
bao(n == 0, f"I1: {n} lô hàng nhận cây từ lô đất khác")

n = sum(1 for b in bich
        if b["lo_hang_id"] not in {l["id"] for l in lo_hang}
        or not set(b["nguon_cay"]) <= set(next(l for l in lo_hang if l["id"] == b["lo_hang_id"])["nguon_cay"]))
bao(n == 0, f"I2: {n} bịch có nguồn cây không nằm trong lô hàng của nó")

n = sum(1 for v in vu if not v["ngay_xuong_giong"] < v["ngay_thu_tu"] <= v["ngay_thu_den"])
bao(n == 0, f"I3: {n} vụ có thứ tự ngày sai")

XA = "9999-12-31"
cham = defaultdict(list)
for v in vu:
    cham[v["lo_id"]].append(v)
n = 0
for lid, ds in cham.items():
    for i, a in enumerate(ds):
        for b in ds[i + 1:]:
            ha, hb = a["ngay_ket_thuc"] or XA, b["ngay_ket_thuc"] or XA
            giao = a["ngay_xuong_giong"] < hb and b["ngay_xuong_giong"] < ha
            if giao and a["ti_le_gieo"] + b["ti_le_gieo"] > 1.001:
                n += 1
                loi.append(f"     {lid}: {a['vu_id']} ({a['ti_le_gieo']}) ∩ {b['vu_id']} ({b['ti_le_gieo']})")
bao(n == 0, f"I4: {n} cặp vụ chồng thời gian mà tổng tỉ lệ gieo > 1")

# I3b — mọi đợt thu phải nằm trong vụ của nó
vmap = {v["vu_id"]: v for v in vu}
n = sum(1 for d in dot
        if d["vu_id"] not in vmap
        or d["ngay_thu_tu"] < vmap[d["vu_id"]]["ngay_xuong_giong"]
        or not d["ngay_thu_tu"] <= d["ngay_thu_den"])
bao(n == 0, f"I3b: {n} đợt thu nằm ngoài vụ của nó")

# I4b — hai đợt thu của CÙNG một vụ không được chồng nhau
theo_vu = defaultdict(list)
for d in dot:
    theo_vu[d["vu_id"]].append(d)
n = 0
for ds in theo_vu.values():
    ds = sorted(ds, key=lambda x: x["ngay_thu_tu"])
    n += sum(1 for a, b in zip(ds, ds[1:]) if b["ngay_thu_tu"] <= a["ngay_thu_den"])
bao(n == 0, f"I4b: {n} cặp đợt thu cùng vụ chồng thời gian")

n = sum(1 for l in lo_hang
        if l["khoi_luong_kho_kg"] is not None and l["khoi_luong_kho_kg"] > l["khoi_luong_tuoi_kg"])
bao(n == 0, f"I9: {n} lô hàng có khối lượng khô > khối lượng tươi")

n = sum(1 for l in lo_hang if l["kiem_nghiem"] is not None)
bao(n == 0, f"I-kiemnghiem: {n} lô hàng có phiếu kiểm nghiệm dựng — phải để null")

n = sum(1 for x in lo_dat + vu + dot + lo_hang + bich + cay if x.get("nguon") not in ("that", "mau", "dan_xuat"))
bao(n == 0, f"I7: {n} bản ghi thiếu hoặc sai trường nguon")

# khoá ngoại
n = sum(1 for x in vu + dot + cay if x["lo_id"] not in LO_IDS)
n += sum(1 for x in lo_hang if x["lo_dat_id"] not in LO_IDS)
n += sum(1 for x in canh_bao if x["lo_id"] is not None and x["lo_id"] not in LO_IDS)
n += sum(1 for r in lo_thang + nhat_ky if r["lo_id"] not in LO_IDS)
bao(n == 0, f"FK lo_id: {n} tham chiếu tới lô không tồn tại")

n = sum(1 for x in lo_hang if x["vu_id"] not in vu_map)
n += sum(1 for x in lo_hang if x["dot_thu_id"] not in {d["dot_id"] for d in dot})
n += sum(1 for r in nhat_ky if r["vu_id"] and r["vu_id"] not in vu_map)
bao(n == 0, f"FK vu_id: {n} tham chiếu tới vụ không tồn tại")

# cảnh báo mức farm không được gắn lô
n = sum(1 for c in canh_bao if (c["pham_vi"] == "farm") != (c["lo_id"] is None))
bao(n == 0, f"canh_bao: {n} bản ghi lệch giữa pham_vi và lo_id")

# bảng lô × tháng phải đủ
bao(len(lo_thang) == 156, f"lo_thang: {len(lo_thang)} hàng, phải là 12 lô × 13 tháng = 156")

# trùng khoá
for ten, ds, k in (("lo_dat", lo_dat, "lo_id"), ("vu", vu, "vu_id"), ("lo_hang", lo_hang, "id"),
                   ("bich", bich, "id"), ("cay", cay, "id"), ("canh_bao", canh_bao, "cb_id"),
                   ("dot_thu", dot, "dot_id")):
    ks = [x[k] for x in ds]
    bao(len(ks) == len(set(ks)), f"{ten}: có khoá {k} trùng")

# lớp đo được không được mang nguon khác 'that'
n = sum(1 for l in lo_dat if l["nguon"] != "that")
bao(n == 0, f"I8: {n} lô đất mang nguon khác 'that'")

if loi:
    print("  ✗ " + "\n  ✗ ".join(loi))
    print(f"\n{len(loi)} lỗi.")
    sys.exit(1)
print("  ✓ 12 bất biến, khoá ngoại, khoá trùng — không lỗi\n\nBộ dữ liệu hợp lệ.")
