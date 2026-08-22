"""Bộ hình theo 12 lô: bản đồ, chuỗi NDVI từng lô, radar, mật độ dữ liệu.

Ba quy tắc trình bày được giữ nghiêm ở đây:

  * KHÔNG TRỤC KÉP. NDVI và lượng mưa là hai đại lượng khác thang; vẽ chung một
    khung với hai trục y là cách nhanh nhất để tạo ra một tương quan không có
    thật — dịch trục là đổi kết luận. Chúng nằm ở hai khung chồng nhau, dùng
    chung trục thời gian.

  * 12 LÔ THÌ KHÔNG TÔ 12 MÀU. Bảng màu định danh chỉ bảo đảm phân biệt được
    tới ~8 màu, và với người mù màu thì ít hơn. 12 lô vẽ thành 12 khung nhỏ,
    mỗi khung một chuỗi — so sánh bằng vị trí, không bằng màu.

  * THANG LIÊN TỤC THÌ MỘT SẮC, nhạt tới đậm. Cầu vồng tạo ra ranh giới giả ở
    chỗ đổi sắc, người đọc tưởng có ngưỡng trong khi số liệu chỉ tăng đều.
"""
import json
import os

import geopandas as gpd
import matplotlib
matplotlib.use("Agg")
import matplotlib.dates as mdates
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import matplotlib.patheffects as pe
from matplotlib.colors import LinearSegmentedColormap
from PIL import Image
from shapely.ops import polylabel

from georef_image import lonlat_to_shot

BASE = os.path.expanduser("~/Documents/GIS_RiTi_TrangAn")
IMG = f"{BASE}/images"

BLUE, ORANGE, AQUA = "#2a78d6", "#eb6834", "#1baf7a"
INK, INK2, GRID = "#0b0b0b", "#52514e", "#e4e3df"
SEQ = LinearSegmentedColormap.from_list(
    "blue1hue", ["#cde2fb", "#9ec5f4", "#6da7ec", "#3987e5",
                 "#256abf", "#184f95", "#0d366b"])
GREEN = LinearSegmentedColormap.from_list(
    "green1hue", ["#eef6ec", "#cfe8c6", "#a3d29a", "#6fb56d",
                  "#3d9648", "#1c7734", "#0a5423"])


def style(ax, ylab=None, title=None):
    ax.grid(True, color=GRID, lw=0.7)
    ax.set_axisbelow(True)
    for s in ("top", "right"):
        ax.spines[s].set_visible(False)
    for s in ("left", "bottom"):
        ax.spines[s].set_color(GRID)
    ax.tick_params(colors=INK2, labelsize=8)
    if ylab:
        ax.set_ylabel(ylab, color=INK2, fontsize=9)
    if title:
        ax.set_title(title, color=INK, fontsize=10.5, loc="left")


def load():
    lots = gpd.read_file(f"{BASE}/data/out/lots.geojson").sort_values("lo")
    s2 = pd.read_csv(f"{BASE}/data/out/lot_s2_timeseries.csv", parse_dates=["date"])
    p1 = f"{BASE}/data/out/lot_s1_timeseries.csv"
    s1 = pd.read_csv(p1, parse_dates=["date"]) if os.path.exists(p1) else None
    cl = pd.read_csv(f"{BASE}/data/out/climate_daily.csv", parse_dates=["date"])
    summ = pd.read_csv(f"{BASE}/data/out/lots_summary.csv")
    return lots, s2, s1, cl, summ


# --- 1. bản đồ 12 lô ------------------------------------------------------
def fig_map(lots, summ):
    g = json.load(open(f"{BASE}/data/out/georef_clean.json"))
    img = np.asarray(Image.open(f"{BASE}/data/raw/screenshot_clean.png").convert("RGB"))
    m = lots.merge(summ[["lo_id", "ndvi_tb", "so_ngay_s2"]], on="lo_id")

    FIG_W = 12.0
    fig, ax = plt.subplots(figsize=(FIG_W, 9), dpi=130)
    ax.imshow(img)
    vmin, vmax = m["ndvi_tb"].min(), m["ndvi_tb"].max()
    halo = [pe.withStroke(linewidth=2.4, foreground="#00000090")]

    rings = [np.array([lonlat_to_shot(g, x, y)
                       for x, y in r.geometry.exterior.coords]) for _, r in m.iterrows()]
    xs = np.concatenate([r[:, 0] for r in rings])
    ys = np.concatenate([r[:, 1] for r in rings])
    ax.set_xlim(xs.min() - 60, xs.max() + 60)
    ax.set_ylim(ys.max() + 60, ys.min() - 60)
    ax.set_xticks([]); ax.set_yticks([])
    # px ảnh trên mỗi inch giấy — cần để biết một nhãn dài bao nhiêu pixel ảnh,
    # từ đó mới so được với bề ngang thật của lô.
    px_per_inch = (xs.max() - xs.min() + 120) / (FIG_W * 0.95)

    for (_, r), xy in zip(m.iterrows(), rings):
        c = GREEN((r["ndvi_tb"] - vmin) / max(vmax - vmin, 1e-9) * 0.85 + 0.1)
        ax.fill(xy[:, 0], xy[:, 1], color=c, alpha=0.62, lw=0)
        ax.plot(xy[:, 0], xy[:, 1], color="w", lw=1.6)
        # Tâm hình học rơi ra ngoài với lô lõm; polylabel cho điểm nằm SÂU trong
        # lô, nhờ đó nhãn không đè lên cạnh hay tràn sang lô bên.
        pt = polylabel(r.geometry, tolerance=1e-6)
        cx, cy = lonlat_to_shot(g, pt.x, pt.y)
        big = r["area_ha"] >= 0.5
        fs = 8 if big else 6.8
        # Lô ở đây là dải dọc hẹp: nhãn một dòng thường rộng hơn cả lô và tràn
        # sang lô bên. So bề rộng chữ ước lượng với bề ngang lô tại chỗ đặt nhãn.
        one = f"{r['area_ha']:.2f} ha · NDVI {r['ndvi_tb']:.2f}"
        text_px = len(one) * fs * 0.55 / 72 * px_per_inch
        near = xy[np.abs(xy[:, 1] - cy) < 25]
        width_px = np.ptp(near[:, 0]) if len(near) > 2 else np.ptp(xy[:, 0])
        narrow = text_px > width_px * 0.95
        sub = f"{r['area_ha']:.2f} ha\nNDVI {r['ndvi_tb']:.2f}" if narrow else one
        dy = 11 if big else 8
        ax.text(cx, cy - dy, f"{int(r['lo'])}", ha="center", va="center",
                fontsize=16 if big else 12, weight="bold", color="w",
                path_effects=halo)
        ax.text(cx, cy + dy * 0.6, sub, ha="center", va="top",
                fontsize=fs, color="w", linespacing=1.3, path_effects=halo)
    sm = plt.cm.ScalarMappable(cmap=GREEN, norm=plt.Normalize(vmin, vmax))
    cb = fig.colorbar(sm, ax=ax, fraction=0.033, pad=0.01)
    cb.set_label("NDVI trung bình 12 tháng", color=INK2, fontsize=9)
    cb.ax.tick_params(colors=INK2, labelsize=8)
    ax.set_title(f"12 lô RiTi Organic Farm — tổng {m['area_ha'].sum():.2f} ha, "
                 f"ranh giới đã nắn về mép thật", color=INK, fontsize=12, loc="left")
    fig.savefig(f"{IMG}/10_ban_do_12_lo.png", dpi=130, bbox_inches="tight")
    plt.close(fig)


# --- 2. NDVI toàn farm + mưa, hai khung chồng -----------------------------
def fig_farm(s2, cl):
    farm = s2.groupby("date")["ndvi"].mean().reset_index()
    fig, ax = plt.subplots(2, 1, figsize=(12, 6.4), dpi=130, sharex=True,
                           height_ratios=[2, 1])
    ax[0].plot(farm["date"], farm["ndvi"], color=BLUE, lw=1.6, zorder=3)
    ax[0].scatter(farm["date"], farm["ndvi"], s=26, color=BLUE, zorder=4,
                  edgecolor="w", lw=0.8)
    style(ax[0], "NDVI trung bình 12 lô",
          f"NDVI toàn farm — {len(farm)} ngày quang trong 12 tháng")
    ax[0].set_ylim(0, 1)

    ax[1].bar(cl["date"], cl["precipitation_sum"], color=AQUA, width=1.0)
    style(ax[1], "Mưa ngày (mm)")
    ax[1].set_title(f"Lượng mưa — tổng {cl['precipitation_sum'].sum():,.0f} mm/năm",
                    color=INK, fontsize=10.5, loc="left")
    ax[1].xaxis.set_major_locator(mdates.MonthLocator())
    ax[1].xaxis.set_major_formatter(mdates.DateFormatter("%m/%y"))
    fig.tight_layout()
    fig.savefig(f"{IMG}/02_ndvi_va_mua_12_thang.png", dpi=130, bbox_inches="tight")
    plt.close(fig)


# --- 3. 12 khung nhỏ: chuỗi NDVI từng lô ----------------------------------
def fig_small_multiples(s2, summ):
    farm = s2.groupby("date")["ndvi"].mean()
    fig, axes = plt.subplots(4, 3, figsize=(13, 11), dpi=130, sharex=True, sharey=True)
    for k, (_, r) in enumerate(summ.sort_values("lo_id").iterrows()):
        ax = axes.ravel()[k]
        d = s2[s2["lo_id"] == r["lo_id"]].sort_values("date")
        ax.plot(farm.index, farm.values, color="#c9c8c3", lw=1.2, zorder=2)
        ax.plot(d["date"], d["ndvi"], color=BLUE, lw=1.5, zorder=3)
        ax.scatter(d["date"], d["ndvi"], s=13, color=BLUE, zorder=4,
                   edgecolor="w", lw=0.6)
        style(ax)
        ax.set_ylim(0, 1)
        ax.set_title(f"{r['lo_id']} · {r['area_ha']:.2f} ha · {int(r['so_ngay_s2'])} ngày"
                     f"\n{r['loai']}", fontsize=8.6, loc="left", color=INK)
        ax.xaxis.set_major_locator(mdates.MonthLocator(interval=3))
        ax.xaxis.set_major_formatter(mdates.DateFormatter("%m/%y"))
    axes[0, 0].text(0.02, 0.06, "xám = trung bình toàn farm", transform=axes[0, 0].transAxes,
                    fontsize=7.5, color=INK2)
    fig.suptitle("NDVI 12 tháng theo từng lô — trục dọc chung 0–1 để so sánh trực tiếp",
                 fontsize=12, color=INK, x=0.007, ha="left", y=0.997)
    fig.tight_layout(rect=[0, 0, 1, 0.985])
    fig.savefig(f"{IMG}/12_chuoi_ndvi_tung_lo.png", dpi=130, bbox_inches="tight")
    plt.close(fig)


# --- 4. bản đồ nhiệt lô × tháng -------------------------------------------
def fig_heat(s2, s1):
    # Trục tháng phải GIỐNG NHAU ở hai bảng và phải đủ 13 tháng, kể cả tháng
    # không có ảnh quang nào. Nếu để mỗi bảng tự sinh cột theo dữ liệu của nó
    # thì tháng 02/2026 biến mất khỏi bảng NDVI — đúng cái tháng cần cho thấy
    # là quang học mất trắng.
    allm = pd.period_range(s2["date"].min(), s2["date"].max(), freq="M")
    if s1 is not None:
        allm = pd.period_range(min(s2["date"].min(), s1["date"].min()),
                               max(s2["date"].max(), s1["date"].max()), freq="M")
    cols = [f"{p.month:02d}/{str(p.year)[2:]}" for p in allm]

    def heat(df, val, ax, title, cmap, unit):
        d = df.copy()
        d["thang"] = d["date"].dt.strftime("%m/%y")
        p = d.pivot_table(index="lo_id", columns="thang", values=val, aggfunc="mean")
        p = p.reindex(columns=cols)
        im = ax.imshow(p.values, aspect="auto", cmap=cmap)
        ax.set_xticks(range(len(cols)), cols, fontsize=8, color=INK2)
        ax.set_yticks(range(len(p)), p.index, fontsize=8, color=INK2)
        ax.set_title(title, fontsize=10.5, loc="left", color=INK)
        for s in ax.spines.values():
            s.set_visible(False)
        ax.tick_params(length=0)
        for i in range(p.shape[0]):
            for j in range(p.shape[1]):
                v = p.values[i, j]
                if np.isfinite(v):
                    lo, hi = np.nanmin(p.values), np.nanmax(p.values)
                    t = (v - lo) / max(hi - lo, 1e-9)
                    ax.text(j, i, f"{v:.2f}", ha="center", va="center", fontsize=6.4,
                            color="w" if t > 0.55 else INK)
        cb = ax.figure.colorbar(im, ax=ax, fraction=0.02, pad=0.01)
        cb.set_label(unit, color=INK2, fontsize=8)
        cb.ax.tick_params(colors=INK2, labelsize=7)

    n = 2 if s1 is not None else 1
    fig, axes = plt.subplots(n, 1, figsize=(13, 4.6 * n), dpi=130)
    axes = np.atleast_1d(axes)
    heat(s2, "ndvi", axes[0],
         "NDVI trung bình theo tháng — ô trắng là tháng không có ngày quang nào",
         GREEN, "NDVI")
    if s1 is not None:
        heat(s1, "vh_db", axes[1],
             "Radar Sentinel-1 VH (dB) theo tháng — xuyên mây nên KHÔNG có ô trống",
             SEQ, "VH (dB)")
    fig.tight_layout()
    fig.savefig(f"{IMG}/13_nhiet_do_lo_theo_thang.png", dpi=130, bbox_inches="tight")
    plt.close(fig)


# --- 5. radar toàn farm theo hướng bay ------------------------------------
def fig_radar(s1):
    if s1 is None:
        return
    fig, ax = plt.subplots(figsize=(12, 4.6), dpi=130)
    for orb, col, nm in (("asc", BLUE, "bay lên (ascending)"),
                         ("des", ORANGE, "bay xuống (descending)")):
        d = s1[s1["orbit"].str.startswith(orb)].groupby("date")["vh_db"].mean()
        if not len(d):
            continue
        ax.plot(d.index, d.values, color=col, lw=1.5, label=nm, zorder=3)
        ax.scatter(d.index, d.values, s=20, color=col, edgecolor="w", lw=0.7, zorder=4)
    style(ax, "VH (dB)",
          "Sentinel-1 VH toàn farm — hai hướng bay tách riêng, không trộn chung")
    ax.legend(frameon=False, fontsize=9, labelcolor=INK2)
    ax.xaxis.set_major_locator(mdates.MonthLocator())
    ax.xaxis.set_major_formatter(mdates.DateFormatter("%m/%y"))
    fig.tight_layout()
    fig.savefig(f"{IMG}/14_radar_sentinel1.png", dpi=130, bbox_inches="tight")
    plt.close(fig)


# --- 6. mật độ dữ liệu: quang học vs radar --------------------------------
def fig_density(s2, s1):
    lo = min([s2["date"].min()] + ([s1["date"].min()] if s1 is not None else []))
    hi = max([s2["date"].max()] + ([s1["date"].max()] if s1 is not None else []))
    idx = pd.period_range(lo, hi, freq="M")     # giữ cả tháng có 0 ngày quang
    a = s2.groupby(s2["date"].dt.to_period("M"))["date"].nunique().reindex(
        idx, fill_value=0)
    fig, ax = plt.subplots(figsize=(12, 4), dpi=130)
    x = np.arange(len(idx))
    ax.bar(x - 0.2, a.values, width=0.4, color=BLUE, label="Sentinel-2 quang học")
    for i, v in enumerate(a.values):
        if v == 0:
            ax.text(i - 0.2, 0.08, "0", ha="center", fontsize=8, color=INK2)
    if s1 is not None:
        b = s1.groupby(s1["date"].dt.to_period("M"))["date"].nunique().reindex(
            idx, fill_value=0)
        ax.bar(x + 0.2, b.values, width=0.4, color=ORANGE, label="Sentinel-1 radar")
    ax.set_xticks(x, [f"{p.month:02d}/{str(p.year)[2:]}" for p in idx], fontsize=8)
    style(ax, "Số ngày có dữ liệu",
          "Mật độ dữ liệu theo tháng — radar lấp đúng những tháng mưa mà ảnh quang học mất trắng")
    ax.legend(frameon=False, fontsize=9, labelcolor=INK2)
    fig.tight_layout()
    fig.savefig(f"{IMG}/15_mat_do_du_lieu.png", dpi=130, bbox_inches="tight")
    plt.close(fig)


def main():
    os.makedirs(IMG, exist_ok=True)
    lots, s2, s1, cl, summ = load()
    fig_map(lots, summ);            print("  10_ban_do_12_lo.png")
    fig_farm(s2, cl);               print("  02_ndvi_va_mua_12_thang.png")
    fig_small_multiples(s2, summ);  print("  12_chuoi_ndvi_tung_lo.png")
    fig_heat(s2, s1);               print("  13_nhiet_do_lo_theo_thang.png")
    fig_radar(s1);                  print("  14_radar_sentinel1.png")
    fig_density(s2, s1);            print("  15_mat_do_du_lieu.png")
    import shutil
    shutil.copy(f"{BASE}/figs/kiem_nan_lo.png", f"{IMG}/01_kiem_nan_ranh_gioi.png")
    print("  01_kiem_nan_ranh_gioi.png")


if __name__ == "__main__":
    main()
