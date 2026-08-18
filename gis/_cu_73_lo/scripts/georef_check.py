"""Kiểm chứng phép georeference ảnh chụp màn hình Google Maps.

Giả thiết: ảnh chụp hướng bắc, không xoay, tỉ lệ đều -> chỉ cần biết
(m/pixel) và toạ độ pixel của ghim RiTi là suy ra được lon/lat mọi pixel.

Script cắt đúng khung tương ứng từ ảnh nền Esri (đã có toạ độ chuẩn).
Nếu bố cục đường/nhà trùng với ảnh chụp -> tham số đúng.

Dùng: python georef_check.py [m_per_px] [pin_x] [pin_y]
"""
import json
import os
import sys

from PIL import Image

BASE = os.path.expanduser("~/Documents/GIS_RiTi_TrangAn")

# Kích thước ảnh chụp màn hình của người dùng (hệ pixel hiển thị)
SHOT_W, SHOT_H = 2000, 1338

# Tham số ước lượng từ việc khớp mốc; có thể tinh chỉnh qua argv
M_PER_PX = float(sys.argv[1]) if len(sys.argv) > 1 else 0.305
PIN_X = float(sys.argv[2]) if len(sys.argv) > 2 else 1210.0
PIN_Y = float(sys.argv[3]) if len(sys.argv) > 3 else 445.0


def main():
    meta = json.load(open(f"{BASE}/data/raw/basemap_meta.json"))
    mos = Image.open(f"{BASE}/data/raw/esri_basemap_z{meta['zoom']}.png")
    mx, my = meta["m_per_px_x"], meta["m_per_px_y"]
    px, py = meta["pin_px"]

    # Khoảng cách từ ghim tới 4 mép ảnh chụp, quy ra mét rồi quy ra pixel mosaic
    left_m, right_m = PIN_X * M_PER_PX, (SHOT_W - PIN_X) * M_PER_PX
    top_m, bot_m = PIN_Y * M_PER_PX, (SHOT_H - PIN_Y) * M_PER_PX

    box = (px - left_m / mx, py - top_m / my,
           px + right_m / mx, py + bot_m / my)
    print("crop box (mosaic px):", [round(v, 1) for v in box])
    print(f"vùng phủ: {(left_m + right_m):.0f} m ngang x {(top_m + bot_m):.0f} m dọc")

    crop = mos.crop(tuple(int(round(v)) for v in box)).resize(
        (SHOT_W, SHOT_H), Image.LANCZOS)
    out = f"{BASE}/figs/georef_candidate.png"
    crop.save(out)
    print("->", out)


if __name__ == "__main__":
    main()
