"""Nắn ranh giới 12 lô vẽ tay về mép ruộng/đường thật -> hiệu chỉnh diện tích.

Chủ farm vạch tương đối, nét lệch mép thật cỡ vài mét. Diện tích tính thẳng từ
nét vẽ vì thế mang sẵn sai số đó. Ở đây nắn nét về cạnh thật nhìn thấy trên ảnh
0,41 m/px rồi tính lại diện tích.

Cách làm: PHÂN THUỶ CÓ MẦM (seeded watershed) trên bản đồ độ dốc sáng của ảnh,
không nắn từng polygon riêng lẻ. Lý do là ranh giới giữa hai lô kề nhau phải
dịch CÙNG NHAU — nắn riêng từng lô sẽ đẻ ra khe hở và chồng lấn ở mọi cạnh chung.

  mầm     = mỗi lô co vào D px (và cả vùng ngoài farm co vào D px)
  dải trống = vành ±D px quanh mỗi nét vẽ, chính là biên độ cho phép dịch
  phân thuỷ = biên chạy về sống núi độ dốc (mép ruộng, mép đường) trong dải đó

Vì mầm giữ nguyên định danh lô, tô pô không đổi: không lô nào biến mất, không
sinh khe hở, tổng diện tích khép kín tuyệt đối.
"""
import json
import os

import geopandas as gpd
import numpy as np
from PIL import Image
from scipy.ndimage import binary_erosion, gaussian_filter
from shapely.geometry import Polygon
from skimage.filters import sobel
from skimage.measure import find_contours
from skimage.morphology import disk
from skimage.segmentation import watershed

from georef_image import shot_to_lonlat

BASE = os.path.expanduser("~/Documents/GIS_RiTi_TrangAn")
UTM = "EPSG:32648"
BAND_M = 5.0        # biên độ nắn tối đa, mét. Chủ farm vẽ lệch cỡ này.
SMOOTH = 1.6        # làm mượt trước khi lấy độ dốc: bỏ luống cây, giữ mép thửa
MODE_R = 4          # bán kính lọc mode để bỏ răng cưa của phân thuỷ (px)
SIMPLIFY_M = 1.0

# Vùng 0..11 trong lots_raw.geojson -> số lô chủ farm ghi trên bản vẽ.
# Đọc trực tiếp từ chữ số render trong PDF (xem figs/kiem_so_lo.png).
REGION_TO_LOT = {0: 7, 1: 1, 2: 12, 3: 2, 4: 3, 5: 9,
                 6: 11, 7: 5, 8: 10, 9: 6, 10: 8, 11: 4}


def main():
    g = json.load(open(f"{BASE}/data/out/georef_clean.json"))
    mpp = g["m_per_px"]
    D = max(3, int(round(BAND_M / mpp)))
    print(f"ảnh {mpp:.3f} m/px -> biên độ nắn D = {D} px (~{D*mpp:.1f} m)")

    raw = gpd.read_file(f"{BASE}/data/out/lots_raw.geojson")
    raw["lo"] = [REGION_TO_LOT[i] for i in range(len(raw))]

    img = np.asarray(Image.open(f"{BASE}/data/raw/screenshot_clean.png").convert("RGB"))
    H, W = img.shape[:2]

    # --- bản đồ cạnh -------------------------------------------------------
    grey = img.mean(axis=2).astype(np.float32)
    edge = sobel(gaussian_filter(grey, SMOOTH))
    # Cạnh thật (bờ ruộng, mép đường) là sống núi liên tục; chuẩn hoá theo
    # bách phân vị để một mái tôn chói không nuốt hết thang giá trị.
    edge = np.clip(edge / np.percentile(edge, 99), 0, 1)

    # --- nhãn gốc từ nét vẽ ------------------------------------------------
    from matplotlib.path import Path as MplPath
    from georef_image import lonlat_to_shot
    yy, xx = np.mgrid[0:H, 0:W]
    pts = np.column_stack([xx.ravel(), yy.ravel()])
    lab0 = np.zeros((H, W), np.int32)
    for i, geom in enumerate(raw.geometry):
        ring = np.array([lonlat_to_shot(g, x, y) for x, y in geom.exterior.coords])
        inside = MplPath(ring).contains_points(pts).reshape(H, W)
        lab0[inside & (lab0 == 0)] = i + 1

    # --- mầm ---------------------------------------------------------------
    markers = np.zeros((H, W), np.int32)
    for i in range(1, len(raw) + 1):
        m = lab0 == i
        for d in range(D, 1, -1):          # lô hẹp: co ít lại cho mầm không mất
            e = binary_erosion(m, disk(d))
            if e.sum() > 200:
                markers[e] = i
                if d < D:
                    print(f"  lô {REGION_TO_LOT[i-1]:2d}: hẹp, co {d} px thay vì {D}")
                break
    out = lab0 == 0
    markers[binary_erosion(out, disk(D))] = len(raw) + 1     # vùng ngoài farm
    markers[0, :] = markers[-1, :] = markers[:, 0] = markers[:, -1] = len(raw) + 1
    band = (markers == 0).sum()
    print(f"dải trống cho phép nắn: {band:,} px ({100*band/(H*W):.1f}% ảnh)")

    lab1 = watershed(edge, markers)

    # Phân thuỷ bám tới từng pixel nên biên răng cưa: một lô 0,2 ha ra chu vi
    # 357 m trong khi hình vuông cùng diện tích chỉ 180 m. Làm mượt trên BẢN ĐỒ
    # NHÃN (lọc mode) chứ không làm mượt từng polygon — mỗi pixel vẫn thuộc đúng
    # một lô nên phân hoạch khép kín tuyệt đối, không sinh khe hở hay chồng lấn.
    from skimage.filters.rank import modal
    for _ in range(2):
        lab1 = modal(lab1.astype(np.uint8), disk(MODE_R)).astype(np.int32)

    # --- vector hoá --------------------------------------------------------
    feats = []
    for i in range(1, len(raw) + 1):
        m = lab1 == i
        cont = max(find_contours(m.astype(float), 0.5), key=len)
        ring = [shot_to_lonlat(g, c, r) for r, c in cont]
        p = Polygon(ring)
        if not p.is_valid:
            p = p.buffer(0)
        feats.append({"lo": REGION_TO_LOT[i - 1], "geometry": p,
                      "px_before": int((lab0 == i).sum()), "px_after": int(m.sum())})

    gdf = gpd.GeoDataFrame(feats, crs="EPSG:4326").to_crs(UTM)
    gdf["geometry"] = gdf.simplify(SIMPLIFY_M)
    gdf["area_ha"] = (gdf.area / 10_000).round(4)
    gdf["perimeter_m"] = gdf.length.round(1)
    before = (raw.to_crs(UTM).area / 10_000).values
    gdf["area_ve_tay_ha"] = [round(before[i], 4) for i in range(len(gdf))]
    gdf["chenh_ha"] = (gdf["area_ha"] - gdf["area_ve_tay_ha"]).round(4)
    gdf["chenh_pct"] = (100 * gdf["chenh_ha"] / gdf["area_ve_tay_ha"]).round(1)
    gdf = gdf.sort_values("lo").reset_index(drop=True)
    gdf["lo_id"] = [f"L{int(v):02d}" for v in gdf["lo"]]

    cols = ["lo_id", "area_ve_tay_ha", "area_ha", "chenh_ha", "chenh_pct", "perimeter_m"]
    print("\n" + gdf[cols].to_string(index=False))
    print(f"\ntổng vẽ tay {gdf['area_ve_tay_ha'].sum():.3f} ha "
          f"-> sau nắn {gdf['area_ha'].sum():.3f} ha "
          f"({gdf['chenh_ha'].sum():+.3f} ha)")

    out_ll = gdf.to_crs("EPSG:4326")
    out_ll.to_file(f"{BASE}/data/out/lots.geojson", driver="GeoJSON")
    out_ll.to_file(f"{BASE}/data/out/aoi_riti.gpkg", driver="GPKG", layer="lots")
    out_ll[cols].to_csv(f"{BASE}/data/out/lots_area.csv", index=False)

    # Ranh giới farm = hợp của 12 lô
    farm = out_ll.to_crs(UTM).union_all().buffer(0.5).buffer(-0.5)
    fa = gpd.GeoDataFrame({"name": ["RiTi Organic Farm — 12 lô"],
                           "area_ha": [round(farm.area / 10_000, 4)],
                           "perimeter_m": [round(farm.length, 1)]},
                          geometry=[farm], crs=UTM).to_crs("EPSG:4326")
    fa.to_file(f"{BASE}/data/out/aoi_riti.geojson", driver="GeoJSON")
    fa.to_file(f"{BASE}/data/out/aoi_riti.gpkg", driver="GPKG", layer="aoi")
    print(f"ranh giới farm (hợp 12 lô): {farm.area/10_000:.4f} ha, "
          f"chu vi {farm.length:.0f} m")

    import math
    minx, miny, maxx, maxy = fa.total_bounds
    from shapely.geometry import box
    pad_lon = 150 / (111320 * math.cos(math.radians(20.258)))
    pad_lat = 150 / 110574
    gpd.GeoDataFrame({"name": ["AOI bbox +150m"]},
                     geometry=[box(minx - pad_lon, miny - pad_lat,
                                   maxx + pad_lon, maxy + pad_lat)],
                     crs="EPSG:4326").to_file(
        f"{BASE}/data/out/aoi_bbox.geojson", driver="GeoJSON")
    np.save(f"{BASE}/data/out/_lab_before.npy", lab0)
    np.save(f"{BASE}/data/out/_lab_after.npy", lab1)
    print("đã ghi: lots.geojson, lots_area.csv, aoi_riti.geojson/.gpkg, aoi_bbox.geojson")


if __name__ == "__main__":
    main()
