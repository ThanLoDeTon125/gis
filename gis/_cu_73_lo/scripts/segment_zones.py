"""Phân vùng các lô trồng bên trong ranh giới farm, từ ảnh Sentinel-2.

OSM không có ranh giới thửa ở khu vực này, nên lớp "vùng trồng" được suy ra
từ chính ảnh vệ tinh.

Điểm quan trọng: gom cụm theo CHUỖI THỜI GIAN (NDVI+NDMI của cả 3 ngày quang),
không theo một thời điểm. Hai lô cùng màu xanh vào một ngày nhưng lớn nhanh
chậm khác nhau sẽ tách ra được; nếu chỉ dùng một ảnh thì chúng dính vào nhau.
"""
import glob
import os
import re

import geopandas as gpd
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
import rasterio
from matplotlib.patches import Patch
from rasterio.features import geometry_mask, shapes
from shapely.geometry import shape
from sklearn.cluster import KMeans

BASE = os.path.expanduser("~/Documents/GIS_RiTi_TrangAn")
UTM = "EPSG:32648"
K = 4
MIN_AREA_M2 = 300          # bỏ mảnh vụn nhỏ hơn 3 pixel

# Ramp thứ bậc một sắc (đã qua validate_palette.js --ordinal, light mode)
ORDINAL = ["#104281", "#256abf", "#3987e5", "#86b6ef"]
INK, INK2, MUTED = "#0b0b0b", "#52514e", "#898781"
SURFACE, GRID, AXIS = "#fcfcfb", "#e1e0d9", "#c3c2b7"


def main():
    ndvi_files = sorted(glob.glob(f"{BASE}/data/out/rasters/ndvi_*.tif"))
    dates = [re.search(r"ndvi_(\d{4}-\d\d-\d\d)", f).group(1) for f in ndvi_files]
    print("ngày dùng để phân vùng:", ", ".join(dates))

    stack, prof = [], None
    for f in ndvi_files:
        with rasterio.open(f) as src:
            stack.append(src.read(1))
            prof = src.profile
    for f in sorted(glob.glob(f"{BASE}/data/out/rasters/ndmi_*.tif")):
        with rasterio.open(f) as src:
            stack.append(src.read(1))
    X = np.stack(stack)                       # (n_feat, H, W)
    H, W = X.shape[1:]

    aoi = gpd.read_file(f"{BASE}/data/out/aoi_riti.geojson").to_crs(UTM)
    inside = ~geometry_mask(aoi.geometry, out_shape=(H, W),
                            transform=prof["transform"], invert=False)
    ok = inside & np.all(np.isfinite(X), axis=0)
    print(f"pixel dùng được: {ok.sum()}/{inside.sum()} trong ranh giới")

    feats = X[:, ok].T
    # Chuẩn hoá từng chỉ số về cùng thang, nếu không NDVI sẽ át NDMI
    feats = (feats - feats.mean(0)) / (feats.std(0) + 1e-9)
    km = KMeans(n_clusters=K, n_init=10, random_state=0).fit(feats)

    lab = np.full((H, W), -1, np.int16)
    lab[ok] = km.labels_

    # Đánh số lại theo NDVI trung bình của ngày cuối: 1 = xanh tốt nhất
    last = X[len(ndvi_files) - 1]
    order = sorted(range(K), key=lambda c: -np.nanmean(last[lab == c]))
    remap = {old: new for new, old in enumerate(order, start=1)}
    lab2 = np.where(lab >= 0, np.vectorize(lambda v: remap.get(v, 0))(lab), 0).astype(np.int16)

    prof2 = dict(prof, dtype="int16", nodata=0, count=1)
    with rasterio.open(f"{BASE}/data/out/rasters/zones.tif", "w", **prof2) as d:
        d.write(lab2, 1)

    # Raster -> vector
    polys = []
    for geom, val in shapes(lab2, mask=lab2 > 0, transform=prof["transform"]):
        polys.append({"geometry": shape(geom), "zone": int(val)})
    gdf = gpd.GeoDataFrame(polys, crs=UTM)
    gdf = gdf[gdf.area >= MIN_AREA_M2]
    gdf = gdf.dissolve(by="zone", as_index=False)
    gdf["area_ha"] = (gdf.area / 10_000).round(3)

    summary = []
    for _, r in gdf.iterrows():
        z = int(r["zone"])
        m = lab2 == z
        summary.append({
            "zone": z, "area_ha": r["area_ha"],
            **{f"ndvi_{d}": round(float(np.nanmean(X[i][m])), 3)
               for i, d in enumerate(dates)},
        })
    # Nhãn suy từ dữ liệu, không đặt cứng: mức NDVI cuối kỳ CỘNG với xu hướng.
    # Một lô NDVI cao mà đứng yên (cây lâu năm) khác hẳn một lô NDVI thấp hơn
    # nhưng đang bật mạnh (mới gieo) — dán nhãn theo mức thôi sẽ mô tả sai.
    def describe(s):
        last, first = s[f"ndvi_{dates[-1]}"], s[f"ndvi_{dates[0]}"]
        d = last - first
        if last >= 0.75 and abs(d) < 0.10:
            kind = "tán dày, ổn định (cây lâu năm/vườn)"
        elif d >= 0.25:
            kind = "bật xanh mạnh (mới gieo/tái sinh)"
        elif last >= 0.55:
            kind = "sinh trưởng đều"
        else:
            kind = "thưa — đất trống/công trình"
        return f"Lô {s['zone']} — {kind}"

    desc = {s["zone"]: describe(s) for s in summary}
    gdf["label"] = gdf["zone"].map(desc)
    gdf["ndvi_change"] = gdf["zone"].map(
        {s["zone"]: round(s[f"ndvi_{dates[-1]}"] - s[f"ndvi_{dates[0]}"], 3)
         for s in summary})
    gdf.to_crs("EPSG:4326").to_file(f"{BASE}/data/out/zones.geojson", driver="GeoJSON")
    gdf.to_crs("EPSG:4326").to_file(f"{BASE}/data/out/aoi_riti.gpkg",
                                    driver="GPKG", layer="zones")

    print("\nphân vùng trong ranh giới farm:")
    for s in sorted(summary, key=lambda x: x["zone"]):
        trend = s[f"ndvi_{dates[-1]}"] - s[f"ndvi_{dates[0]}"]
        print(f"  lô {s['zone']}: {s['area_ha']:5.2f} ha  "
              + "  ".join(f"NDVI {d[5:]}={s[f'ndvi_{d}']:.3f}" for d in dates)
              + f"   thay đổi {trend:+.3f}")

    # --- Bản đồ phân vùng ---------------------------------------------------
    fig, ax = plt.subplots(figsize=(9.5, 6.2), dpi=120, facecolor=SURFACE)
    ax.set_facecolor(SURFACE)
    tr = prof["transform"]
    ext = [tr.c, tr.c + W * tr.a, tr.f + H * tr.e, tr.f]
    from matplotlib.colors import ListedColormap
    ax.imshow(np.where(lab2 > 0, lab2, np.nan), extent=ext,
              cmap=ListedColormap(ORDINAL), vmin=1, vmax=K, interpolation="nearest")
    aoi.boundary.plot(ax=ax, color=INK, lw=1.8)
    # Cắt khung sát ranh giới, nếu không lưới 810x670 m để lại nhiều khoảng trắng
    bx0, by0, bx1, by1 = aoi.total_bounds
    ax.set_xlim(bx0 - 25, bx1 + 25)
    ax.set_ylim(by0 - 25, by1 + 25)
    ax.set_xticks([]); ax.set_yticks([])
    for sp in ax.spines.values():
        sp.set_visible(False)
    ax.set_title("Phân vùng lô trồng trong ranh giới RiTi Organic Farm",
                 color=INK, fontsize=13, pad=12, loc="left")
    ax.text(0, 1.005, "", transform=ax.transAxes)
    areas = dict(zip(gdf["zone"], gdf["area_ha"]))
    labels = dict(zip(gdf["zone"], gdf["label"]))
    ax.legend(handles=[Patch(facecolor=ORDINAL[z - 1],
                             label=f"{labels[z]} — {areas[z]:.2f} ha")
                       for z in sorted(areas)],
              loc="upper left", bbox_to_anchor=(0, -0.02), frameon=False,
              fontsize=9.5, labelcolor=INK2, ncol=1)
    fig.text(0.01, 0.005,
             f"Gom cụm K-means trên NDVI+NDMI của {len(dates)} ngày quang mây "
             f"({', '.join(dates)}) · Sentinel-2 10 m",
             color=MUTED, fontsize=8.5)
    fig.tight_layout(rect=[0, 0.22, 1, 1])
    fig.savefig(f"{BASE}/figs/zones.png", dpi=120, facecolor=SURFACE)
    print("\nđã ghi: data/out/zones.geojson, rasters/zones.tif, figs/zones.png")


if __name__ == "__main__":
    main()
