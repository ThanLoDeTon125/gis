"""Kiểm chứng đường viền đã tách và phép georeference tự động.

Hai phép kiểm độc lập nhau:
  A. Chiếu polygon NGƯỢC về ảnh chụp -> phải trùng nét vẽ đỏ (kiểm khâu tách).
  B. Chiếu polygon lên ảnh nền Esri  -> phải bám đúng đường/bờ (kiểm khâu georef).
Thêm: dò chân ghim bản đồ để so với toạ độ thật lấy từ URL Google Maps.
"""
import json
import math
import os

import geopandas as gpd
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
from PIL import Image
from scipy.ndimage import binary_dilation, distance_transform_edt
from skimage.morphology import disk

BASE = os.path.expanduser("~/Documents/GIS_RiTi_TrangAn")
INK, MUTED, SURFACE = "#0b0b0b", "#898781", "#fcfcfb"


def merc_y(lat):
    return math.log(math.tan(math.pi / 4 + math.radians(lat) / 2))


def main():
    g = json.load(open(f"{BASE}/data/out/georef.json"))
    b = g["esri_bounds"]
    EW, EH = g["esri_size"]
    my_top, my_bot = merc_y(b["north"]), merc_y(b["south"])

    def lonlat_to_shot(lon, lat):
        mx = (lon - b["west"]) / (b["east"] - b["west"]) * EW
        my = (merc_y(lat) - my_top) / (my_bot - my_top) * EH
        return ((mx - g["esri_x"]) / g["scale"] + g["crop_x"],
                (my - g["esri_y"]) / g["scale"] + g["crop_y"])

    def shot_to_lonlat(px, py):
        mx = g["esri_x"] + (px - g["crop_x"]) * g["scale"]
        my = g["esri_y"] + (py - g["crop_y"]) * g["scale"]
        lon = b["west"] + (mx / EW) * (b["east"] - b["west"])
        lat = math.degrees(2 * math.atan(math.exp(
            my_top + (my / EH) * (my_bot - my_top))) - math.pi / 2)
        return lon, lat

    shot = np.asarray(Image.open(f"{BASE}/data/raw/screenshot.png").convert("RGB"))
    a = shot.astype(int)
    red = (a[..., 0] > 170) & (a[..., 0] - a[..., 1] > 60) & (a[..., 0] - a[..., 2] > 60)
    pin = binary_dilation(distance_transform_edt(red) > 8, disk(6))
    ys, xs = np.where(pin)
    # Ghim Google Maps là hình giọt nước, điểm neo là ĐỈNH NHỌN phía dưới
    tip_y = ys.max()
    tip_x = xs[ys > tip_y - 3].mean()
    lon, lat = shot_to_lonlat(tip_x, tip_y)
    de = (lon - 105.854332) * 111320 * math.cos(math.radians(20.258))
    dn = (lat - 20.2579952) * 110574
    print(f"chân ghim dò được ở pixel ({tip_x:.0f}, {tip_y})")
    print(f"  suy ra : {lat:.7f}, {lon:.7f}")
    print(f"  thật   : 20.2579952, 105.8543320")
    print(f"  LỆCH   : {de:+.1f} m đông, {dn:+.1f} m bắc "
          f"-> tổng {math.hypot(de, dn):.1f} m")

    aoi = gpd.read_file(f"{BASE}/data/out/aoi_riti.geojson")
    lons, lats = aoi.geometry.iloc[0].exterior.xy
    sx, sy = zip(*[lonlat_to_shot(x, y) for x, y in zip(lons, lats)])

    fig, ax = plt.subplots(1, 2, figsize=(15, 5.4), dpi=115, facecolor=SURFACE)
    ax[0].imshow(shot)
    ax[0].plot(sx, sy, color="#00e5ff", lw=1.2, ls="--")
    ax[0].plot(tip_x, tip_y, marker="v", ms=9, color="#ffd60a", mec="black", mew=1)
    ax[0].set_title("A. Polygon chiếu ngược về ảnh chụp\n"
                    "(lam đứt nét phải nằm giữa nét vẽ đỏ)",
                    fontsize=11, color=INK, loc="left")

    meta = json.load(open(f"{BASE}/data/raw/basemap_meta.json"))
    esri = np.asarray(Image.open(
        f"{BASE}/data/raw/esri_basemap_z{meta['zoom']}.png"))
    ax[1].imshow(esri, extent=[b["west"], b["east"], b["south"], b["north"]])
    ax[1].plot(lons, lats, color="#00e5ff", lw=1.6)
    ax[1].plot(105.854332, 20.2579952, marker="o", ms=8, color="#ffd60a",
               mec="black", mew=1.2, ls="none")
    minx, miny, maxx, maxy = aoi.total_bounds
    ax[1].set_xlim(minx - 0.0012, maxx + 0.0012)
    ax[1].set_ylim(miny - 0.0009, maxy + 0.0009)
    ax[1].set_title("B. Cũng polygon đó trên ảnh nền có toạ độ chuẩn\n"
                    "(phải bám đường và bờ ruộng)",
                    fontsize=11, color=INK, loc="left")
    ax[1].ticklabel_format(useOffset=False, style="plain")
    ax[1].tick_params(colors=MUTED, labelsize=8)
    ax[0].set_xticks([]); ax[0].set_yticks([])
    for s in ax[0].spines.values():
        s.set_visible(False)
    fig.tight_layout()
    fig.savefig(f"{BASE}/figs/verify_outline.png", dpi=115, facecolor=SURFACE)
    print("đã ghi: figs/verify_outline.png")


if __name__ == "__main__":
    main()
