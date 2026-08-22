"""Dựng 12 lô từ nét vẽ vector trong 'map mới.pdf' -> polygon có toạ độ thật.

Ba bước:
  1. Rasterise 27 nét vector lên lưới ảnh, hàn các khe hở ở đầu nét (chủ farm
     vẽ tay nên hai nét gặp nhau thường hụt vài pixel — không hàn thì hai lô
     kề nhau sẽ rò sang nhau và dính thành một).
  2. Gán nhãn các vùng nền -> mỗi vùng kín là một lô. Vùng chạm mép ảnh là
     phần ngoài farm, loại bỏ.
  3. Nhận số lô bằng cách dò các vệt chữ số (blob rời khỏi mạng nét) trên bản
     PDF đã render, rồi chiếu tâm vệt vào vùng chứa nó.

Toạ độ pixel -> WGS84 dùng georef của ẢNH SẠCH (data/out/georef_clean.json),
vì PDF nhúng đúng ảnh đó (đã đối chiếu: lệch 130/1.568.040 pixel).
"""
import json
import math
import os

import geopandas as gpd
import numpy as np
from PIL import Image, ImageDraw
from scipy.ndimage import binary_closing, binary_dilation, label
from shapely.geometry import Polygon
from skimage.measure import find_contours
from skimage.morphology import disk

from georef_image import lonlat_to_shot, shot_to_lonlat   # noqa: F401

BASE = os.path.expanduser("~/Documents/GIS_RiTi_TrangAn")
UTM = "EPSG:32648"
SS = 2                 # siêu lấy mẫu: vẽ nét ở lưới gấp đôi cho biên mượt
STROKE_W = 3           # bề rộng nét khi rasterise (px ảnh gốc)
CLOSE_R = 7            # bán kính hàn khe hở đầu nét (px ảnh gốc)
MIN_AREA_PX = 1500     # vùng nhỏ hơn = kẽ hở giữa hai nét, không phải lô


def rasterise(strokes, W, H):
    im = Image.new("1", (W * SS, H * SS), 0)
    d = ImageDraw.Draw(im)
    for s in strokes:
        pts = [(x * SS, y * SS) for x, y in s["pts"]]
        d.line(pts, fill=1, width=STROKE_W * SS, joint="curve")
    return np.asarray(im, bool)


def regions(lines):
    """Vùng kín giữa các nét. Hàn khe hở trước, nếu không các lô rò vào nhau."""
    closed = binary_closing(lines, disk(CLOSE_R * SS))
    lab, n = label(~closed)
    print(f"  {n} vùng nền trước khi lọc")
    keep = []
    border = set(lab[0, :]) | set(lab[-1, :]) | set(lab[:, 0]) | set(lab[:, -1])
    for i in range(1, n + 1):
        if i in border:
            continue                      # chạm mép ảnh -> ngoài farm
        m = lab == i
        if m.sum() < MIN_AREA_PX * SS * SS:
            continue
        keep.append(m)
    keep.sort(key=lambda m: -m.sum())
    print(f"  {len(keep)} vùng kín đủ lớn")
    return keep, closed


def digit_blobs(lines_full):
    """Tâm các vệt chữ số trên bản render, quy về hệ pixel ảnh nền."""
    page = np.asarray(Image.open(f"{BASE}/data/out/_page_render.png").convert("RGB"))
    base = np.asarray(Image.open(f"{BASE}/data/raw/screenshot_clean.png").convert("RGB"))
    PH, PW = page.shape[:2]
    BH, BW = base.shape[:2]
    # Ảnh nền chiếm phần trái của trang; tỉ lệ suy từ chiều cao (trang = đúng ảnh)
    sc = PH / BH
    IW = int(round(BW * sc))
    sub = page[:, :IW].astype(int)
    ref = np.asarray(Image.fromarray(base.astype(np.uint8)).resize((IW, PH))).astype(int)
    drawn = (np.abs(sub - ref).max(axis=2) > 60) & (sub.min(axis=2) > 150)

    # Bỏ mạng nét -> còn lại chữ số
    ln = np.asarray(Image.fromarray(
        (lines_full * 255).astype(np.uint8)).resize((IW, PH))) > 100
    ln = binary_dilation(ln, disk(4))
    blobs = drawn & ~ln
    lab, n = label(binary_dilation(blobs, disk(3)))
    out = []
    for i in range(1, n + 1):
        ys, xs = np.nonzero(lab == i)
        if len(ys) < 120:
            continue
        out.append({"x": float(xs.mean()) / sc, "y": float(ys.mean()) / sc,
                    "n": len(ys), "w": int(xs.max() - xs.min()),
                    "h": int(ys.max() - ys.min())})
    return out


def main():
    st = json.load(open(f"{BASE}/data/out/pdf_strokes.json"))
    W, H = st["image_size"]
    g = json.load(open(f"{BASE}/data/out/georef_clean.json"))

    lines = rasterise(st["strokes"], W, H)
    print(f"rasterise {len(st['strokes'])} nét trên lưới {W*SS}x{H*SS}")
    regs, closed = regions(lines)

    lines_full = np.asarray(Image.fromarray(
        (lines * 255).astype(np.uint8)).resize((W, H))) > 100
    blobs = digit_blobs(lines_full)
    print(f"  {len(blobs)} vệt chữ số")

    # Gom vệt gần nhau (số 10, 11, 12 gồm hai chữ số)
    blobs.sort(key=lambda b: b["x"])
    groups = []
    for b in blobs:
        if groups and abs(b["x"] - groups[-1][-1]["x"]) < 30 \
                and abs(b["y"] - groups[-1][-1]["y"]) < 25:
            groups[-1].append(b)
        else:
            groups.append([b])
    marks = [{"x": sum(b["x"] for b in gp) / len(gp),
              "y": sum(b["y"] for b in gp) / len(gp),
              "k": len(gp)} for gp in groups]
    print(f"  {len(marks)} nhãn số sau khi gom")

    feats = []
    for m in regs:
        cs = find_contours(m.astype(float), 0.5)
        cont = max(cs, key=len)
        ring = [shot_to_lonlat(g, c / SS, r / SS) for r, c in cont]
        p = Polygon(ring)
        if not p.is_valid:
            p = p.buffer(0)
        ys, xs = np.nonzero(m)
        feats.append({"geometry": p, "cx": xs.mean() / SS, "cy": ys.mean() / SS,
                      "px_area": int(m.sum() / SS / SS), "mask": m})

    # Gán nhãn số cho vùng chứa tâm nhãn
    for f in feats:
        f["label_xy"] = None
    for mk in marks:
        for f in feats:
            r, c = int(mk["y"] * SS), int(mk["x"] * SS)
            if 0 <= r < f["mask"].shape[0] and 0 <= c < f["mask"].shape[1] \
                    and f["mask"][r, c]:
                f["label_xy"] = (round(mk["x"], 1), round(mk["y"], 1))
                f["n_digit"] = mk["k"]
                break

    gdf = gpd.GeoDataFrame(
        [{k: v for k, v in f.items() if k != "mask"} for f in feats],
        crs="EPSG:4326")
    gdf["area_ha"] = gdf.to_crs(UTM).area / 10_000
    gdf = gdf.sort_values("area_ha", ascending=False).reset_index(drop=True)
    print(f"\n{len(gdf)} vùng, tổng {gdf['area_ha'].sum():.3f} ha")
    print(gdf[["cx", "cy", "px_area", "area_ha", "label_xy"]].to_string())

    gdf.drop(columns=[c for c in ("mask",) if c in gdf]).to_file(
        f"{BASE}/data/out/lots_raw.geojson", driver="GeoJSON")
    json.dump(marks, open(f"{BASE}/data/out/lot_marks.json", "w"), indent=1)
    print("\nđã ghi: data/out/lots_raw.geojson, lot_marks.json")


if __name__ == "__main__":
    main()
