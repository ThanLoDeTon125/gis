"""Đọc nét vẽ VECTOR trong 'map mới.pdf' -> toạ độ pixel trên ảnh nền.

Chủ farm vạch 12 lô bằng công cụ vẽ, nên nét nằm trong PDF dưới dạng đường
vector chứ không bị nướng vào ảnh. Đọc thẳng vector cho toạ độ chính xác tuyệt
đối — hơn hẳn việc dò lại nét trắng trên ảnh raster (nét trắng còn lẫn với nhà
lưới, chữ nhãn Google).

Mỗi nét là một khối  q <a b c d e f> cm  ... m/l/c ...  S  Q  nên phải nhân
toạ độ đường với đúng ma trận cm của khối đó.
"""
import json
import os
import re

import numpy as np
from pypdf import PdfReader

BASE = os.path.expanduser("~/Documents/GIS_RiTi_TrangAn")
PDF = f"{BASE}/map mới.pdf"

NUM = r"[-+]?\.?\d[\d.]*(?:[eE][-+]?\d+)?"


def mat_mul(m, n):
    a, b, c, d, e, f = m
    A, B, C, D, E, F = n
    return (a * A + b * C, a * B + b * D,
            c * A + d * C, c * B + d * D,
            e * A + f * C + E, e * B + f * D + F)


def apply(m, x, y):
    a, b, c, d, e, f = m
    return (a * x + c * y + e, b * x + d * y + f)


def bezier(p0, p1, p2, p3, n=16):
    t = np.linspace(0, 1, n)[:, None]
    p0, p1, p2, p3 = (np.array(p, float) for p in (p0, p1, p2, p3))
    return ((1 - t) ** 3 * p0 + 3 * (1 - t) ** 2 * t * p1
            + 3 * (1 - t) * t ** 2 * p2 + t ** 3 * p3)[1:]


def parse(pdf_path=PDF):
    page = PdfReader(pdf_path).pages[0]
    content = page.get_contents().get_data().decode("latin-1")

    # Ảnh nền được đặt bằng khối  q <cm> ... /X4 Do Q  -> lấy ma trận đó làm gốc
    img = page["/Resources"]["/XObject"]["/X4"].get_object()
    IW, IH = int(img["/Width"]), int(img["/Height"])

    toks = content.replace("\n", " ").split()
    stack, ctm = [], (1, 0, 0, 1, 0, 0)
    img_ctm = None
    paths, cur, start = [], [], None
    ops = []

    i = 0
    while i < len(toks):
        t = toks[i]
        if t == "q":
            stack.append(ctm)
        elif t == "Q":
            ctm = stack.pop() if stack else (1, 0, 0, 1, 0, 0)
        elif t == "cm":
            m = tuple(float(x) for x in toks[i - 6:i])
            ctm = mat_mul(m, ctm)
        elif t == "m" and len(toks[i - 2:i]) == 2:
            if cur:
                paths.append((cur, ctm, None))
            p = apply(ctm, float(toks[i - 2]), float(toks[i - 1]))
            cur, start = [p], p
        elif t == "l" and cur:
            cur.append(apply(ctm, float(toks[i - 2]), float(toks[i - 1])))
        elif t == "c" and cur:
            v = [float(x) for x in toks[i - 6:i]]
            p1 = apply(ctm, v[0], v[1])
            p2 = apply(ctm, v[2], v[3])
            p3 = apply(ctm, v[4], v[5])
            cur.extend([tuple(p) for p in bezier(cur[-1], p1, p2, p3)])
        elif t == "v" and cur:
            v = [float(x) for x in toks[i - 4:i]]
            p2 = apply(ctm, v[0], v[1])
            p3 = apply(ctm, v[2], v[3])
            cur.extend([tuple(p) for p in bezier(cur[-1], cur[-1], p2, p3)])
        elif t == "y" and cur:
            v = [float(x) for x in toks[i - 4:i]]
            p1 = apply(ctm, v[0], v[1])
            p3 = apply(ctm, v[2], v[3])
            cur.extend([tuple(p) for p in bezier(cur[-1], p1, p3, p3)])
        elif t == "h" and cur and start:
            cur.append(start)
        elif t in ("S", "s", "f", "F", "f*", "B", "B*", "b", "b*", "n"):
            if cur:
                paths.append((cur, ctm, t))
                ops.append(t)
            cur, start = [], None
        elif t == "Do" and toks[i - 1] == "/X4":
            img_ctm = ctm
        i += 1
    if cur:
        paths.append((cur, ctm, None))

    if img_ctm is None:
        raise SystemExit("không tìm thấy khối vẽ ảnh nền /X4 Do")

    # Ảnh chiếm hình vuông đơn vị dưới img_ctm: pixel (px,py) -> u=px/IW, v=1-py/IH
    a, b, c, d, e, f = img_ctm
    inv_den = a * d - b * c

    def page_to_px(X, Y):
        """Nghịch đảo img_ctm rồi đổi hình vuông đơn vị -> pixel ảnh."""
        X, Y = X - e, Y - f
        u = (X * d - Y * c) / inv_den
        v = (-X * b + Y * a) / inv_den
        return u * IW, (1 - v) * IH

    out = []
    for pts, _, op in paths:
        if op in ("f", "F", "f*", "n", None):     # nét vẽ là stroke, không phải fill
            continue
        px = [page_to_px(x, y) for x, y in pts]
        if len(px) < 2:
            continue
        L = sum(np.hypot(px[k + 1][0] - px[k][0], px[k + 1][1] - px[k][1])
                for k in range(len(px) - 1))
        out.append({"pts": [[round(x, 2), round(y, 2)] for x, y in px],
                    "len_px": round(L, 1)})
    out.sort(key=lambda s: -s["len_px"])
    return {"image_size": [IW, IH], "strokes": out}


if __name__ == "__main__":
    r = parse()
    n = len(r["strokes"])
    tot = sum(s["len_px"] for s in r["strokes"])
    print(f"ảnh nền {r['image_size'][0]}x{r['image_size'][1]} px")
    print(f"{n} nét vẽ, tổng chiều dài {tot:,.0f} px")
    for s in r["strokes"][:8]:
        p0, p1 = s["pts"][0], s["pts"][-1]
        print(f"  dài {s['len_px']:7.1f} px  {len(s['pts']):3d} điểm  "
              f"({p0[0]:.0f},{p0[1]:.0f}) -> ({p1[0]:.0f},{p1[1]:.0f})")
    json.dump(r, open(f"{BASE}/data/out/pdf_strokes.json", "w"), indent=1)
    print("đã ghi: data/out/pdf_strokes.json")
