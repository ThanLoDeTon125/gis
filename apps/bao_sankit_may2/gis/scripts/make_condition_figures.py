"""Hình cho báo cáo tình trạng vùng trồng: nước, chu kỳ vụ, sức khoẻ theo lô.

Bổ sung cho make_lot_figures.py (bản đồ + chuỗi thô); ở đây là các hình ĐỌC
HIỆN TƯỢNG, nên mỗi hình phải trả lời đúng một câu hỏi:

  16  mỗi lô có mấy vụ, vụ rơi vào lúc nào?
  17  cả năm thừa hay thiếu nước, thiếu vào lúc nào?
  18  đất giữ ẩm ra sao theo tầng?
  19  lô nào xanh hơn/kém hơn mặt bằng chung, kém đều hay kém từng lúc?
  21  mùa khô so với mùa mưa, lô nào tụt sâu nhất?
  22  ẩm trong tán lá (NDMI) theo tháng — dấu hiệu thiếu nước sớm hơn NDVI
  23  hiện trạng cuối kỳ trên bản đồ
"""
import json
import os

import geopandas as gpd
import matplotlib
matplotlib.use("Agg")
import matplotlib.dates as mdates
import matplotlib.patheffects as pe
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
from matplotlib.colors import LinearSegmentedColormap, TwoSlopeNorm
from PIL import Image
from shapely.ops import polylabel

from georef_image import lonlat_to_shot
from make_lot_figures import BLUE, ORANGE, AQUA, INK, INK2, GRID, GREEN, SEQ, style

BASE = os.path.expanduser("~/Documents/GIS_RiTi_TrangAn")
IMG = f"{BASE}/images"
YELLOW, RED = "#eda100", "#e34948"
# Thang phân kỳ: hai cực ấm/lạnh + XÁM ở giữa. Giữa không được là một sắc màu,
# nếu không "không lệch gì" lại trông như một trạng thái riêng.
DIV = LinearSegmentedColormap.from_list(
    "div", ["#0d366b", "#2a78d6", "#9ec5f4", "#f0efec",
            "#f0a3a2", "#e34948", "#8f1f1e"])


def load():
    s2 = pd.read_csv(f"{BASE}/data/out/lot_s2_timeseries.csv", parse_dates=["date"])
    ck = pd.read_csv(f"{BASE}/data/out/lot_chu_ky.csv", parse_dates=["dinh", "day"])
    tt = pd.read_csv(f"{BASE}/data/out/lot_tinh_trang.csv", parse_dates=["ngay_cuoi"])
    cl = pd.read_csv(f"{BASE}/data/out/climate_daily.csv", parse_dates=["date"])
    sm = pd.read_csv(f"{BASE}/data/out/soil_moisture_daily.csv", parse_dates=["date"])
    nw = pd.read_csv(f"{BASE}/data/out/nuoc_theo_thang.csv")
    lots = gpd.read_file(f"{BASE}/data/out/lots.geojson").sort_values("lo")
    return s2, ck, tt, cl, sm, nw, lots


def gaps(s2, min_days=35):
    d = sorted(s2["date"].unique())
    return [(pd.Timestamp(d[i]), pd.Timestamp(d[i + 1]))
            for i in range(len(d) - 1)
            if (pd.Timestamp(d[i + 1]) - pd.Timestamp(d[i])).days > min_days]


# --- 16. chu kỳ vụ theo lô ------------------------------------------------
def fig_cycles(s2, ck, tt):
    gg = gaps(s2)
    fig, axes = plt.subplots(4, 3, figsize=(13, 11), dpi=130, sharex=True, sharey=True)
    for k, lid in enumerate(sorted(s2["lo_id"].unique())):
        ax = axes.ravel()[k]
        d = s2[s2["lo_id"] == lid].sort_values("date")
        for a, b in gg:      # vùng mù: không có ảnh quang học nào
            ax.axvspan(a, b, color="#f2f1ed", zorder=1)
        ax.plot(d["date"], d["ndvi"], color=BLUE, lw=1.5, zorder=3)
        ax.scatter(d["date"], d["ndvi"], s=13, color=BLUE, zorder=4,
                   edgecolor="w", lw=0.6)
        c = ck[ck["lo_id"] == lid]
        for _, r in c.iterrows():
            chac = r["tin_cay"] == "chắc"
            ax.scatter([r["dinh"]], [r["ndvi_dinh"]], s=74, marker="v",
                       color=ORANGE if chac else "#c9c8c3", zorder=5,
                       edgecolor="w", lw=0.9)
            ax.annotate("", xy=(r["dinh"], r["ndvi_dinh"]),
                        xytext=(r["day"], r["ndvi_day"]), zorder=2,
                        arrowprops=dict(arrowstyle="-", color=ORANGE if chac
                                        else "#c9c8c3", lw=1.1, alpha=0.75))
        style(ax)
        ax.set_ylim(0, 1)
        row = tt[tt["lo_id"] == lid].iloc[0]
        ax.set_title(f"{lid} · {row['area_ha']:.2f} ha · {int(row['so_vu'])} vụ "
                     f"({int(row['so_vu_chac'])} chắc)\n{row['trang_thai_cuoi_ky']}",
                     fontsize=8.6, loc="left", color=INK)
        ax.xaxis.set_major_locator(mdates.MonthLocator(interval=3))
        ax.xaxis.set_major_formatter(mdates.DateFormatter("%m/%y"))
    fig.suptitle("Chu kỳ canh tác từng lô — đỉnh NDVI là lúc tán phủ kín nhất trước khi thu\n"
                 "▼ cam = đỉnh vụ chắc · ▼ xám = cần kiểm chứng · nền xám = khoảng không có ảnh quang học",
                 fontsize=11, color=INK, x=0.007, ha="left", y=1.005)
    fig.tight_layout(rect=[0, 0, 1, 0.975])
    fig.savefig(f"{IMG}/16_chu_ky_canh_tac.png", dpi=130, bbox_inches="tight")
    plt.close(fig)


# --- 17. cân bằng nước ----------------------------------------------------
def fig_water(cl, nw):
    fig, ax = plt.subplots(2, 1, figsize=(12, 6.6), dpi=130, height_ratios=[1.25, 1])
    x = np.arange(len(nw))
    lab = [s[2:] for s in nw["ym"]]
    ax[0].bar(x - 0.2, nw["mua"], width=0.4, color=AQUA, label="Mưa")
    ax[0].bar(x + 0.2, nw["et0"], width=0.4, color=ORANGE, label="Bốc thoát hơi ET0")
    ax[0].set_xticks(x, lab, fontsize=8)
    style(ax[0], "mm/tháng",
          "Nước vào và nước ra theo tháng — cột cam cao hơn cột xanh là tháng thiếu nước")
    ax[0].legend(frameon=False, fontsize=9, labelcolor=INK2)

    cb = nw["can_bang"].values
    col = [AQUA if v >= 0 else RED for v in cb]
    ax[1].bar(x, cb, width=0.62, color=col)
    ax[1].axhline(0, color=INK2, lw=1)
    for i, v in enumerate(cb):
        if v < 0:
            ax[1].text(i, v - 12, f"{v:.0f}", ha="center", va="top",
                       fontsize=7.5, color=RED)
    ax[1].set_xticks(x, lab, fontsize=8)
    style(ax[1], "mm", "Cân bằng nước = mưa − ET0. Đỏ là tháng phải tưới bù.")
    fig.tight_layout()
    fig.savefig(f"{IMG}/17_can_bang_nuoc.png", dpi=130, bbox_inches="tight")
    plt.close(fig)


# --- 18. độ ẩm đất theo tầng ---------------------------------------------
def fig_soil(sm, cl):
    fig, ax = plt.subplots(2, 1, figsize=(12, 6.4), dpi=130, sharex=True,
                           height_ratios=[1.5, 1])
    for c, col, nm in (("sm_nong", BLUE, "tầng mặt 0–7 cm"),
                       ("sm_giua", ORANGE, "tầng giữa 7–28 cm"),
                       ("sm_sau", AQUA, "tầng sâu 28–100 cm")):
        ax[0].plot(sm["date"], sm[c].rolling(5, center=True).mean(),
                   color=col, lw=1.6, label=nm)
    style(ax[0], "m³ nước / m³ đất",
          "Độ ẩm đất theo tầng — tầng mặt phản ứng theo từng trận mưa, tầng sâu đổi chậm")
    ax[0].legend(frameon=False, fontsize=9, labelcolor=INK2, ncol=3)

    kho = (cl["precipitation_sum"] < 1).astype(int)
    run = kho * 0
    c = 0
    for i, v in enumerate(kho.values):
        c = c + 1 if v else 0
        run.iloc[i] = c
    ax[1].fill_between(cl["date"], run, color="#d9d8d3", step="mid")
    ax[1].plot(cl["date"], run, color=INK2, lw=0.9)
    i = int(np.argmax(run.values))
    ax[1].annotate(f"{int(run.max())} ngày liền không mưa",
                   xy=(cl["date"].iloc[i], run.max()),
                   xytext=(-10, -14), textcoords="offset points",
                   fontsize=8.5, color=INK, ha="right",
                   path_effects=[pe.withStroke(linewidth=2.5, foreground="w")])
    style(ax[1], "số ngày khô liên tiếp", "Chuỗi ngày không mưa (dưới 1 mm)")
    ax[1].xaxis.set_major_locator(mdates.MonthLocator())
    ax[1].xaxis.set_major_formatter(mdates.DateFormatter("%m/%y"))
    fig.tight_layout()
    fig.savefig(f"{IMG}/18_do_am_dat.png", dpi=130, bbox_inches="tight")
    plt.close(fig)


# --- 19. lệch so với mặt bằng farm ---------------------------------------
def fig_deviation(s2, tt):
    farm = s2.groupby("date")["ndvi"].mean().rename("farm")
    j = s2.join(farm, on="date")
    j["lech"] = j["ndvi"] - j["farm"]
    order = tt.sort_values("lech_tb")["lo_id"].tolist()
    fig, ax = plt.subplots(1, 2, figsize=(13, 5.2), dpi=130,
                           width_ratios=[1, 1.35])

    v = tt.set_index("lo_id").loc[order, "lech_tb"]
    col = [BLUE if x >= 0 else RED for x in v]
    ax[0].barh(np.arange(len(v)), v.values, color=col, height=0.66)
    ax[0].axvline(0, color=INK2, lw=1)
    ax[0].set_yticks(np.arange(len(v)), order, fontsize=8.5)
    for i, x in enumerate(v.values):
        ax[0].text(x + (0.006 if x >= 0 else -0.006), i, f"{x:+.3f}",
                   va="center", ha="left" if x >= 0 else "right",
                   fontsize=7.5, color=INK2)
    pad = float(np.abs(v.values).max()) * 0.35     # chỗ cho nhãn số ở hai đầu
    ax[0].set_xlim(v.values.min() - pad, v.values.max() + pad)
    style(ax[0], None, "Lệch NDVI trung bình so với mặt bằng farm")
    ax[0].set_xlabel("NDVI lệch", color=INK2, fontsize=9)

    p = j.pivot_table(index="lo_id", columns="date", values="lech").loc[order]
    lim = float(np.nanmax(np.abs(p.values)))
    # DIV đi từ lam (thấp) tới đỏ (cao); ở đây cần NGƯỢC LẠI để khớp cột bên
    # trái và khớp trực giác: lam = hơn mặt bằng, đỏ = kém mặt bằng.
    im = ax[1].imshow(p.values, aspect="auto", cmap=DIV.reversed(),
                      norm=TwoSlopeNorm(0, -lim, lim))
    ax[1].set_yticks(np.arange(len(p)), p.index, fontsize=8.5)
    step = max(1, len(p.columns) // 12)
    ax[1].set_xticks(np.arange(0, len(p.columns), step),
                     [pd.Timestamp(c).strftime("%d/%m/%y")
                      for c in p.columns[::step]], fontsize=7, rotation=45,
                     ha="right")
    ax[1].set_title("Lệch theo từng ngày — xanh là hơn mặt bằng, đỏ là kém",
                    fontsize=10.5, loc="left", color=INK)
    for s in ax[1].spines.values():
        s.set_visible(False)
    ax[1].tick_params(length=0, colors=INK2)
    cb = fig.colorbar(im, ax=ax[1], fraction=0.025, pad=0.01)
    cb.ax.tick_params(colors=INK2, labelsize=7)
    fig.tight_layout()
    fig.savefig(f"{IMG}/19_lech_so_voi_farm.png", dpi=130, bbox_inches="tight")
    plt.close(fig)


# --- 21. mùa khô vs mùa mưa ----------------------------------------------
def fig_season(tt):
    d = tt.sort_values("chenh_mua")
    y = np.arange(len(d))
    fig, ax = plt.subplots(figsize=(11, 5.6), dpi=130)
    for i, (_, r) in enumerate(d.iterrows()):
        ax.plot([r["ndvi_mua_kho"], r["ndvi_mua_mua"]], [i, i],
                color=GRID, lw=2.6, zorder=1, solid_capstyle="round")
    ax.scatter(d["ndvi_mua_kho"], y, s=64, color=ORANGE, zorder=3,
               edgecolor="w", lw=1.1, label="Mùa khô (11–4)")
    ax.scatter(d["ndvi_mua_mua"], y, s=64, color=BLUE, zorder=3,
               edgecolor="w", lw=1.1, label="Mùa mưa (5–10)")
    for i, (_, r) in enumerate(d.iterrows()):
        ax.text(max(r["ndvi_mua_kho"], r["ndvi_mua_mua"]) + 0.018, i,
                f"{r['chenh_mua']:+.2f}", va="center", fontsize=8, color=INK2)
    ax.set_yticks(y, [f"{r['lo_id']}  ({r['area_ha']:.2f} ha)"
                      for _, r in d.iterrows()], fontsize=9)
    style(ax, None, "NDVI mùa khô so với mùa mưa — số bên phải là mức chênh")
    ax.set_xlabel("NDVI trung bình", color=INK2, fontsize=9)
    ax.legend(frameon=False, fontsize=9, labelcolor=INK2, loc="lower right")
    fig.tight_layout()
    fig.savefig(f"{IMG}/21_mua_kho_mua_mua.png", dpi=130, bbox_inches="tight")
    plt.close(fig)


# --- 22. NDMI theo tháng --------------------------------------------------
def fig_ndmi(s2):
    d = s2.copy()
    d["thang"] = d["date"].dt.strftime("%m/%y")
    allm = pd.period_range(d["date"].min(), d["date"].max(), freq="M")
    cols = [f"{p.month:02d}/{str(p.year)[2:]}" for p in allm]
    p = d.pivot_table(index="lo_id", columns="thang", values="ndmi",
                      aggfunc="mean").reindex(columns=cols)
    fig, ax = plt.subplots(figsize=(13, 5), dpi=130)
    lim = float(np.nanmax(np.abs(p.values)))
    im = ax.imshow(p.values, aspect="auto", cmap=DIV.reversed(),
                   norm=TwoSlopeNorm(0, -lim, lim))
    ax.set_xticks(range(len(cols)), cols, fontsize=8, color=INK2)
    ax.set_yticks(range(len(p)), p.index, fontsize=8.5, color=INK2)
    for i in range(p.shape[0]):
        for j in range(p.shape[1]):
            v = p.values[i, j]
            if np.isfinite(v):
                ax.text(j, i, f"{v:+.2f}", ha="center", va="center", fontsize=6.4,
                        color="w" if abs(v) > lim * 0.55 else INK)
    ax.set_title("Ẩm trong tán lá NDMI theo tháng — âm là tán khô, dương là tán đủ nước",
                 fontsize=10.5, loc="left", color=INK)
    for s in ax.spines.values():
        s.set_visible(False)
    ax.tick_params(length=0)
    cb = fig.colorbar(im, ax=ax, fraction=0.02, pad=0.01)
    cb.set_label("NDMI", color=INK2, fontsize=8)
    cb.ax.tick_params(colors=INK2, labelsize=7)
    fig.tight_layout()
    fig.savefig(f"{IMG}/22_ndmi_theo_thang.png", dpi=130, bbox_inches="tight")
    plt.close(fig)


# --- 23. bản đồ hiện trạng cuối kỳ ---------------------------------------
def fig_status_map(lots, tt):
    g = json.load(open(f"{BASE}/data/out/georef_clean.json"))
    img = np.asarray(Image.open(f"{BASE}/data/raw/screenshot_clean.png").convert("RGB"))
    m = lots.merge(tt[["lo_id", "ndvi_cuoi", "ngay_cuoi", "xu_huong_thang",
                       "trang_thai_cuoi_ky"]], on="lo_id")
    FIG_W = 12.0
    fig, ax = plt.subplots(figsize=(FIG_W, 9), dpi=130)
    ax.imshow(img)
    halo = [pe.withStroke(linewidth=2.4, foreground="#00000090")]
    rings = [np.array([lonlat_to_shot(g, x, y)
                       for x, y in r.geometry.exterior.coords]) for _, r in m.iterrows()]
    xs = np.concatenate([r[:, 0] for r in rings])
    ys = np.concatenate([r[:, 1] for r in rings])
    ax.set_xlim(xs.min() - 60, xs.max() + 60)
    ax.set_ylim(ys.max() + 60, ys.min() - 60)
    ax.set_xticks([]); ax.set_yticks([])
    for (_, r), xy in zip(m.iterrows(), rings):
        c = GREEN(np.clip(r["ndvi_cuoi"], 0.15, 0.95))
        ax.fill(xy[:, 0], xy[:, 1], color=c, alpha=0.66, lw=0)
        ax.plot(xy[:, 0], xy[:, 1], color="w", lw=1.6)
        pt = polylabel(r.geometry, tolerance=1e-6)
        cx, cy = lonlat_to_shot(g, pt.x, pt.y)
        k = r["xu_huong_thang"]
        arr = "▲" if k >= 0.05 else ("▼" if k <= -0.05 else "▬")
        big = r["area_ha"] >= 0.5
        ax.text(cx, cy - (11 if big else 8), f"{int(r['lo'])}", ha="center",
                va="center", fontsize=16 if big else 12, weight="bold",
                color="w", path_effects=halo)
        ax.text(cx, cy + (7 if big else 5),
                f"NDVI {r['ndvi_cuoi']:.2f}\n{arr} {k:+.2f}/tháng", ha="center",
                va="top", fontsize=7.6 if big else 6.6, color="w",
                linespacing=1.3, path_effects=halo)
    sm_ = plt.cm.ScalarMappable(cmap=GREEN, norm=plt.Normalize(0.15, 0.95))
    cb = fig.colorbar(sm_, ax=ax, fraction=0.033, pad=0.01)
    cb.set_label("NDVI lần quan trắc cuối", color=INK2, fontsize=9)
    cb.ax.tick_params(colors=INK2, labelsize=8)
    ax.set_title(f"Hiện trạng ngày {m['ngay_cuoi'].max():%d/%m/%Y} — "
                 f"▲ đang lên xanh · ▬ ổn định · ▼ đang xuống",
                 color=INK, fontsize=12, loc="left")
    fig.savefig(f"{IMG}/23_hien_trang_cuoi_ky.png", dpi=130, bbox_inches="tight")
    plt.close(fig)


def main():
    s2, ck, tt, cl, sm, nw, lots = load()
    fig_cycles(s2, ck, tt);   print("  16_chu_ky_canh_tac.png")
    fig_water(cl, nw);        print("  17_can_bang_nuoc.png")
    fig_soil(sm, cl);         print("  18_do_am_dat.png")
    fig_deviation(s2, tt);    print("  19_lech_so_voi_farm.png")
    fig_season(tt);           print("  21_mua_kho_mua_mua.png")
    fig_ndmi(s2);             print("  22_ndmi_theo_thang.png")
    fig_status_map(lots, tt); print("  23_hien_trang_cuoi_ky.png")


if __name__ == "__main__":
    main()
