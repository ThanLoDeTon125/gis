"""Georeference một ảnh chụp Google Maps bất kỳ bằng NCC với ảnh nền Esri.

Tách khỏi extract_outline.py để dùng lại cho ảnh chụp SẠCH (không có nét vẽ).
Ảnh sạch cần thiết vì nét vẽ tay che mất chính cạnh ruộng mà ta muốn nắn vào:
ở ảnh có nét vẽ, dải ~8 px dọc ranh giới là màu sơn chứ không phải mặt đất.

    .venv/bin/python scripts/georef_image.py data/raw/screenshot_clean.png \
        data/out/georef_clean.json

Nguyên tắc giống bản gốc: lọc thông cao cả hai ảnh để bám CẠNH chứ không bám
màu (hai ảnh chụp khác mùa, màu ruộng lệch hoàn toàn), rồi quét dải tỉ lệ tìm
đỉnh tương quan.
"""
import json
import math
import os
import sys

import numpy as np
from PIL import Image
from scipy.ndimage import gaussian_filter
from skimage.feature import match_template
from skimage.transform import resize

BASE = os.path.expanduser("~/Documents/GIS_RiTi_TrangAn")
CROP = 0.08          # bỏ viền: minimap, nút zoom, nhãn chữ


def highpass(g, sigma=6.0):
    g = g.astype(np.float32)
    return g - gaussian_filter(g, sigma)


def merc_y(lat):
    return math.log(math.tan(math.pi / 4 + math.radians(lat) / 2))


def inv_merc_y(y):
    return math.degrees(2 * math.atan(math.exp(y)) - math.pi / 2)


def georeference(shot_path, mpp_lo=0.30, mpp_hi=0.80, step=0.02):
    meta = json.load(open(f"{BASE}/data/raw/basemap_meta.json"))
    esri = np.asarray(Image.open(
        f"{BASE}/data/raw/esri_basemap_z{meta['zoom']}.png").convert("L"))
    EH, EW = esri.shape
    mpp_e = meta["m_per_px_x"]

    rgb = np.asarray(Image.open(shot_path).convert("RGB")).astype(int)
    H, W = rgb.shape[:2]
    R, G, B = rgb[..., 0], rgb[..., 1], rgb[..., 2]
    red = (R > 170) & (R - G > 60) & (R - B > 60)   # ghim bản đồ (và nét vẽ nếu có)

    gray = np.asarray(Image.open(shot_path).convert("L")).astype(np.float32)
    gray[red] = np.median(gray)
    hp_shot_full = highpass(gray)
    y0, x0 = int(H * CROP), int(W * CROP)
    hp_shot = hp_shot_full[y0:H - y0, x0:W - x0]
    hp_esri = highpass(esri.astype(np.float32))
    print(f"ảnh {os.path.basename(shot_path)}: {W}x{H}, đỏ {red.sum()} px")

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

    print("quét thô:")
    best = None
    for mpp in np.arange(mpp_lo, mpp_hi + 1e-9, step):
        r = score(float(mpp))
        if r is None:
            continue
        print(f"  {r['mpp']:.3f} m/px  NCC={r['peak']:.4f}")
        if best is None or r["peak"] > best["peak"]:
            best = r

    print("quét tinh:")
    for span, st in ((step, step / 4), (step / 4, step / 20)):
        for mpp in np.arange(best["mpp"] - span, best["mpp"] + span + 1e-9, st):
            r = score(float(mpp))
            if r and r["peak"] > best["peak"]:
                best = r
        print(f"  -> {best['mpp']:.4f} m/px  NCC={best['peak']:.4f}")

    b = meta["bounds_lonlat"]
    out = {"shot": os.path.basename(shot_path),
           "m_per_px": best["mpp"], "ncc_peak": best["peak"],
           "esri_x": best["ex"], "esri_y": best["ey"], "scale": best["scale"],
           "crop_x": x0, "crop_y": y0,
           "shot_size": [W, H], "esri_size": [EW, EH],
           "esri_bounds": b, "esri_zoom": meta["zoom"]}

    # Kiểm chứng độc lập: ghim RiTi trong ảnh phải rơi đúng toạ độ từ URL Maps
    if red.sum() > 200:
        from scipy.ndimage import distance_transform_edt, label
        d = distance_transform_edt(red)
        lab, n = label(d > 4)          # khối đặc = thân ghim
        if n:
            sizes = np.bincount(lab.ravel())
            sizes[0] = 0
            pin = lab == sizes.argmax()
            ys, xs = np.nonzero(pin)
            px, py = float(xs.mean()), float(ys.max())   # chân ghim
            lon, lat = shot_to_lonlat(out, px, py)
            dlon = (lon - 105.854332) * 111320 * math.cos(math.radians(20.258))
            dlat = (lat - 20.2579952) * 110574
            err = math.hypot(dlon, dlat)
            print(f"kiểm chứng ghim RiTi: lệch {dlon:+.1f} m đông, "
                  f"{dlat:+.1f} m bắc (tổng {err:.1f} m)")
            out["pin_check_m"] = round(err, 2)
            out["pin_px"] = [px, py]
    return out


def shot_to_lonlat(g, px, py):
    b, (EW, EH) = g["esri_bounds"], g["esri_size"]
    my_top, my_bot = merc_y(b["north"]), merc_y(b["south"])
    mx = g["esri_x"] + (px - g["crop_x"]) * g["scale"]
    my = g["esri_y"] + (py - g["crop_y"]) * g["scale"]
    lon = b["west"] + (mx / EW) * (b["east"] - b["west"])
    lat = inv_merc_y(my_top + (my / EH) * (my_bot - my_top))
    return lon, lat


def lonlat_to_shot(g, lon, lat):
    b, (EW, EH) = g["esri_bounds"], g["esri_size"]
    my_top, my_bot = merc_y(b["north"]), merc_y(b["south"])
    mx = (lon - b["west"]) / (b["east"] - b["west"]) * EW
    my = (merc_y(lat) - my_top) / (my_bot - my_top) * EH
    return ((mx - g["esri_x"]) / g["scale"] + g["crop_x"],
            (my - g["esri_y"]) / g["scale"] + g["crop_y"])


if __name__ == "__main__":
    shot = sys.argv[1] if len(sys.argv) > 1 else f"{BASE}/data/raw/screenshot_clean.png"
    dest = sys.argv[2] if len(sys.argv) > 2 else f"{BASE}/data/out/georef_clean.json"
    g = georeference(shot if os.path.isabs(shot) else f"{BASE}/{shot}")
    dest = dest if os.path.isabs(dest) else f"{BASE}/{dest}"
    json.dump(g, open(dest, "w"), indent=2)
    print("đã ghi:", dest)
