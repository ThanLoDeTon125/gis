"""Hình tổng hợp: NDVI theo thời gian, mưa theo ngày, và bản đồ NDVI 3 ngày quang.

Quy ước trình bày (theo chuẩn dataviz):
  - KHÔNG dùng hai trục y trên cùng một khung. NDVI và lượng mưa là hai đại
    lượng khác thang -> tách thành hai khung chồng nhau, dùng chung trục ngày.
  - Thang liên tục (NDVI) tô bằng MỘT sắc, nhạt->đậm; không dùng cầu vồng.
  - Lưới và trục lùi về sau; chữ dùng mực trung tính, không nhuộm theo màu chuỗi.
"""
import csv
import glob
import os
import re
from datetime import datetime

import geopandas as gpd
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
import rasterio
from matplotlib.colors import LinearSegmentedColormap
from matplotlib.dates import DateFormatter, DayLocator

BASE = os.path.expanduser("~/Documents/GIS_RiTi_TrangAn")

SURFACE, GRID, AXIS = "#fcfcfb", "#e1e0d9", "#c3c2b7"
INK, INK2, MUTED = "#0b0b0b", "#52514e", "#898781"
VEG = "#008300"      # slot 6 — chuỗi thực vật
WATER = "#2a78d6"    # slot 1 — chuỗi lượng mưa
# Thang NDVI: một sắc lục, nhạt -> đậm
NDVI_CMAP = LinearSegmentedColormap.from_list(
    "greens1hue", ["#f1f8ee", "#cfe8c6", "#a3d29a", "#6fb56d", "#3d9648",
                   "#1c7734", "#0a5423"])


def style(ax):
    ax.set_facecolor(SURFACE)
    for s in ("top", "right"):
        ax.spines[s].set_visible(False)
    for s in ("left", "bottom"):
        ax.spines[s].set_color(AXIS)
        ax.spines[s].set_linewidth(1.0)
    ax.tick_params(colors=MUTED, labelsize=9, length=3)
    for lb in ax.get_xticklabels() + ax.get_yticklabels():
        lb.set_color(INK2)
    ax.grid(axis="y", color=GRID, lw=0.8, zorder=0)
    ax.set_axisbelow(True)


def main():
    s2 = list(csv.DictReader(open(f"{BASE}/data/out/sentinel2_ndvi_timeseries.csv")))
    clim = list(csv.DictReader(open(f"{BASE}/data/out/climate_daily.csv")))

    good = [r for r in s2 if r.get("ndvi_mean")]
    bad = [r for r in s2 if not r.get("ndvi_mean")]
    gd = [datetime.strptime(r["date"], "%Y-%m-%d") for r in good]
    gv = [float(r["ndvi_mean"]) for r in good]
    p10 = [float(r["ndvi_p10"]) for r in good]
    p90 = [float(r["ndvi_p90"]) for r in good]
    bd = [datetime.strptime(r["date"], "%Y-%m-%d") for r in bad]

    cd = [datetime.strptime(r["date"], "%Y-%m-%d") for r in clim]
    rain = [float(r["precipitation_sum"]) for r in clim]

    fig, (ax1, ax2) = plt.subplots(
        2, 1, figsize=(11, 7.6), dpi=120, sharex=True,
        gridspec_kw={"height_ratios": [1.25, 1], "hspace": 0.18},
        facecolor=SURFACE)

    # --- Khung 1: NDVI ------------------------------------------------------
    style(ax1)
    ax1.fill_between(gd, p10, p90, color=VEG, alpha=0.14, lw=0, zorder=2,
                     label="Khoảng phân tán trong farm (P10–P90)")
    ax1.plot(gd, gv, color=VEG, lw=2, zorder=3, label="NDVI trung bình")
    ax1.plot(gd, gv, "o", ms=9, mfc=VEG, mec=SURFACE, mew=2, ls="none", zorder=4)
    for x, y in zip(gd, gv):
        ax1.annotate(f"{y:.3f}", (x, y), textcoords="offset points",
                     xytext=(0, 13), ha="center", color=INK, fontsize=10.5,
                     zorder=5)
    # Không giấu các lượt bay bị mây — vẽ chúng ra ở đáy khung
    ax1.plot(bd, [0.02] * len(bd), marker="x", ls="none", ms=7, mew=1.6,
             color=MUTED, zorder=3, label="Lượt bay bị mây che (không dùng được)")
    ax1.set_ylim(0, 1.0)
    ax1.set_ylabel("NDVI", color=INK2, fontsize=10)
    farm_ha = gpd.read_file(f"{BASE}/data/out/aoi_riti.geojson").to_crs(
        "EPSG:32648").area.iloc[0] / 10_000
    ax1.set_title(f"Vùng trồng RiTi Organic Farm — {farm_ha:.2f} ha".replace(".", ",")
                  + f" · {cd[0]:%d/%m} – {cd[-1]:%d/%m/%Y}",
                  color=INK, fontsize=13.5, loc="left", pad=54)
    ax1.text(0, 1.135, "Chỉ số thực vật NDVI tăng đều qua cả ba lượt ảnh quang mây",
             transform=ax1.transAxes, color=INK2, fontsize=10.5)
    # Chú giải thành một hàng ngang phía trên khung — đặt trong khung sẽ đè lên
    # dải phân tán và các dấu lượt bay bị mây.
    ax1.legend(loc="lower left", bbox_to_anchor=(0, 1.0), ncol=3, frameon=False,
               fontsize=9.5, labelcolor=INK2, handlelength=1.6,
               columnspacing=1.6, borderpad=0)

    # --- Khung 2: mưa (trục riêng, KHÔNG chồng trục với NDVI) ---------------
    style(ax2)
    ax2.bar(cd, rain, width=0.72, color=WATER, zorder=3, linewidth=0)
    ax2.set_ylabel("Lượng mưa ngày (mm)", color=INK2, fontsize=10)
    tot = sum(rain)
    wet = sum(1 for r in rain if r >= 1)
    et0 = sum(float(r["et0_fao_evapotranspiration"]) for r in clim)
    ax2.text(0, 1.02, f"Mưa: {tot:.0f} mm trong {len(rain)} ngày · {wet} ngày có mưa "
                      f"· cân bằng nước {tot-et0:+.0f} mm so với bốc thoát hơi",
             transform=ax2.transAxes, color=INK2, fontsize=10.5)
    ax2.xaxis.set_major_locator(DayLocator(interval=4))
    ax2.xaxis.set_major_formatter(DateFormatter("%d/%m"))

    fig.text(0.008, 0.012,
             "Nguồn: Sentinel-2 L2A (ESA/Copernicus qua AWS Open Data) · "
             "khí hậu Open-Meteo · ranh giới số hoá từ ảnh Google Maps, "
             "georeference bằng Esri World Imagery",
             color=MUTED, fontsize=8.2)
    fig.tight_layout(rect=[0, 0.03, 1, 1])
    fig.savefig(f"{BASE}/figs/summary_ndvi_rain.png", dpi=120, facecolor=SURFACE)
    print("đã ghi: figs/summary_ndvi_rain.png")

    # --- Bản đồ NDVI ba ngày quang -----------------------------------------
    files = sorted(glob.glob(f"{BASE}/data/out/rasters/ndvi_*.tif"))
    aoi = gpd.read_file(f"{BASE}/data/out/aoi_riti.geojson").to_crs("EPSG:32648")
    fig2, axes = plt.subplots(1, len(files), figsize=(4.3 * len(files), 4.8),
                              dpi=120, facecolor=SURFACE)
    for ax, f in zip(np.atleast_1d(axes), files):
        d = re.search(r"ndvi_(\d{4}-\d\d-\d\d)", f).group(1)
        with rasterio.open(f) as src:
            a = src.read(1)
            tr, H, W = src.transform, src.height, src.width
        ext = [tr.c, tr.c + W * tr.a, tr.f + H * tr.e, tr.f]
        im = ax.imshow(a, extent=ext, cmap=NDVI_CMAP, vmin=0, vmax=0.9,
                       interpolation="nearest")
        aoi.boundary.plot(ax=ax, color=INK, lw=1.6)
        ax.set_xticks([]); ax.set_yticks([])
        for sp in ax.spines.values():
            sp.set_visible(False)
        ax.set_title(datetime.strptime(d, "%Y-%m-%d").strftime("%d/%m/%Y"),
                     color=INK, fontsize=11.5, loc="left")
    cb = fig2.colorbar(im, ax=np.atleast_1d(axes).tolist(), fraction=0.035,
                       pad=0.02)
    cb.set_label("NDVI", color=INK2, fontsize=10)
    cb.ax.tick_params(colors=MUTED, labelsize=9)
    cb.outline.set_visible(False)
    fig2.suptitle("NDVI trong ranh giới vùng trồng — Sentinel-2 10 m",
                  color=INK, fontsize=13, x=0.012, ha="left", y=0.985)
    fig2.savefig(f"{BASE}/figs/ndvi_maps.png", dpi=120, facecolor=SURFACE,
                 bbox_inches="tight")
    print("đã ghi: figs/ndvi_maps.png")


if __name__ == "__main__":
    main()
