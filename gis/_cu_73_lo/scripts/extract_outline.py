"""Tách chính xác đường viền đỏ từ file ảnh chụp gốc + georeference tự động.

Hai cải tiến so với bản dựng tay trước đó:

1. GEOREFERENCE TỰ ĐỘNG thay vì ướm mốc bằng mắt. Quét dải tỉ lệ, mỗi tỉ lệ
   thu nhỏ ảnh chụp về đúng thang của ảnh nền Esri rồi tính tương quan chéo
   chuẩn hoá (NCC). Tỉ lệ + độ lệch nào cho đỉnh tương quan cao nhất là đáp án.
   Cả hai ảnh đều lọc thông cao trước, để bám vào CẠNH (đường, mái nhà) chứ
   không bám vào màu — hai ảnh chụp khác mùa nên màu ruộng lệch nhau hoàn toàn.

2. ĐƯỜNG VIỀN LẤY TỪ PIXEL, không dò bằng mắt. Ghim bản đồ cũng màu đỏ và dính
   vào nét vẽ, nên phải loại nó trước: ghim là khối đặc (khoảng cách tới nền
   >8 px) còn nét vẽ chỉ dày ~8 px, tách được bằng biến đổi khoảng cách.
"""
import json
import math
import os

import geopandas as gpd
import numpy as np
from PIL import Image
from scipy.ndimage import (binary_closing, binary_dilation, binary_fill_holes,
                           distance_transform_edt, gaussian_filter, label)
from shapely.geometry import Polygon, box
from skimage.feature import match_template
from skimage.measure import find_contours
from skimage.morphology import disk
from skimage.transform import resize

BASE = os.path.expanduser("~/Documents/GIS_RiTi_TrangAn")
SHOT = f"{BASE}/data/raw/screenshot.png"
CROP = 0.10          # bỏ 10% viền: chứa minimap, nút zoom, nhãn chữ
STROKE_HALF = 4      # nửa bề rộng nét vẽ (px), đo được từ biến đổi khoảng cách
PIN_THICK = 8        # ngưỡng dày để nhận diện ghim bản đồ


def highpass(g, sigma=6.0):
    """Giữ lại cạnh, bỏ nền sáng-tối. Hai ảnh khác mùa nên chỉ cạnh là chung."""
    g = g.astype(np.float32)
    return g - gaussian_filter(g, sigma)


def merc_y(lat):
    return math.log(math.tan(math.pi / 4 + math.radians(lat) / 2))


def inv_merc_y(y):
    return math.degrees(2 * math.atan(math.exp(y)) - math.pi / 2)


def main():
    meta = json.load(open(f"{BASE}/data/raw/basemap_meta.json"))
    esri = np.asarray(Image.open(
        f"{BASE}/data/raw/esri_basemap_z{meta['zoom']}.png").convert("L"))
    EH, EW = esri.shape
    mpp_e = meta["m_per_px_x"]

    shot_rgb = np.asarray(Image.open(SHOT).convert("RGB")).astype(int)
    H, W = shot_rgb.shape[:2]
    R, G, B = shot_rgb[..., 0], shot_rgb[..., 1], shot_rgb[..., 2]
    red = (R > 170) & (R - G > 60) & (R - B > 60)
    print(f"ảnh chụp {W}x{H}, pixel đỏ {red.sum()} ({100*red.mean():.2f}%)")

    # --- 1. Georeference tự động -------------------------------------------
    gray = np.asarray(Image.open(SHOT).convert("L")).astype(np.float32)
    gray[red] = np.median(gray)          # xoá nét vẽ để nó không lái tương quan
    hp_shot_full = highpass(gray)
    y0, x0 = int(H * CROP), int(W * CROP)
    hp_shot = hp_shot_full[y0:H - y0, x0:W - x0]
    hp_esri = highpass(esri.astype(np.float32))

    def score(mpp):
        s = mpp / mpp_e
        th, tw = int(round(hp_shot.shape[0] * s)), int(round(hp_shot.shape[1] * s))
        if th >= EH or tw >= EW or th < 40:
            return None
        tpl = resize(hp_shot, (th, tw), anti_aliasing=True, preserve_range=True)
        res = match_template(hp_esri, tpl.astype(np.float32))
        i = np.unravel_index(np.argmax(res), res.shape)
        return {"mpp": mpp, "peak": float(res[i]),
                "ey": int(i[0]), "ex": int(i[1]), "scale": s}

    print("\nquét thô dải tỉ lệ:")
    best = None
    for mpp in np.arange(0.24, 0.38001, 0.01):
        r = score(float(mpp))
        if r is None:
            continue
        print(f"  {r['mpp']:.3f} m/px  NCC={r['peak']:.4f}")
        if best is None or r["peak"] > best["peak"]:
            best = r

    print("\nquét tinh quanh đỉnh:")
    for mpp in np.arange(best["mpp"] - 0.010, best["mpp"] + 0.01001, 0.002):
        r = score(float(mpp))
        if r and r["peak"] > best["peak"]:
            best = r
    for mpp in np.arange(best["mpp"] - 0.002, best["mpp"] + 0.00201, 0.0005):
        r = score(float(mpp))
        if r and r["peak"] > best["peak"]:
            best = r
    print(f"  chốt {best['mpp']:.4f} m/px, NCC={best['peak']:.4f}")

    # Ảnh chụp (đã cắt viền) đặt tại (ex, ey) trong mosaic Esri, thu nhỏ scale lần
    # => pixel ảnh chụp (px,py) -> pixel mosaic
    s, ex, ey = best["scale"], best["ex"], best["ey"]

    def shot_to_esri(px, py):
        return ex + (px - x0) * s, ey + (py - y0) * s

    b = meta["bounds_lonlat"]
    my_top, my_bot = merc_y(b["north"]), merc_y(b["south"])

    def esri_to_lonlat(mx, my):
        lon = b["west"] + (mx / EW) * (b["east"] - b["west"])
        lat = inv_merc_y(my_top + (my / EH) * (my_bot - my_top))
        return lon, lat

    def shot_to_lonlat(px, py):
        return esri_to_lonlat(*shot_to_esri(px, py))

    # Kiểm chứng: ghim RiTi phải rơi đúng toạ độ đã biết từ URL Google Maps
    pin_px, pin_py = 1304.0, 470.0     # tâm chân ghim, đo từ vùng dày đã dò
    plon, plat = shot_to_lonlat(pin_px, pin_py)
    dlon = (plon - 105.854332) * 111320 * math.cos(math.radians(20.258))
    dlat = (plat - 20.2579952) * 110574
    print(f"\nkiểm chứng bằng ghim RiTi (nguồn độc lập, lấy từ URL Google Maps):")
    print(f"  suy ra  : {plat:.7f}, {plon:.7f}")
    print(f"  thực tế : 20.2579952, 105.8543320")
    print(f"  lệch    : {dlon:+.1f} m đông, {dlat:+.1f} m bắc "
          f"(tổng {math.hypot(dlon, dlat):.1f} m)")

    # --- 2. Tách đường viền -------------------------------------------------
    d = distance_transform_edt(red)
    pin = binary_dilation(d > PIN_THICK, disk(6))      # khối đặc = ghim bản đồ
    line = red & ~pin
    print(f"\nloại ghim bản đồ: {pin.sum()} px")

    # Hàn lại chỗ hổng do ghim để lại, rồi tô đặc phần trong
    closed = binary_closing(line, disk(22))
    filled = binary_fill_holes(closed)
    lab, n = label(filled)
    sizes = np.bincount(lab.ravel())
    sizes[0] = 0
    solid = lab == sizes.argmax()
    print(f"vùng khép kín lớn nhất: {solid.sum()} px ({n} thành phần)")

    # Co vào nửa bề rộng nét -> lấy TIM nét, không lấy mép ngoài
    core = distance_transform_edt(solid) > STROKE_HALF
    cs = find_contours(core.astype(float), 0.5)
    cont = max(cs, key=len)                             # (row, col)
    print(f"đường viền thô: {len(cont)} điểm")

    # Chỗ từng bị ghim che, phép hàn hình thái để lại một bướu giả. Bỏ hẳn các
    # điểm viền nằm trong vùng ghim và để cạnh nối thẳng qua — nét thật ở đoạn
    # này bị ghim che mất nên nối thẳng là suy luận trung thực nhất.
    scar = binary_dilation(pin, disk(8))
    rr = np.clip(cont[:, 0].astype(int), 0, scar.shape[0] - 1)
    cc = np.clip(cont[:, 1].astype(int), 0, scar.shape[1] - 1)
    keep = ~scar[rr, cc]
    print(f"bỏ {int((~keep).sum())} điểm nằm trong vùng ghim "
          f"(cạnh nối thẳng ~{2*math.sqrt(scar.sum()/math.pi)*best['mpp']:.0f} m)")
    cont = cont[keep]

    ring = [shot_to_lonlat(c, r) for r, c in cont]
    poly = Polygon(ring)
    if not poly.is_valid:
        poly = poly.buffer(0)

    utm = gpd.GeoSeries([poly], crs="EPSG:4326").to_crs("EPSG:32648")
    # Làm mượt ở mức 1.5 m: dưới sai số georeference nên không mất chi tiết thật
    simp = utm.simplify(1.5)
    poly_ll = simp.to_crs("EPSG:4326").iloc[0]
    area = float(simp.area.iloc[0])
    perim = float(simp.length.iloc[0])

    gdf = gpd.GeoDataFrame(
        {"name": ["RiTi Organic Farm — vùng trồng"],
         "area_ha": [round(area / 10_000, 4)],
         "perimeter_m": [round(perim, 1)],
         "method": ["tách tự động từ nét vẽ, georeference bằng NCC với Esri"],
         "georef_m_per_px": [round(best["mpp"], 5)],
         "georef_ncc": [round(best["peak"], 4)]},
        geometry=[poly_ll], crs="EPSG:4326")
    gdf.to_file(f"{BASE}/data/out/aoi_riti.geojson", driver="GeoJSON")
    gdf.to_file(f"{BASE}/data/out/aoi_riti.gpkg", driver="GPKG", layer="aoi")

    minx, miny, maxx, maxy = poly_ll.bounds
    pad_lon = 150 / (111320 * math.cos(math.radians(20.258)))
    pad_lat = 150 / 110574
    gpd.GeoDataFrame({"name": ["AOI bbox +150m"]},
                     geometry=[box(minx - pad_lon, miny - pad_lat,
                                   maxx + pad_lon, maxy + pad_lat)],
                     crs="EPSG:4326").to_file(
        f"{BASE}/data/out/aoi_bbox.geojson", driver="GeoJSON")

    json.dump({"m_per_px": best["mpp"], "ncc_peak": best["peak"],
               "esri_x": ex, "esri_y": ey, "scale": s,
               "crop_x": x0, "crop_y": y0,
               "shot_size": [W, H], "esri_size": [EW, EH],
               "esri_bounds": b, "esri_zoom": meta["zoom"]},
              open(f"{BASE}/data/out/georef.json", "w"), indent=2)

    print(f"\ndiện tích: {area:,.0f} m² = {area/10_000:.4f} ha")
    print(f"chu vi   : {perim:,.1f} m")
    print(f"số đỉnh  : {len(poly_ll.exterior.coords)}")
    print("đã ghi: aoi_riti.geojson/.gpkg, aoi_bbox.geojson, georef.json")


if __name__ == "__main__":
    main()
