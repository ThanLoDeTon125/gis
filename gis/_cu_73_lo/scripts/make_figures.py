"""Dựng bản đồ lô và gom TOÀN BỘ ảnh về một thư mục duy nhất: images/.

Quy ước đặt tên trong images/:
  00_*  ảnh tổng quan và kiểm chứng
  10_*  bản đồ lô
  20_*  ảnh nền chuyên đề (địa hình)
  ngay_YYYY-MM-DD.png   MỘT ảnh cho MỖI ngày có dữ liệu vệ tinh
"""
import glob
import json
import math
import os
import re
import shutil

import geopandas as gpd
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
import rasterio
from PIL import Image
from matplotlib.colors import LinearSegmentedColormap
from matplotlib.patches import Patch

BASE = os.path.expanduser("~/Documents/GIS_RiTi_TrangAn")
IMG = f"{BASE}/images"
UTM = "EPSG:32648"

SURFACE, GRID, AXIS = "#fcfcfb", "#e1e0d9", "#c3c2b7"
INK, INK2, MUTED = "#0b0b0b", "#52514e", "#898781"
# Bảng màu định danh, thứ tự cố định, không xoay vòng.
# Bộ 4 màu này đã qua validate_palette.js ở chế độ mọi-cặp (bản đồ thì hai lớp
# bất kỳ đều có thể nằm kề nhau, không chỉ các cặp liền kề trong chú giải).
# Ngọc #1baf7a có tương phản 2,74:1 so với nền -> bắt buộc có nhãn hiện trên
# từng lô và bảng số liệu kèm theo, và cả hai đều có.
KIND_COLOR = {
    "Tán dày ổn định — cây lâu năm/vườn": "#2a78d6",
    "Bật xanh mạnh — mới gieo/tái sinh": "#eb6834",
    "Sinh trưởng đều": "#1baf7a",
    "Che phủ thưa / đất trống, công trình": "#4a3aa7",
    "không đủ dữ liệu (mây)": "#898781",
}
NDVI_CMAP = LinearSegmentedColormap.from_list(
    "greens1hue", ["#f1f8ee", "#cfe8c6", "#a3d29a", "#6fb56d", "#3d9648",
                   "#1c7734", "#0a5423"])


def merc_y(lat):
    return math.log(math.tan(math.pi / 4 + math.radians(lat) / 2))


def parcel_map():
    g = json.load(open(f"{BASE}/data/out/georef.json"))
    b, (EW, EH) = g["esri_bounds"], g["esri_size"]
    my_top, my_bot = merc_y(b["north"]), merc_y(b["south"])

    def lonlat_to_shot(lon, lat):
        mx = (lon - b["west"]) / (b["east"] - b["west"]) * EW
        my = (merc_y(lat) - my_top) / (my_bot - my_top) * EH
        return ((mx - g["esri_x"]) / g["scale"] + g["crop_x"],
                (my - g["esri_y"]) / g["scale"] + g["crop_y"])

    aoi = gpd.read_file(f"{BASE}/data/out/aoi_riti.geojson")
    par = gpd.read_file(f"{BASE}/data/out/parcels.geojson")
    img = np.asarray(Image.open(f"{BASE}/data/raw/screenshot.png").convert("RGB"))

    ax_, ay_ = zip(*[lonlat_to_shot(x, y)
                     for x, y in zip(*aoi.geometry.iloc[0].exterior.xy)])
    x0, y0 = int(min(ax_)) - 30, int(min(ay_)) - 30
    x1, y1 = int(max(ax_)) + 30, int(max(ay_)) + 30

    fig, ax = plt.subplots(figsize=(13, 13 * (y1 - y0) / (x1 - x0)),
                           dpi=130, facecolor=SURFACE)
    ax.imshow(img[y0:y1, x0:x1], extent=[x0, x1, y1, y0])

    for _, r in par.iterrows():
        col = KIND_COLOR.get(r["loai"], "#898781")
        for poly in ([r.geometry] if r.geometry.geom_type == "Polygon"
                     else r.geometry.geoms):
            px, py = zip(*[lonlat_to_shot(x, y) for x, y in poly.exterior.coords])
            ax.fill(px, py, color=col, alpha=0.42, lw=0)
            ax.plot(px, py, color=col, lw=1.6)
        c = r.geometry.representative_point()
        cx, cy = lonlat_to_shot(c.x, c.y)
        ax.annotate(r["lo_id"], (cx, cy), ha="center", va="center",
                    fontsize=8.5, color="white",
                    bbox=dict(boxstyle="round,pad=0.22", fc="#0b0b0b",
                              ec="none", alpha=0.72))
    ax.plot(ax_, ay_, color="#ffffff", lw=2.6)
    ax.plot(ax_, ay_, color=INK, lw=1.4)

    ax.set_xlim(x0, x1); ax.set_ylim(y1, y0)
    ax.set_xticks([]); ax.set_yticks([])
    for s in ax.spines.values():
        s.set_visible(False)
    used = [k for k in KIND_COLOR if (par["loai"] == k).any()]
    ax.legend(handles=[Patch(facecolor=KIND_COLOR[k], alpha=0.6, label=k)
                       for k in used],
              loc="upper left", bbox_to_anchor=(0, -0.015), frameon=False,
              fontsize=9, labelcolor=INK2, ncol=2)
    ax.set_title(f"RiTi Organic Farm — {len(par)} lô, tổng "
                 f"{par.to_crs(UTM).area.sum()/10_000:.2f} ha",
                 color=INK, fontsize=14, loc="left", pad=10)
    fig.tight_layout(rect=[0, 0.10, 1, 1])
    fig.savefig(f"{IMG}/10_ban_do_lo.png", dpi=130, facecolor=SURFACE)
    plt.close(fig)
    print("-> 10_ban_do_lo.png")


def daily_images():
    """MỘT ảnh cho MỖI ngày: ảnh thật + NDVI + ranh giới lô, ghép trong 1 file."""
    aoi = gpd.read_file(f"{BASE}/data/out/aoi_riti.geojson").to_crs(UTM)
    par = gpd.read_file(f"{BASE}/data/out/parcels.geojson").to_crs(UTM)
    for f in sorted(glob.glob(f"{BASE}/data/out/rasters/ndvi_*.tif")):
        d = re.search(r"ndvi_(\d{4}-\d\d-\d\d)", f).group(1)
        with rasterio.open(f) as src:
            arr, tr, Hh, Ww = src.read(1), src.transform, src.height, src.width
        ext = [tr.c, tr.c + Ww * tr.a, tr.f + Hh * tr.e, tr.f]
        fig, ax = plt.subplots(figsize=(7.6, 6.4), dpi=130, facecolor=SURFACE)
        im = ax.imshow(arr, extent=ext, cmap=NDVI_CMAP, vmin=0, vmax=0.9,
                       interpolation="nearest")
        par.boundary.plot(ax=ax, color="#0b0b0b", lw=0.7, alpha=0.75)
        aoi.boundary.plot(ax=ax, color="#0b0b0b", lw=2.0)
        minx, miny, maxx, maxy = aoi.total_bounds
        ax.set_xlim(minx - 40, maxx + 40); ax.set_ylim(miny - 40, maxy + 40)
        ax.set_xticks([]); ax.set_yticks([])
        for s in ax.spines.values():
            s.set_visible(False)
        cb = fig.colorbar(im, ax=ax, fraction=0.04, pad=0.02)
        cb.set_label("NDVI", color=INK2, fontsize=9)
        cb.ax.tick_params(colors=MUTED, labelsize=8)
        cb.outline.set_visible(False)
        v = arr[np.isfinite(arr)]
        ax.set_title(f"{d[8:]}/{d[5:7]}/{d[:4]} — NDVI theo lô "
                     f"(trung bình vùng {v.mean():.3f})",
                     color=INK, fontsize=12, loc="left")
        fig.tight_layout()
        fig.savefig(f"{IMG}/ngay_{d}.png", dpi=130, facecolor=SURFACE)
        plt.close(fig)
        print(f"-> ngay_{d}.png")


def collect():
    """Gom các hình đã dựng ở bước khác về cùng thư mục, đổi tên có thứ tự."""
    pairs = [
        ("figs/verify_outline.png", "00_kiem_chung_ranh_gioi.png"),
        ("figs/aoi_overlay.png", "01_ranh_gioi_tren_anh_nen.png"),
        ("figs/summary_ndvi_rain.png", "02_ndvi_va_mua_1_thang.png"),
        ("figs/ndvi_maps.png", "03_ndvi_ba_ngay_quang.png"),
        ("figs/zones.png", "11_phan_vung_4_nhom.png"),
        ("figs/terrain.png", "20_dia_hinh_do_doc.png"),
        ("data/raw/screenshot.png", "99_anh_chup_goc.png"),
    ]
    for src, dst in pairs:
        s = f"{BASE}/{src}"
        if os.path.exists(s):
            shutil.copy2(s, f"{IMG}/{dst}")
            print(f"-> {dst}")


if __name__ == "__main__":
    os.makedirs(IMG, exist_ok=True)
    parcel_map()
    daily_images()
    collect()
    n = len(os.listdir(IMG))
    print(f"\n{n} ảnh trong {IMG}")
