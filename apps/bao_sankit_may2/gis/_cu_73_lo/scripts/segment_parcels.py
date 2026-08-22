"""Tách farm thành các lô nhỏ theo ranh giới thửa nhìn thấy trên ảnh.

Nguyên tắc thiết kế: HÌNH lấy từ ảnh phân giải cao, GIÁ TRỊ lấy từ ảnh đa phổ.

  - Ranh giới lô  <- ảnh chụp Google Maps 0,288 m/px. Bờ ruộng, lối đi, mép
    nhà lưới đều nhìn rõ. Sentinel-2 10 m thì một lô 0,2 ha chỉ vỏn vẹn 20
    pixel, không thể vẽ ranh giới từ đó.
  - NDVI theo lô  <- Sentinel-2, vì ảnh Google chỉ có RGB, không có cận hồng
    ngoại nên không tính được chỉ số thực vật.

Gộp vùng bằng RAG (Region Adjacency Graph): sau bước phân mảnh thô, hai mảnh
kề nhau có màu trung bình gần nhau sẽ nhập lại — nếu không một thửa bị bóng
cây cắt ngang sẽ vỡ thành nhiều lô giả.
"""
import json
import math
import os

import geopandas as gpd
import numpy as np
import rasterio
from PIL import Image
from rasterio.features import geometry_mask
from scipy.ndimage import binary_dilation, distance_transform_edt, median_filter
from shapely.geometry import Polygon
from skimage import graph
from skimage.measure import find_contours
from skimage.morphology import disk
from skimage.segmentation import felzenszwalb

BASE = os.path.expanduser("~/Documents/GIS_RiTi_TrangAn")
UTM = "EPSG:32648"
MIN_AREA_M2 = 250          # nhỏ hơn nữa thì không còn là "lô" mà là nhiễu
FZ_SCALE = 250             # càng lớn mảnh càng to
FZ_MIN_PX = 1200           # ~100 m² ở 0,288 m/px
# Ngưỡng gộp RAG tính theo khoảng cách màu, nên PHỤ THUỘC THANG GIÁ TRỊ của ảnh.
# Ảnh ở thang 0-255 -> ngưỡng cỡ đơn vị chục. Ở thang 0-1 thì ngưỡng phải nhỏ
# hơn 255 lần; đặt nhầm thang sẽ gộp toàn bộ farm thành một mảnh duy nhất.
#
# Tham số này có NGƯỠNG SỤP ĐỔ: dò thực nghiệm cho thấy tới 12 thì các lô trung
# tâm dính lại thành một khối chiếm quá nửa farm. Chọn 6 để lô lớn nhất giữ ở
# mức ~15% diện tích, tiêu chí quan trọng hơn tổng số lô.
RAG_THRESH = 6
IMG_SCALE = 255.0          # thang giá trị dùng cho cả felzenszwalb lẫn RAG


def merc_y(lat):
    return math.log(math.tan(math.pi / 4 + math.radians(lat) / 2))


def main():
    g = json.load(open(f"{BASE}/data/out/georef.json"))
    b, (EW, EH) = g["esri_bounds"], g["esri_size"]
    my_top, my_bot = merc_y(b["north"]), merc_y(b["south"])

    def shot_to_lonlat(px, py):
        mx = g["esri_x"] + (px - g["crop_x"]) * g["scale"]
        my = g["esri_y"] + (py - g["crop_y"]) * g["scale"]
        lon = b["west"] + (mx / EW) * (b["east"] - b["west"])
        lat = math.degrees(2 * math.atan(math.exp(
            my_top + (my / EH) * (my_bot - my_top))) - math.pi / 2)
        return lon, lat

    def lonlat_to_shot(lon, lat):
        mx = (lon - b["west"]) / (b["east"] - b["west"]) * EW
        my = (merc_y(lat) - my_top) / (my_bot - my_top) * EH
        return ((mx - g["esri_x"]) / g["scale"] + g["crop_x"],
                (my - g["esri_y"]) / g["scale"] + g["crop_y"])

    aoi = gpd.read_file(f"{BASE}/data/out/aoi_riti.geojson")
    poly = aoi.geometry.iloc[0]
    lons, lats = poly.exterior.xy
    sxy = np.array([lonlat_to_shot(x, y) for x, y in zip(lons, lats)])

    img = np.asarray(Image.open(f"{BASE}/data/raw/screenshot.png").convert("RGB"))
    x0, y0 = int(sxy[:, 0].min()) - 4, int(sxy[:, 1].min()) - 4
    x1, y1 = int(sxy[:, 0].max()) + 4, int(sxy[:, 1].max()) + 4
    sub = img[y0:y1, x0:x1].astype(float)
    print(f"cắt vùng farm khỏi ảnh chụp: {sub.shape[1]} x {sub.shape[0]} px")

    # Nét vẽ đỏ phải xoá, nếu không nó thành một "ranh giới" giả xuyên ảnh
    a = img[y0:y1, x0:x1].astype(int)
    red = (a[..., 0] > 170) & (a[..., 0] - a[..., 1] > 60) & (a[..., 0] - a[..., 2] > 60)
    redmask = binary_dilation(red, disk(3))
    for c in range(3):
        ch = sub[..., c]
        ch[redmask] = median_filter(ch, size=15)[redmask]
    print(f"xoá nét vẽ: {redmask.sum()} px, lấp bằng lọc trung vị")

    # Mặt nạ farm trong hệ pixel ảnh cắt
    from matplotlib.path import Path as MplPath
    yy, xx = np.mgrid[y0:y1, x0:x1]
    inside = MplPath(sxy).contains_points(
        np.column_stack([xx.ravel(), yy.ravel()])).reshape(xx.shape)
    print(f"pixel trong ranh giới: {inside.sum()}")

    seg = felzenszwalb(sub, scale=FZ_SCALE, sigma=0.9, min_size=FZ_MIN_PX)
    print(f"phân mảnh thô: {seg.max()+1} mảnh")
    rag = graph.rag_mean_color(sub, seg)
    seg = graph.cut_threshold(seg, rag, RAG_THRESH)
    print(f"sau khi gộp theo màu: {len(np.unique(seg))} mảnh")

    seg = np.where(inside, seg + 1, 0)

    # Bỏ mảnh vụn: gán chúng về mảnh lớn gần nhất
    mpp = g["m_per_px"]
    px_area = mpp * mpp
    for _ in range(3):
        ids, counts = np.unique(seg[seg > 0], return_counts=True)
        small = ids[counts * px_area < MIN_AREA_M2]
        if not len(small):
            break
        drop = np.isin(seg, small)
        seg[drop] = 0
        # lấp lỗ bằng nhãn của pixel hợp lệ gần nhất
        _, (iy, ix) = distance_transform_edt(
            (seg == 0) & inside, return_indices=True)
        seg = np.where((seg == 0) & inside, seg[iy, ix], seg)

    ids = [i for i in np.unique(seg) if i > 0]
    print(f"số lô sau khi dọn: {len(ids)}")

    # --- Vector hoá ---------------------------------------------------------
    feats = []
    for i in ids:
        m = (seg == i).astype(float)
        for cont in find_contours(m, 0.5):
            if len(cont) < 20:
                continue
            ring = [shot_to_lonlat(c + x0, r + y0) for r, c in cont]
            p = Polygon(ring)
            if not p.is_valid:
                p = p.buffer(0)
            if p.is_empty or p.geom_type != "Polygon":
                continue
            feats.append({"seg": int(i), "geometry": p})
    gdf = gpd.GeoDataFrame(feats, crs="EPSG:4326").dissolve(by="seg", as_index=False)
    gdf["geometry"] = gdf.intersection(poly)
    gdf = gdf[~gdf.is_empty]
    gdf = gdf.to_crs(UTM)
    gdf["geometry"] = gdf.simplify(1.2)
    gdf = gdf[gdf.area >= MIN_AREA_M2].reset_index(drop=True)
    gdf["area_ha"] = gdf.area / 10_000

    # --- Gắn NDVI Sentinel-2 cho từng lô ------------------------------------
    import glob
    import re
    ndvi_files = sorted(glob.glob(f"{BASE}/data/out/rasters/ndvi_*.tif"))
    dates = [re.search(r"ndvi_(\d{4}-\d\d-\d\d)", f).group(1) for f in ndvi_files]
    rasters, tr = [], None
    for f in ndvi_files:
        with rasterio.open(f) as src:
            rasters.append(src.read(1))
            tr, RH, RW = src.transform, src.height, src.width

    for d, arr in zip(dates, rasters):
        vals = []
        for geom in gdf.geometry:
            mk = ~geometry_mask([geom], out_shape=(RH, RW), transform=tr, invert=False)
            v = arr[mk]
            v = v[np.isfinite(v)]
            vals.append(round(float(v.mean()), 3) if v.size else None)
        gdf[f"ndvi_{d}"] = vals

    first, last = f"ndvi_{dates[0]}", f"ndvi_{dates[-1]}"
    gdf["ndvi_change"] = (gdf[last] - gdf[first]).round(3)

    def classify(r):
        lo, hi = r[first], r[last]
        if lo is None or hi is None or not np.isfinite(lo) or not np.isfinite(hi):
            return "không đủ dữ liệu (mây)"
        d = hi - lo
        if hi >= 0.75 and abs(d) < 0.10:
            return "Tán dày ổn định — cây lâu năm/vườn"
        if d >= 0.25:
            return "Bật xanh mạnh — mới gieo/tái sinh"
        if hi >= 0.55:
            return "Sinh trưởng đều"
        # Gộp "chậm" và "đất trống" làm một: bản đồ nền ảnh cần bảng màu định
        # danh qua được kiểm tra mọi-cặp, mà bảng chuẩn chỉ bảo đảm tới 4 màu.
        return "Che phủ thưa / đất trống, công trình"

    gdf["loai"] = gdf.apply(classify, axis=1)
    gdf = gdf.sort_values("area_ha", ascending=False).reset_index(drop=True)
    gdf.insert(0, "lo_id", [f"L{i+1:02d}" for i in range(len(gdf))])
    gdf["area_ha"] = gdf["area_ha"].round(4)

    out = gdf.to_crs("EPSG:4326")
    out.to_file(f"{BASE}/data/out/parcels.geojson", driver="GeoJSON")
    out.to_file(f"{BASE}/data/out/aoi_riti.gpkg", driver="GPKG", layer="parcels")
    cols = ["lo_id", "area_ha"] + [f"ndvi_{d}" for d in dates] + ["ndvi_change", "loai"]
    out[cols].to_csv(f"{BASE}/data/out/parcels.csv", index=False)

    farm_ha = gpd.GeoSeries([poly], crs=4326).to_crs(UTM).area.iloc[0] / 10_000
    print(f"\n{len(gdf)} lô, tổng {gdf['area_ha'].sum():.3f} ha "
          f"/ ranh giới farm {farm_ha:.3f} ha")
    print(out[cols].to_string(index=False))
    print("\nđã ghi: parcels.geojson, parcels.csv, lớp 'parcels' trong aoi_riti.gpkg")


if __name__ == "__main__":
    main()
