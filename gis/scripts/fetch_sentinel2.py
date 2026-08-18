"""Chuỗi ảnh Sentinel-2 12 THÁNG cho vùng trồng RiTi -> NDVI/NDMI/NDWI theo ngày.

Nguồn: STAC Element84 Earth Search -> COG trên AWS Open Data. Miễn phí, không key.

Khác bản cũ (1 tháng, 8 cảnh, 3 ngày dùng được): quét trọn 12 tháng ~88 lượt
bay để chuỗi đủ dày mà đọc mùa vụ.

Ba điểm mấu chốt:

  * ẢNH GỐC LÀ COG. rasterio chỉ tải đúng khối pixel trong khung AOI qua HTTP
    range request — vài trăm KB thay vì ~1 GB mỗi cảnh. Không có điều này thì
    88 cảnh là chuyện của vài ngày tải.

  * TỈ LỆ MÂY TRONG METADATA LÀ CỦA CẢ TILE 110 km, vô dụng với một mảnh 9 ha.
    Ta tự tính lại từ band SCL riêng trong ranh giới farm; cảnh "99% mây" vẫn
    có thể dùng nếu farm nằm đúng lỗ mây.

  * GIỮ CẢ CẢNH MÂY MỘT PHẦN. Mây hiếm khi phủ đều: có ngày lô 1 quang trong
    khi lô 7 bị che. Vì thế lưu luôn mặt nạ hợp lệ theo pixel, để bước tách
    theo lô tự quyết từng lô một, thay vì vứt cả ngày.
"""
import csv
import json
import os
from concurrent.futures import ThreadPoolExecutor

import geopandas as gpd
import numpy as np
import rasterio
from pystac_client import Client
from rasterio.enums import Resampling
from rasterio.features import geometry_mask
from rasterio.transform import from_bounds
from rasterio.windows import from_bounds as window_from_bounds

BASE = os.path.expanduser("~/Documents/GIS_RiTi_TrangAn")
STAC = "https://earth-search.aws.element84.com/v1"
UTM = "EPSG:32648"
RES = 10.0
DATE_RANGE = "2025-08-12/2026-08-12"
WORKERS = 6

SCL_BAD = {0, 1, 3, 8, 9, 10}   # nodata, bão hoà, bóng mây, mây vừa/cao, ti mây
BANDS = {"green": "green", "red": "red", "nir": "nir", "swir16": "swir16"}


def read_to_grid(href, bounds, shape, resampling):
    with rasterio.open(href) as src:
        win = window_from_bounds(*bounds, transform=src.transform)
        return src.read(1, window=win, out_shape=shape, resampling=resampling,
                        boundless=True, fill_value=0).astype(np.float32)


def main():
    os.makedirs(f"{BASE}/data/out/rasters/s2", exist_ok=True)

    aoi = gpd.read_file(f"{BASE}/data/out/aoi_riti.geojson").to_crs(UTM)
    bbox_ll = gpd.read_file(f"{BASE}/data/out/aoi_bbox.geojson")
    minx, miny, maxx, maxy = bbox_ll.to_crs(UTM).total_bounds
    minx, miny = np.floor(minx / RES) * RES, np.floor(miny / RES) * RES
    maxx, maxy = np.ceil(maxx / RES) * RES, np.ceil(maxy / RES) * RES
    W, H = int((maxx - minx) / RES), int((maxy - miny) / RES)
    bounds = (minx, miny, maxx, maxy)
    transform = from_bounds(*bounds, W, H)
    farm = ~geometry_mask(aoi.geometry, out_shape=(H, W), transform=transform,
                          invert=False)
    print(f"lưới {W}x{H} @ {RES:.0f} m; {farm.sum()} pixel trong farm "
          f"(~{farm.sum()*RES*RES/1e4:.2f} ha)")

    items = list(Client.open(STAC).search(
        collections=["sentinel-2-l2a"],
        intersects=json.loads(bbox_ll.to_json())["features"][0]["geometry"],
        datetime=DATE_RANGE).items())
    items.sort(key=lambda it: it.properties["datetime"])
    print(f"{len(items)} lượt bay trong {DATE_RANGE}\n")

    prof = dict(driver="GTiff", height=H, width=W, count=3, dtype="float32",
                crs=UTM, transform=transform, nodata=np.nan, compress="deflate")

    def one(it):
        day = it.properties["datetime"][:10]
        try:
            scl = read_to_grid(it.assets["scl"].href, bounds, (H, W),
                               Resampling.nearest).astype(np.int16)
            bad = np.isin(scl, list(SCL_BAD))
            valid = (~bad) & farm
            vpct = 100.0 * valid.sum() / max(farm.sum(), 1)
            if vpct < 1.0:                       # farm kín mây -> không tải band
                return {"date": day, "scene": it.id, "valid_pct": round(vpct, 1),
                        "cloud_tile_pct": round(it.properties.get("eo:cloud_cover", np.nan), 1)}

            off = 0.0 if it.properties.get("earthsearch:boa_offset_applied") else -1000.0
            b = {k: (read_to_grid(it.assets[a].href, bounds, (H, W),
                                  Resampling.bilinear) + off) * 1e-4
                 for k, a in BANDS.items()}
            eps = 1e-6
            ndvi = (b["nir"] - b["red"]) / (b["nir"] + b["red"] + eps)
            ndmi = (b["nir"] - b["swir16"]) / (b["nir"] + b["swir16"] + eps)
            ndwi = (b["green"] - b["nir"]) / (b["green"] + b["nir"] + eps)
            v = ndvi[valid]
            v = v[np.isfinite(v)]

            with rasterio.open(f"{BASE}/data/out/rasters/s2/s2_{day}.tif",
                               "w", **prof) as dst:
                dst.write(np.where(valid, ndvi, np.nan).astype(np.float32), 1)
                dst.write(np.where(valid, ndmi, np.nan).astype(np.float32), 2)
                dst.write(valid.astype(np.float32), 3)
                dst.descriptions = ("ndvi", "ndmi", "valid")
            return {"date": day, "scene": it.id, "valid_pct": round(vpct, 1),
                    "cloud_tile_pct": round(it.properties.get("eo:cloud_cover", np.nan), 1),
                    "ndvi_mean": round(float(v.mean()), 4) if v.size else None,
                    "ndvi_p90": round(float(np.percentile(v, 90)), 4) if v.size else None,
                    "ndmi_mean": round(float(np.nanmean(ndmi[valid])), 4) if v.size else None,
                    "ndwi_mean": round(float(np.nanmean(ndwi[valid])), 4) if v.size else None}
        except Exception as e:
            return {"date": day, "scene": it.id, "loi": f"{type(e).__name__}: {e}"[:120]}

    rows = []
    with ThreadPoolExecutor(WORKERS) as ex:
        for i, r in enumerate(ex.map(one, items), 1):
            rows.append(r)
            tag = ("LỖI " + r["loi"]) if "loi" in r else (
                f"quang {r['valid_pct']:5.1f}%  NDVI {r.get('ndvi_mean') or float('nan'):.3f}"
                if r.get("ndvi_mean") is not None else f"quang {r['valid_pct']:5.1f}%  (bỏ)")
            print(f"[{i:3d}/{len(items)}] {r['date']}  {tag}")

    rows.sort(key=lambda r: r["date"])
    keys = ["date", "scene", "cloud_tile_pct", "valid_pct", "ndvi_mean",
            "ndvi_p90", "ndmi_mean", "ndwi_mean", "loi"]
    with open(f"{BASE}/data/out/s2_scenes.csv", "w", newline="") as f:
        w = csv.DictWriter(f, fieldnames=keys, extrasaction="ignore")
        w.writeheader()
        w.writerows(rows)

    ok = [r for r in rows if r.get("ndvi_mean") is not None]
    good = [r for r in ok if r["valid_pct"] >= 70]
    print(f"\n{len(rows)} lượt bay -> {len(ok)} ngày có pixel quang "
          f"({len(good)} ngày quang >=70% farm)")
    print("đã ghi: data/out/s2_scenes.csv, data/out/rasters/s2/s2_*.tif")


if __name__ == "__main__":
    main()
