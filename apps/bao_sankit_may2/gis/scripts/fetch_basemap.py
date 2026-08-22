"""Tải ảnh vệ tinh Esri World Imagery (có toạ độ chuẩn) quanh RiTi Organic Farm.

Mục đích: làm ảnh tham chiếu để georeference ảnh chụp màn hình Google Maps
của người dùng (ảnh chụp màn hình không mang theo toạ độ).

Không cần API key. Ảnh nền lưu kèm bounds chính xác trong basemap_meta.json.
"""
import json
import math
import os
import sys
from concurrent.futures import ThreadPoolExecutor

import requests
from PIL import Image

# Ghim "RiTi Organic Farm | Tràng An" lấy từ URL Google Maps
PIN_LAT, PIN_LON = 20.2579952, 105.854332

# Khung cần phủ, tính bằng mét quanh ghim (ước lượng từ ảnh chụp màn hình)
M_WEST, M_EAST, M_NORTH, M_SOUTH = 700, 500, 350, 550

# z18 (~0.56 m/px) là mức chi tiết nhất Esri có cho khu vực này;
# z19+ trả về tile placeholder "Map data not yet available".
ZOOM = int(sys.argv[1]) if len(sys.argv) > 1 else 18
TILE = 256
URL = ("https://services.arcgisonline.com/ArcGIS/rest/services/"
       "World_Imagery/MapServer/tile/{z}/{y}/{x}")

OUT_DIR = os.path.expanduser("~/Documents/GIS_RiTi_TrangAn/data/raw")
FIG_DIR = os.path.expanduser("~/Documents/GIS_RiTi_TrangAn/figs")


def deg2num(lat, lon, z):
    """Toạ độ địa lý -> toạ độ tile (số thực) trong lưới Web Mercator."""
    n = 2.0 ** z
    x = (lon + 180.0) / 360.0 * n
    lat_rad = math.radians(lat)
    y = (1.0 - math.log(math.tan(lat_rad) + 1 / math.cos(lat_rad)) / math.pi) / 2.0 * n
    return x, y


def num2deg(x, y, z):
    """Nghịch đảo của deg2num."""
    n = 2.0 ** z
    lon = x / n * 360.0 - 180.0
    lat = math.degrees(math.atan(math.sinh(math.pi * (1 - 2 * y / n))))
    return lat, lon


def main():
    os.makedirs(OUT_DIR, exist_ok=True)
    os.makedirs(FIG_DIR, exist_ok=True)

    # Quy đổi mét -> độ tại vĩ độ này
    dlat = 1.0 / 110574.0
    dlon = 1.0 / (111320.0 * math.cos(math.radians(PIN_LAT)))
    north = PIN_LAT + M_NORTH * dlat
    south = PIN_LAT - M_SOUTH * dlat
    west = PIN_LON - M_WEST * dlon
    east = PIN_LON + M_EAST * dlon

    x0f, y0f = deg2num(north, west, ZOOM)
    x1f, y1f = deg2num(south, east, ZOOM)
    x0, y0 = int(math.floor(x0f)), int(math.floor(y0f))
    x1, y1 = int(math.floor(x1f)), int(math.floor(y1f))

    nx, ny = x1 - x0 + 1, y1 - y0 + 1
    print(f"zoom={ZOOM}  tiles={nx}x{ny}={nx * ny}")

    mosaic = Image.new("RGB", (nx * TILE, ny * TILE))
    sess = requests.Session()
    sess.headers["User-Agent"] = "Mozilla/5.0 (GIS survey; educational use)"

    def grab(args):
        ix, iy = args
        for attempt in range(3):
            try:
                r = sess.get(URL.format(z=ZOOM, x=x0 + ix, y=y0 + iy), timeout=30)
                if r.status_code == 200:
                    return ix, iy, r.content
            except requests.RequestException:
                pass
        return ix, iy, None

    jobs = [(ix, iy) for iy in range(ny) for ix in range(nx)]
    ok = 0
    with ThreadPoolExecutor(max_workers=8) as pool:
        for ix, iy, blob in pool.map(grab, jobs):
            if blob is None:
                continue
            import io
            mosaic.paste(Image.open(io.BytesIO(blob)).convert("RGB"),
                         (ix * TILE, iy * TILE))
            ok += 1
    print(f"tải được {ok}/{len(jobs)} tile")

    # Bounds chính xác của mosaic (mép ngoài của các tile biên)
    lat_top, lon_left = num2deg(x0, y0, ZOOM)
    lat_bot, lon_right = num2deg(x1 + 1, y1 + 1, ZOOM)

    path = os.path.join(OUT_DIR, f"esri_basemap_z{ZOOM}.png")
    mosaic.save(path)

    # Bản thu nhỏ để đối chiếu bằng mắt với ảnh chụp màn hình
    small = mosaic.copy()
    small.thumbnail((2000, 2000), Image.LANCZOS)
    small_path = os.path.join(FIG_DIR, "esri_reference.png")
    small.save(small_path)

    meta = {
        "source": "Esri World Imagery",
        "zoom": ZOOM,
        "size_px": [mosaic.width, mosaic.height],
        "bounds_lonlat": {"west": lon_left, "east": lon_right,
                          "south": lat_bot, "north": lat_top},
        "pin_lonlat": [PIN_LON, PIN_LAT],
        # Toạ độ pixel của ghim trong mosaic đầy đủ
        "pin_px": [(deg2num(PIN_LAT, PIN_LON, ZOOM)[0] - x0) * TILE,
                   (deg2num(PIN_LAT, PIN_LON, ZOOM)[1] - y0) * TILE],
        "thumb_size_px": [small.width, small.height],
    }
    meta["m_per_px_x"] = ((lon_right - lon_left) / mosaic.width) * 111320.0 * math.cos(math.radians(PIN_LAT))
    meta["m_per_px_y"] = ((lat_top - lat_bot) / mosaic.height) * 110574.0

    with open(os.path.join(OUT_DIR, "basemap_meta.json"), "w") as f:
        json.dump(meta, f, indent=2)
    print(json.dumps(meta, indent=2))
    print("mosaic ->", path)
    print("thumb  ->", small_path)


if __name__ == "__main__":
    main()
