"""Chuyển đường viền đỏ trên ảnh chụp màn hình thành polygon GIS thật.

Phép biến đổi pixel -> WGS84 được chốt bằng cách khớp mốc bất biến (ngã ba
đường, nhà, lùm cây) giữa ảnh chụp Google Maps và ảnh nền Esri có toạ độ chuẩn.
Xem georef_check.py để tái lập kiểm chứng.

Đầu ra:
  data/out/aoi_riti.geojson   - ranh giới vùng trồng (EPSG:4326)
  data/out/aoi_riti.gpkg      - bản GeoPackage (mở bằng QGIS)
  data/out/aoi_bbox.geojson   - khung bao, dùng để cắt ảnh vệ tinh
  figs/aoi_overlay.png        - ảnh kiểm chứng: polygon chồng lên ảnh nền
"""
import json
import os

import geopandas as gpd
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
from PIL import Image
from shapely.geometry import Polygon, box

BASE = os.path.expanduser("~/Documents/GIS_RiTi_TrangAn")

# --- Tham số georeference (chốt từ khớp mốc) ---------------------------------
PIN_LAT, PIN_LON = 20.2579952, 105.854332   # ghim RiTi, lấy từ URL Google Maps
M_PER_PX = 0.305                            # tỉ lệ ảnh chụp màn hình
PIN_X, PIN_Y = 1207.0, 441.0                # ghim nằm ở pixel nào trong ảnh chụp
SHOT_W, SHOT_H = 2000, 1338

# --- Đường viền đỏ, số hoá theo pixel ảnh chụp -------------------------------
# Đi theo chiều kim đồng hồ từ đỉnh phía bắc (ngã ba đường).
OUTLINE_PX = [
    (735, 60),                                    # đỉnh bắc - ngã ba đường
    (900, 150), (1050, 250), (1150, 330),         # cạnh đông bắc, bám đường
    (1205, 400), (1225, 432),                     # qua ghim RiTi
    (1350, 540), (1500, 645), (1600, 720),        # cạnh đông nam, bám đường
    (1668, 800),
    (1755, 795),                                  # mấu nhô ra phía đông
    (1740, 880), (1722, 965), (1700, 1050),       # cạnh đông, đi xuống
    (1660, 1140), (1630, 1210), (1612, 1245),     # góc đông nam
    (1450, 1247), (1300, 1232), (1150, 1205),     # cạnh nam, bám đường
    (1000, 1175), (850, 1145), (700, 1112),
    (560, 1075), (430, 1035), (330, 1000),
    (215, 940),                                   # góc tây nam
    (148, 878),                                   # góc tây
]

# Hệ số quy đổi độ <-> mét tại vĩ độ này
M_PER_DEG_LAT = 110574.0
M_PER_DEG_LON = 111320.0 * np.cos(np.radians(PIN_LAT))


def px_to_lonlat(x, y):
    """Pixel ảnh chụp (gốc trên-trái, trục y hướng xuống) -> (lon, lat)."""
    lon = PIN_LON + (x - PIN_X) * M_PER_PX / M_PER_DEG_LON
    lat = PIN_LAT - (y - PIN_Y) * M_PER_PX / M_PER_DEG_LAT
    return lon, lat


def main():
    os.makedirs(f"{BASE}/data/out", exist_ok=True)

    coords = [px_to_lonlat(x, y) for x, y in OUTLINE_PX]
    poly = Polygon(coords)
    if not poly.is_valid:
        poly = poly.buffer(0)

    gdf = gpd.GeoDataFrame(
        {"name": ["RiTi Organic Farm - vùng trồng khoanh"],
         "source": ["số hoá từ ảnh Google Maps, georeference bằng Esri World Imagery"]},
        geometry=[poly], crs="EPSG:4326")

    # Diện tích phải tính trên hệ chiếu mét, không tính trên độ.
    # Ninh Bình thuộc múi UTM 48N -> EPSG:32648.
    utm = gdf.to_crs("EPSG:32648")
    area_m2 = float(utm.area.iloc[0])
    perim_m = float(utm.length.iloc[0])
    gdf["area_ha"] = round(area_m2 / 10_000, 3)
    gdf["perimeter_m"] = round(perim_m, 1)

    gdf.to_file(f"{BASE}/data/out/aoi_riti.geojson", driver="GeoJSON")
    gdf.to_file(f"{BASE}/data/out/aoi_riti.gpkg", driver="GPKG", layer="aoi")

    # Khung bao nới thêm 150 m để cắt ảnh vệ tinh (chừa lề cho pixel biên)
    minx, miny, maxx, maxy = poly.bounds
    pad_lon = 150 / M_PER_DEG_LON
    pad_lat = 150 / M_PER_DEG_LAT
    bbox = box(minx - pad_lon, miny - pad_lat, maxx + pad_lon, maxy + pad_lat)
    gpd.GeoDataFrame({"name": ["AOI bbox +150m"]}, geometry=[bbox],
                     crs="EPSG:4326").to_file(
        f"{BASE}/data/out/aoi_bbox.geojson", driver="GeoJSON")

    # --- Ảnh kiểm chứng: polygon chồng lên ảnh nền Esri ----------------------
    meta = json.load(open(f"{BASE}/data/raw/basemap_meta.json"))
    mos = np.asarray(Image.open(f"{BASE}/data/raw/esri_basemap_z{meta['zoom']}.png"))
    b = meta["bounds_lonlat"]
    fig, ax = plt.subplots(figsize=(12, 9.6), dpi=110)
    ax.imshow(mos, extent=[b["west"], b["east"], b["south"], b["north"]])
    xs, ys = poly.exterior.xy
    ax.plot(xs, ys, color="#ff3b30", lw=2.4, label="Vùng trồng khoanh")
    ax.fill(xs, ys, color="#ff3b30", alpha=0.13)
    ax.plot(PIN_LON, PIN_LAT, marker="o", ms=9, mfc="#ffd60a", mec="black",
            mew=1.4, ls="none", label="Ghim RiTi Organic Farm")
    ax.set_xlim(minx - 0.0018, maxx + 0.0018)
    ax.set_ylim(miny - 0.0013, maxy + 0.0013)
    ax.set_xlabel("Kinh độ"); ax.set_ylabel("Vĩ độ")
    ax.set_title(f"Vùng trồng RiTi Organic Farm — {area_m2/10_000:.2f} ha\n"
                 f"nền: Esri World Imagery z18", fontsize=11)
    ax.legend(loc="lower left", fontsize=9)
    ax.ticklabel_format(useOffset=False, style="plain")
    fig.tight_layout()
    fig.savefig(f"{BASE}/figs/aoi_overlay.png", dpi=110)

    print(f"diện tích : {area_m2:,.0f} m² = {area_m2/10_000:.3f} ha")
    print(f"chu vi    : {perim_m:,.0f} m")
    print(f"bbox      : {minx:.6f},{miny:.6f} -> {maxx:.6f},{maxy:.6f}")
    print(f"kích thước: {(maxx-minx)*M_PER_DEG_LON:.0f} m ngang x "
          f"{(maxy-miny)*M_PER_DEG_LAT:.0f} m dọc")
    print("đã ghi: aoi_riti.geojson / .gpkg, aoi_bbox.geojson, figs/aoi_overlay.png")


if __name__ == "__main__":
    main()
