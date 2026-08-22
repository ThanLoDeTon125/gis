"""Hình kiểm chứng: nét vẽ tay (vàng) ↔ nét đã nắn (lam), trên ảnh nền sạch.

Ba khung: toàn farm, và hai khung phóng to vào nơi nắn nhiều nhất — chỗ nào
diện tích đổi >10% thì phải xem tận mắt xem nắn đúng mép ruộng hay chạy theo
bóng cây.
"""
import json
import os

import geopandas as gpd
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
from PIL import Image

from georef_image import lonlat_to_shot

BASE = os.path.expanduser("~/Documents/GIS_RiTi_TrangAn")


def rings(gdf, g):
    out = []
    for geom, lo in zip(gdf.geometry, gdf["lo"]):
        gs = [geom] if geom.geom_type == "Polygon" else list(geom.geoms)
        for p in gs:
            xy = np.array([lonlat_to_shot(g, x, y) for x, y in p.exterior.coords])
            out.append((lo, xy))
    return out


def main():
    g = json.load(open(f"{BASE}/data/out/georef_clean.json"))
    img = np.asarray(Image.open(f"{BASE}/data/raw/screenshot_clean.png").convert("RGB"))

    raw = gpd.read_file(f"{BASE}/data/out/lots_raw.geojson")
    from snap_lots import REGION_TO_LOT
    raw["lo"] = [REGION_TO_LOT[i] for i in range(len(raw))]
    snap = gpd.read_file(f"{BASE}/data/out/lots.geojson")

    r0, r1 = rings(raw, g), rings(snap, g)
    d = snap.set_index("lo_id")["chenh_pct"].abs().sort_values(ascending=False)
    hot = list(d.index[:2])
    print("nắn nhiều nhất:", ", ".join(f"{k} {d[k]:+.0f}%" for k in d.index[:4]))

    fig = plt.figure(figsize=(15, 8.2), dpi=125)
    gs = fig.add_gridspec(2, 3, width_ratios=[2, 1, 1], hspace=0.06, wspace=0.06)
    ax = fig.add_subplot(gs[:, 0])
    axz = [fig.add_subplot(gs[0, 1]), fig.add_subplot(gs[0, 2]),
           fig.add_subplot(gs[1, 1]), fig.add_subplot(gs[1, 2])]

    def draw(a):
        a.imshow(img)
        for lo, xy in r0:
            a.plot(xy[:, 0], xy[:, 1], color="#ffd60a", lw=1.9, alpha=0.95)
        for lo, xy in r1:
            a.plot(xy[:, 0], xy[:, 1], color="#0affe4", lw=1.5)
        a.set_xticks([]); a.set_yticks([])

    draw(ax)
    for lo, xy in r1:
        a = snap.set_index("lo").loc[lo, "area_ha"]
        ax.text(xy[:, 0].mean(), xy[:, 1].mean(), f"{int(lo)}\n{a:.2f}ha",
                color="w", ha="center", va="center", fontsize=9, weight="bold",
                path_effects=None)
    ax.set_title("12 lô: nét vẽ tay (vàng) → nắn về mép thật (lam)", fontsize=11)

    for a, lo_id in zip(axz, hot + list(d.index[2:4])):
        lo = int(lo_id[1:])
        xy = [x for l, x in r1 if l == lo][0]
        cx, cy = xy[:, 0].mean(), xy[:, 1].mean()
        h = max(np.ptp(xy[:, 0]), np.ptp(xy[:, 1])) * 0.75 + 30
        draw(a)
        a.set_xlim(cx - h, cx + h); a.set_ylim(cy + h, cy - h)
        row = snap.set_index("lo_id").loc[lo_id]
        a.set_title(f"lô {lo}: {row['area_ve_tay_ha']:.3f} → {row['area_ha']:.3f} ha "
                    f"({row['chenh_pct']:+.0f}%)", fontsize=9)

    fig.savefig(f"{BASE}/figs/kiem_nan_lo.png", dpi=125, bbox_inches="tight")
    print("đã ghi: figs/kiem_nan_lo.png")


if __name__ == "__main__":
    main()
