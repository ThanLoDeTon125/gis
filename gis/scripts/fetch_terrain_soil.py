"""Địa hình (Copernicus DEM 30 m) + thổ nhưỡng (SoilGrids 250 m) cho vùng trồng.

Cả hai nguồn đều miễn phí và không cần API key:
  - Copernicus GLO-30 DEM: COG công khai trên AWS Open Data
  - SoilGrids v2.0 (ISRIC): REST API truy vấn theo điểm
"""
import csv
import json
import os

import geopandas as gpd
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
import rasterio
import requests
from rasterio.warp import calculate_default_transform, reproject, Resampling
from rasterio.windows import from_bounds as window_from_bounds

BASE = os.path.expanduser("~/Documents/GIS_RiTi_TrangAn")
UTM = "EPSG:32648"
LAT, LON = 20.2579952, 105.854332

# Ô 1x1 độ chứa farm: N20 E105
DEM_URL = ("https://copernicus-dem-30m.s3.amazonaws.com/"
           "Copernicus_DSM_COG_10_N20_00_E105_00_DEM/"
           "Copernicus_DSM_COG_10_N20_00_E105_00_DEM.tif")


def do_dem():
    aoi = gpd.read_file(f"{BASE}/data/out/aoi_riti.geojson")
    bbox = gpd.read_file(f"{BASE}/data/out/aoi_bbox.geojson")
    minx, miny, maxx, maxy = bbox.total_bounds

    with rasterio.open(DEM_URL) as src:
        win = window_from_bounds(minx, miny, maxx, maxy, transform=src.transform)
        dem = src.read(1, window=win).astype(np.float32)
        tr = src.window_transform(win)
        crs = src.crs
    print(f"DEM: {dem.shape[1]} x {dem.shape[0]} pixel (~30 m)")

    # Chiếu sang UTM để độ dốc tính được bằng mét (không thể tính dốc trên hệ độ)
    dst_tr, dw, dh = calculate_default_transform(
        crs, UTM, dem.shape[1], dem.shape[0], minx, miny, maxx, maxy, resolution=30)
    dem_utm = np.empty((dh, dw), np.float32)
    reproject(dem, dem_utm, src_transform=tr, src_crs=crs,
              dst_transform=dst_tr, dst_crs=UTM, resampling=Resampling.bilinear)

    gy, gx = np.gradient(dem_utm, 30.0, 30.0)
    slope = np.degrees(np.arctan(np.hypot(gx, gy)))
    aspect = (np.degrees(np.arctan2(-gx, gy)) + 360) % 360

    prof = dict(driver="GTiff", height=dh, width=dw, count=1, dtype="float32",
                crs=UTM, transform=dst_tr, compress="deflate")
    for nm, arr in (("dem", dem_utm), ("slope_deg", slope), ("aspect_deg", aspect)):
        with rasterio.open(f"{BASE}/data/out/rasters/{nm}.tif", "w", **prof) as d:
            d.write(arr, 1)

    aoi_u = aoi.to_crs(UTM)
    fig, ax = plt.subplots(1, 2, figsize=(11, 4.6), dpi=110)
    ext = [dst_tr.c, dst_tr.c + dw * 30, dst_tr.f - dh * 30, dst_tr.f]
    m0 = ax[0].imshow(dem_utm, extent=ext, cmap="terrain")
    ax[0].set_title("Cao độ (m)"); plt.colorbar(m0, ax=ax[0], fraction=0.046)
    m1 = ax[1].imshow(slope, extent=ext, cmap="magma", vmin=0, vmax=max(5, slope.max()))
    ax[1].set_title("Độ dốc (độ)"); plt.colorbar(m1, ax=ax[1], fraction=0.046)
    for a in ax:
        aoi_u.boundary.plot(ax=a, color="#0a84ff", lw=1.8)
        a.set_xticks([]); a.set_yticks([])
    fig.tight_layout(); fig.savefig(f"{BASE}/figs/terrain.png", dpi=110)

    from rasterio.features import geometry_mask
    mk = ~geometry_mask(aoi_u.geometry, out_shape=(dh, dw),
                        transform=dst_tr, invert=False)
    e, s = dem_utm[mk], slope[mk]
    stats = {"n_px": int(mk.sum()),
             "elev_min_m": float(e.min()), "elev_max_m": float(e.max()),
             "elev_mean_m": float(e.mean()),
             "slope_mean_deg": float(s.mean()), "slope_max_deg": float(s.max())}
    print("địa hình trong ranh giới:", json.dumps(stats, indent=2))
    return stats


def do_soil():
    props = ["phh2o", "soc", "clay", "sand", "silt", "cec", "nitrogen", "bdod"]
    # SoilGrids hay trả 503 khi quá tải -> thử lại có giãn cách.
    # Nếu vẫn hỏng mà file cũ còn đó thì giữ file cũ: dữ liệu đất là tĩnh,
    # truy vấn theo điểm, không đổi giữa các lần chạy.
    import time
    d = None
    for attempt in range(5):
        try:
            r = requests.get("https://rest.isric.org/soilgrids/v2.0/properties/query",
                             params=[("lon", LON), ("lat", LAT), ("value", "mean")]
                             + [("property", p) for p in props]
                             + [("depth", x) for x in
                                ["0-5cm", "5-15cm", "15-30cm", "30-60cm"]],
                             timeout=120)
            r.raise_for_status()
            d = r.json()
            break
        except requests.RequestException as e:
            wait = 5 * (attempt + 1)
            print(f"  SoilGrids lỗi ({e.__class__.__name__}), thử lại sau {wait}s "
                  f"[{attempt+1}/5]")
            time.sleep(wait)
    if d is None:
        old = f"{BASE}/data/out/soil_soilgrids.csv"
        if os.path.exists(old):
            print("  SoilGrids không truy cập được — GIỮ NGUYÊN file cũ:", old)
            return list(csv.DictReader(open(old)))
        raise RuntimeError("SoilGrids không truy cập được và chưa có dữ liệu cũ")
    rows = []
    for layer in d["properties"]["layers"]:
        name = layer["name"]
        unit = layer["unit_measure"]
        factor = unit["d_factor"]
        for dep in layer["depths"]:
            v = dep["values"].get("mean")
            rows.append({"property": name, "depth": dep["label"],
                         "value": None if v is None else round(v / factor, 3),
                         "unit": unit["mapped_units"].replace("*" + str(factor), "").strip(),
                         "target_unit": unit["target_units"]})
    out = f"{BASE}/data/out/soil_soilgrids.csv"
    with open(out, "w", newline="") as f:
        w = csv.DictWriter(f, fieldnames=["property", "depth", "value", "unit", "target_unit"])
        w.writeheader(); w.writerows(rows)
    print("\nthổ nhưỡng (SoilGrids, tầng 0-5cm):")
    for x in rows:
        if x["depth"] == "0-5cm":
            print(f"  {x['property']:9s} = {x['value']} {x['target_unit']}")
    print("đã ghi:", out)
    return rows


if __name__ == "__main__":
    os.makedirs(f"{BASE}/data/out/rasters", exist_ok=True)
    do_dem()
    do_soil()
