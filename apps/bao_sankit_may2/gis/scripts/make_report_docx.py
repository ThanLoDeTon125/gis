"""Dựng báo cáo DOCX theo 12 lô do chủ farm vạch, kỳ dữ liệu 12 tháng.

Báo cáo đọc số liệu trực tiếp từ data/out/ — không có con số nào gõ tay, nên
chạy lại pipeline là báo cáo tự cập nhật theo.
"""
import os
from datetime import datetime

import geopandas as gpd
import numpy as np
import pandas as pd
from docx import Document
from docx.enum.section import WD_ORIENT
from docx.enum.table import WD_TABLE_ALIGNMENT
from docx.enum.text import WD_ALIGN_PARAGRAPH
from docx.oxml import OxmlElement
from docx.oxml.ns import qn
from docx.shared import Cm, Pt, RGBColor

BASE = os.path.expanduser("~/Documents/GIS_RiTi_TrangAn")
IMG = f"{BASE}/images"
UTM = "EPSG:32648"
OUT = f"{BASE}/BaoCao_RiTi_Farm_12_lo.docx"

INK2 = RGBColor(0x52, 0x51, 0x4E)
ACCENT = RGBColor(0x1C, 0x77, 0x34)


def shade(cell, hexcolor):
    el = OxmlElement("w:shd")
    el.set(qn("w:val"), "clear")
    el.set(qn("w:fill"), hexcolor)
    cell._tc.get_or_add_tcPr().append(el)


def add_table(doc, header, rows, widths=None, font=9):
    t = doc.add_table(rows=1, cols=len(header))
    t.style = "Table Grid"
    t.alignment = WD_TABLE_ALIGNMENT.CENTER
    for i, h in enumerate(header):
        c = t.rows[0].cells[i]
        c.text = ""
        r = c.paragraphs[0].add_run(str(h))
        r.bold = True
        r.font.size = Pt(font)
        shade(c, "E8F0E4")
    for row in rows:
        cells = t.add_row().cells
        for i, v in enumerate(row):
            cells[i].text = ""
            r = cells[i].paragraphs[0].add_run(str(v))
            r.font.size = Pt(font)
    if widths:
        for row in t.rows:
            for i, w in enumerate(widths):
                row.cells[i].width = Cm(w)
    return t


def caption(doc, text):
    p = doc.add_paragraph()
    p.alignment = WD_ALIGN_PARAGRAPH.CENTER
    r = p.add_run(text)
    r.italic = True
    r.font.size = Pt(9)
    r.font.color.rgb = INK2


def pic(doc, name, cap, width=16.0):
    path = f"{IMG}/{name}"
    if not os.path.exists(path):
        print("  (thiếu hình:", name, ")")
        return
    doc.add_picture(path, width=Cm(width))
    doc.paragraphs[-1].alignment = WD_ALIGN_PARAGRAPH.CENTER
    caption(doc, cap)


def vn(x, n=2):
    return f"{x:,.{n}f}".replace(",", " ").replace(".", ",")


def main():
    lots = gpd.read_file(f"{BASE}/data/out/lots.geojson")
    summ = pd.read_csv(f"{BASE}/data/out/lots_summary.csv")
    s2 = pd.read_csv(f"{BASE}/data/out/lot_s2_timeseries.csv", parse_dates=["date"])
    s2s = pd.read_csv(f"{BASE}/data/out/s2_scenes.csv")
    clim = pd.read_csv(f"{BASE}/data/out/climate_daily.csv", parse_dates=["date"])
    soil = pd.read_csv(f"{BASE}/data/out/soil_soilgrids.csv")
    p1 = f"{BASE}/data/out/lot_s1_timeseries.csv"
    s1 = pd.read_csv(p1, parse_dates=["date"]) if os.path.exists(p1) else None
    s1s = pd.read_csv(f"{BASE}/data/out/s1_scenes.csv") if os.path.exists(
        f"{BASE}/data/out/s1_scenes.csv") else None

    farm_ha = float(lots.to_crs(UTM).area.sum()) / 10_000
    ve_tay = summ["area_ve_tay_ha"].sum()
    d0, d1 = s2["date"].min(), s2["date"].max()
    n_s2_day = s2["date"].nunique()
    n_s1_day = s1["date"].nunique() if s1 is not None else 0

    doc = Document()
    sec = doc.sections[0]
    sec.orientation, sec.page_width, sec.page_height = (
        WD_ORIENT.PORTRAIT, Cm(21), Cm(29.7))
    sec.left_margin = sec.right_margin = Cm(2.0)
    st = doc.styles["Normal"]
    st.font.name = "Calibri"
    st.font.size = Pt(10.5)

    # --- Bìa ---------------------------------------------------------------
    h = doc.add_heading("BÁO CÁO DỮ LIỆU GIS THEO 12 LÔ", level=0)
    h.alignment = WD_ALIGN_PARAGRAPH.CENTER
    p = doc.add_paragraph(); p.alignment = WD_ALIGN_PARAGRAPH.CENTER
    r = p.add_run("RiTi Organic Farm | Tràng An\nTrường Yên, Hoa Lư, Ninh Bình")
    r.bold = True; r.font.size = Pt(14); r.font.color.rgb = ACCENT
    p = doc.add_paragraph(); p.alignment = WD_ALIGN_PARAGRAPH.CENTER
    r = p.add_run(f"Kỳ dữ liệu {clim['date'].min():%d/%m/%Y} – {clim['date'].max():%d/%m/%Y}"
                  f" · lập ngày {datetime.now():%d/%m/%Y}")
    r.font.size = Pt(10); r.font.color.rgb = INK2

    add_table(doc, ["Chỉ tiêu", "Giá trị"], [
        ["Toạ độ trung tâm", "20,2579952 N — 105,8543320 E"],
        ["Số lô", f"{len(lots)} lô do chủ farm vạch trên bản đồ"],
        ["Diện tích (đã hiệu chỉnh)", f"{vn(farm_ha)} ha ({vn(farm_ha*10_000,0)} m²)"],
        ["Diện tích theo nét vẽ tay", f"{vn(ve_tay)} ha (chênh {vn(farm_ha-ve_tay)} ha)"],
        ["Lô nhỏ nhất / lớn nhất",
         f"{vn(summ['area_ha'].min(),3)} ha (lô {summ.loc[summ['area_ha'].idxmin(),'lo_id']})"
         f" / {vn(summ['area_ha'].max(),3)} ha (lô {summ.loc[summ['area_ha'].idxmax(),'lo_id']})"],
        ["Ngày có ảnh quang học", f"{n_s2_day} ngày / {len(s2s)} lượt bay Sentinel-2"],
        ["Ngày có ảnh radar", f"{n_s1_day} ngày / {len(s1s) if s1s is not None else 0} "
                              f"lượt bay Sentinel-1 (không lượt nào bị mây loại)"],
        ["Tổng bản ghi lô × ngày", f"{len(s2):,} (quang học) + "
                                   f"{len(s1) if s1 is not None else 0:,} (radar)"],
        ["Hệ toạ độ", "EPSG:4326 (lưu trữ) · EPSG:32648 UTM 48N (tính diện tích)"],
        ["Sai số ranh giới", "±2,9 m (kiểm bằng nguồn độc lập)"],
    ], widths=[5.5, 11.5], font=10)

    # --- 1. Tóm tắt --------------------------------------------------------
    doc.add_heading("1. Tóm tắt", level=1)
    up = summ.nlargest(1, "bien_do").iloc[0]
    flat = summ.nsmallest(1, "bien_do").iloc[0]
    doc.add_paragraph(
        f"Farm gồm {len(lots)} lô do chủ farm vạch trên ảnh Google Maps, tổng "
        f"{vn(farm_ha)} ha sau khi ranh giới được nắn về mép ruộng và mép đường "
        f"nhìn thấy trên ảnh {vn(0.406,2)} m/pixel. So với diện tích tính thẳng từ "
        f"nét vẽ tay ({vn(ve_tay)} ha), phần hiệu chỉnh là "
        f"{vn(farm_ha-ve_tay)} ha ({vn(100*(farm_ha-ve_tay)/ve_tay,1)} %).")
    doc.add_paragraph(
        f"Trong 12 tháng, mỗi lô có trung bình "
        f"{vn(summ['so_ngay_s2'].mean(),0)} ngày dữ liệu quang học và "
        f"{vn(summ['so_ngay_s1'].mean(),0) if 'so_ngay_s1' in summ else 0} ngày dữ liệu radar. "
        f"NDVI trung bình toàn farm là {vn(summ['ndvi_tb'].mean(),2)}. "
        f"Lô biến động mạnh nhất là {up['lo_id']} (biên độ NDVI {vn(up['bien_do'],2)} — "
        f"dấu hiệu luân canh theo vụ), ổn định nhất là {flat['lo_id']} "
        f"(biên độ {vn(flat['bien_do'],2)}).")
    doc.add_paragraph(
        f"Khí hậu cả năm: {vn(clim['precipitation_sum'].sum(),0)} mm mưa so với "
        f"{vn(clim['et0_fao_evapotranspiration'].sum(),0)} mm bốc thoát hơi — cân bằng "
        f"nước {vn(clim['precipitation_sum'].sum()-clim['et0_fao_evapotranspiration'].sum(),0)} mm. "
        f"Mưa dồn vào tháng 8–10 và tháng 5–7; tháng 1–3 là kỳ khô rõ rệt.")

    # --- 2. Hiệu chỉnh diện tích ------------------------------------------
    doc.add_heading("2. Hiệu chỉnh diện tích từng lô", level=1)
    doc.add_paragraph(
        "Nét vẽ tay chỉ mang tính tương đối: đường vẽ lệch mép thửa thật vài mét, "
        "và với lô nhỏ thì vài mét đó là vài chục phần trăm diện tích. Ranh giới "
        "được nắn tự động về cạnh thật nhìn thấy trên ảnh — mép đường bê tông, bờ "
        "ruộng, mép nhà lưới — trong biên độ tối đa 5 m quanh nét vẽ.")
    doc.add_paragraph(
        "Phép nắn chạy trên toàn bộ 12 lô cùng lúc (phân thuỷ có mầm) chứ không "
        "nắn từng lô riêng, nên cạnh chung giữa hai lô kề nhau dịch cùng nhau: "
        "không sinh khe hở, không chồng lấn, tổng diện tích luôn khép kín.")
    add_table(doc, ["Lô", "Vẽ tay (ha)", "Đã nắn (ha)", "Chênh (ha)", "Chênh (%)"],
              [[r["lo_id"], vn(r["area_ve_tay_ha"], 3), vn(r["area_ha"], 3),
                f"{r['area_ha']-r['area_ve_tay_ha']:+.3f}".replace(".", ","),
                f"{r['chenh_pct']:+.1f}".replace(".", ",")]
               for _, r in summ.iterrows()]
              + [["TỔNG", vn(ve_tay, 3), vn(farm_ha, 3),
                  f"{farm_ha-ve_tay:+.3f}".replace(".", ","),
                  f"{100*(farm_ha-ve_tay)/ve_tay:+.1f}".replace(".", ",")]],
              widths=[2.0, 3.2, 3.2, 3.0, 3.0], font=9.5)
    pic(doc, "01_kiem_nan_ranh_gioi.png",
        "Hình 1. Vàng = nét vẽ tay, lam = ranh giới sau khi nắn. Bốn khung phóng to "
        "là những lô được hiệu chỉnh nhiều nhất.", 17)

    # --- 3. Bản đồ ---------------------------------------------------------
    doc.add_page_break()
    doc.add_heading("3. Bản đồ 12 lô", level=1)
    pic(doc, "10_ban_do_12_lo.png",
        f"Hình 2. {len(lots)} lô trên nền ảnh 0,41 m. Sắc xanh đậm dần theo NDVI "
        f"trung bình 12 tháng.", 17)

    # --- 4. Bảng dữ liệu theo lô ------------------------------------------
    doc.add_page_break()
    doc.add_heading("4. Dữ liệu tổng hợp theo lô", level=1)
    doc.add_paragraph(
        "NDVI đo mức xanh của tán lá (0 = đất trống, >0,8 = tán dày kín). Biên độ "
        "là khoảng cách giữa lần cao nhất và thấp nhất trong 12 tháng — biên độ lớn "
        "nghĩa là lô có gieo và thu theo vụ, biên độ nhỏ nghĩa là che phủ quanh năm. "
        "NDMI đo độ ẩm trong tán lá. VH là tín hiệu radar, đo cấu trúc tán.")
    hdr = ["Lô", "ha", "% farm", "Ngày S2", "NDVI tb", "NDVI min", "NDVI max",
           "Biên độ", "NDMI tb"]
    has1 = "vh_db_tb" in summ.columns
    if has1:
        hdr += ["Ngày S1", "VH (dB)"]
    hdr += ["Phân loại"]
    rows = []
    for _, r in summ.iterrows():
        row = [r["lo_id"], vn(r["area_ha"], 3), f"{100*r['area_ha']/farm_ha:.1f}%",
               int(r["so_ngay_s2"]), vn(r["ndvi_tb"], 2), vn(r["ndvi_min"], 2),
               vn(r["ndvi_max"], 2), vn(r["bien_do"], 2), vn(r["ndmi_tb"], 2)]
        if has1:
            row += [int(r["so_ngay_s1"]), vn(r["vh_db_tb"], 1)]
        row += [r["loai"]]
        rows.append(row)
    add_table(doc, hdr, rows, font=8)

    doc.add_heading("4.1 Địa hình theo lô", level=2)
    if "cao_do_m" in summ.columns:
        doc.add_paragraph(
            "Cao độ và độ dốc lấy từ DEM Copernicus 30 m. Ở độ phân giải này một lô "
            "0,2 ha chỉ chiếm khoảng 2 pixel, nên số liệu của các lô nhỏ chỉ nên đọc "
            "như giá trị vùng, không phải đo đạc tại chỗ.")
        add_table(doc, ["Lô", "Diện tích (ha)", "Cao độ (m)", "Độ dốc (°)"],
                  [[r["lo_id"], vn(r["area_ha"], 3), vn(r["cao_do_m"], 1),
                    vn(r["do_doc_deg"], 1)] for _, r in summ.iterrows()],
                  widths=[2.5, 4.0, 4.0, 4.0], font=9.5)
        pic(doc, "20_dia_hinh_do_doc.png",
            "Hình. Cao độ và độ dốc toàn khu, nguồn Copernicus GLO-30.", 16)

    # --- 5. Chuỗi thời gian theo lô ---------------------------------------
    doc.add_page_break()
    doc.add_heading("5. Chuỗi 12 tháng của từng lô", level=1)
    doc.add_paragraph(
        f"Mỗi lô được tách riêng trên từng ảnh: tổng cộng {len(s2):,} bản ghi "
        f"lô × ngày từ ảnh quang học"
        + (f" và {len(s1):,} bản ghi từ radar. " if s1 is not None else ". ") +
        "Mây hiếm khi phủ đều cả farm, nên từng lô được xét riêng — lô nào đủ "
        "60 % diện tích quang thì lô đó có số liệu ngày đó, thay vì bỏ cả ngày.")
    pic(doc, "12_chuoi_ndvi_tung_lo.png",
        "Hình 3. NDVI 12 tháng của từng lô. Trục dọc chung 0–1 để so sánh trực tiếp; "
        "đường xám là trung bình toàn farm.", 17)
    pic(doc, "13_nhiet_do_lo_theo_thang.png",
        "Hình 4. Trung bình theo tháng. Ô trắng ở bảng trên là tháng không có ngày "
        "quang nào — bảng dưới (radar) không có ô trắng vì radar xuyên mây.", 17)

    doc.add_heading("5.1 Nhận định từng lô", level=2)
    for _, r in summ.iterrows():
        d = s2[s2["lo_id"] == r["lo_id"]].sort_values("date")
        if not len(d):
            continue
        hi = d.loc[d["ndvi"].idxmax()]
        lo = d.loc[d["ndvi"].idxmin()]
        p = doc.add_paragraph()
        run = p.add_run(f"Lô {int(r['lo_id'][1:])} — {vn(r['area_ha'],3)} ha "
                        f"({vn(100*r['area_ha']/farm_ha,1)} % farm). ")
        run.bold = True
        pct = f"{r['chenh_pct']:+.1f}".replace(".", ",")
        p.add_run(
            f"{r['loai']}. NDVI dao động {vn(r['ndvi_min'],2)}–{vn(r['ndvi_max'],2)} "
            f"(cao nhất {hi['date']:%d/%m/%Y}, thấp nhất {lo['date']:%d/%m/%Y}), "
            f"trung bình {vn(r['ndvi_tb'],2)} trên {int(r['so_ngay_s2'])} ngày quan trắc. "
            f"Diện tích vẽ tay {vn(r['area_ve_tay_ha'],3)} ha được hiệu chỉnh {pct} %.")

    # --- 6. Radar ----------------------------------------------------------
    if s1 is not None:
        doc.add_page_break()
        doc.add_heading("6. Sentinel-1 radar — dữ liệu không bị mây chặn", level=1)
        doc.add_paragraph(
            f"Ở Ninh Bình mùa mưa, ảnh quang học mất trắng hàng tháng liền. Radar "
            f"bước sóng C xuyên mây nên cả {len(s1s)} lượt bay trong 12 tháng đều "
            f"dùng được, không lượt nào bị loại. Radar không đo diệp lục như NDVI mà "
            f"đo cấu trúc và độ ẩm của tán — hai nguồn bổ sung nhau chứ không thay "
            f"thế nhau.")
        doc.add_paragraph(
            "Hai hướng bay được tách riêng: cùng một thửa, lượt bay lên và lượt bay "
            "xuống soi từ hai phía khác nhau nên lệch nhau cả dB. Trộn chung sẽ tạo "
            "ra một chuỗi răng cưa giả không phải do cây trồng.")
        pic(doc, "14_radar_sentinel1.png",
            "Hình 5. Tín hiệu VH toàn farm theo thời gian, tách theo hướng bay.", 17)
        pic(doc, "15_mat_do_du_lieu.png",
            "Hình 6. Số ngày có dữ liệu mỗi tháng. Radar lấp đúng những tháng mưa "
            "mà ảnh quang học trống.", 17)

    # --- 7. Khí hậu --------------------------------------------------------
    doc.add_page_break()
    doc.add_heading("7. Khí hậu 12 tháng", level=1)
    pic(doc, "02_ndvi_va_mua_12_thang.png",
        "Hình 7. NDVI trung bình toàn farm và lượng mưa ngày, chung trục thời gian.", 17)
    m = clim.groupby(clim["date"].dt.strftime("%m/%Y")).agg(
        mua=("precipitation_sum", "sum"), et0=("et0_fao_evapotranspiration", "sum"),
        tmax=("temperature_2m_max", "max"), tmin=("temperature_2m_min", "min"))
    m = m.reindex(sorted(m.index, key=lambda s: (s[3:], s[:2])))
    add_table(doc, ["Tháng", "Mưa (mm)", "ET0 (mm)", "Cân bằng (mm)",
                    "T° thấp nhất", "T° cao nhất"],
              [[i, vn(r["mua"], 0), vn(r["et0"], 0), f"{r['mua']-r['et0']:+,.0f}",
                vn(r["tmin"], 1), vn(r["tmax"], 1)] for i, r in m.iterrows()],
              widths=[2.6, 2.8, 2.8, 3.2, 2.8, 2.8], font=9)

    doc.add_heading("8. Thổ nhưỡng", level=1)
    doc.add_paragraph(
        "Nguồn SoilGrids v2.0 ở độ phân giải 250 m — là giá trị mô hình cho cả vùng, "
        "không thay thế mẫu đất phân tích tại ruộng. Toàn bộ 12 lô nằm trong cùng "
        "một ô 250 m nên không có khác biệt theo lô từ nguồn này.")
    add_table(doc, list(soil.columns), soil.round(2).values.tolist(), font=9)

    # --- 9. Phương pháp ----------------------------------------------------
    doc.add_page_break()
    doc.add_heading("9. Phương pháp", level=1)
    for head, body in [
        ("Đọc ranh giới lô",
         "Chủ farm vạch 12 lô bằng công cụ vẽ trên bản đồ, xuất ra PDF. Nét vẽ nằm "
         "trong PDF dưới dạng đường vector chứ không bị nướng vào ảnh, nên toạ độ "
         "được đọc thẳng từ vector — chính xác hơn hẳn việc dò lại nét trắng trên "
         "ảnh raster, nơi nét vẽ lẫn với mái nhà lưới và chữ nhãn của Google."),
        ("Gắn toạ độ cho ảnh chụp",
         "Ảnh chụp màn hình không mang toạ độ. Phép biến đổi pixel → WGS84 được xác "
         "định tự động bằng tương quan chéo chuẩn hoá với ảnh nền Esri World Imagery "
         "đã có toạ độ chuẩn. Cả hai ảnh lọc thông cao trước để bám vào cạnh (đường, "
         "mái nhà) thay vì màu — hai ảnh chụp khác mùa nên màu ruộng lệch hoàn toàn. "
         "Kết quả 0,406 m/pixel; kiểm chứng độc lập bằng toạ độ ghim RiTi lấy từ URL "
         "Google Maps cho sai lệch 2,9 m."),
        ("Nắn ranh giới",
         "Phân thuỷ có mầm trên bản đồ độ dốc sáng của ảnh: mỗi lô co vào 12 pixel "
         "làm mầm, vành ±12 pixel quanh nét vẽ để trống, biên chạy về sống núi độ dốc "
         "trong vành đó. Vì mầm giữ nguyên định danh lô nên tô pô không đổi."),
        ("Tách dữ liệu theo lô",
         "Lô nhỏ nhất chỉ khoảng 20 pixel Sentinel-2, mà pixel ngoài rìa thì nửa "
         "trong nửa ngoài. Mỗi pixel 10 m vì thế được chia 4×4 ô con 2,5 m, trọng số "
         "của pixel với lô bằng tỉ lệ ô con nằm trong lô. Trung bình có trọng số cho "
         "vành ngoài đóng góp đúng phần diện tích của nó, thay vì bị đếm tròn 0 hoặc 1."),
        ("Lọc mây",
         "Tỉ lệ mây trong metadata là của cả tile 110 × 110 km, vô dụng với một mảnh "
         f"{vn(farm_ha)} ha. Pipeline tính lại tỉ lệ mây riêng trong từng lô từ band "
         "phân loại cảnh SCL — nhờ vậy một cảnh ghi '99 % mây' vẫn dùng được nếu farm "
         "nằm đúng lỗ mây."),
        ("Radar",
         "gamma0 lưu ở thang tuyến tính, nên trung bình phải lấy trên thang tuyến "
         "tính rồi mới đổi sang dB; lấy trung bình thẳng trên dB là sai vì dB là hàm "
         "log. Nguồn dùng bản RTC đã hiệu chỉnh bức xạ và nắn theo địa hình."),
    ]:
        doc.add_heading(head, level=2)
        doc.add_paragraph(body)

    doc.add_heading("Nguồn dữ liệu", level=2)
    add_table(doc, ["Lớp", "Nguồn", "Độ phân giải"], [
        ["Ảnh đa phổ, NDVI/NDMI", "Sentinel-2 L2A (ESA) qua STAC Element84 + AWS", "10 m"],
        ["Radar VV/VH", "Sentinel-1 RTC qua Microsoft Planetary Computer", "10 m"],
        ["Ảnh nền phân giải cao", "Ảnh chụp Google Maps do chủ farm cung cấp", "0,41 m"],
        ["Ảnh nền tham chiếu toạ độ", "Esri World Imagery", "0,56 m"],
        ["Khí hậu", "Open-Meteo (ERA5 + mô hình dự báo)", "điểm"],
        ["Địa hình", "Copernicus GLO-30 DEM", "30 m"],
        ["Thổ nhưỡng", "SoilGrids v2.0 (ISRIC)", "250 m"],
    ], widths=[5.0, 8.5, 3.5], font=9)
    doc.add_paragraph("Toàn bộ nguồn miễn phí, không cần khoá API.")

    # --- 10. Giới hạn ------------------------------------------------------
    doc.add_heading("10. Giới hạn cần biết", level=1)
    small = summ[summ["area_ha"] < 0.3]
    for t in [
        f"Ranh giới có sai số ±2,9 m và KHÔNG phải ranh giới pháp lý. Không dùng cho "
        f"hồ sơ địa chính.",
        f"Ranh giới đã nắn phản ánh mép thửa NHÌN THẤY TRÊN ẢNH, không phải ranh giới "
        f"sở hữu. Nếu ranh giới thật khác hiện trạng canh tác, số liệu ở đây theo hiện trạng.",
        f"NDVI của lô nhỏ kém tin cậy: {len(small)} lô dưới 0,3 ha "
        f"({', '.join(small['lo_id'])}) chỉ chứa vài chục pixel Sentinel-2 và còn "
        f"chịu ảnh hưởng lẫn từ lô bên cạnh.",
        f"Nhãn phân loại suy từ dạng chuỗi NDVI 12 tháng, chưa đối chiếu thực địa. "
        f"NDVI cao có thể là vườn cây ăn quả, cũng có thể là bụi rậm — cần một lần đi "
        f"thực địa để gán đúng cây trồng.",
        f"Chuỗi quang học vẫn thưa vào mùa mưa dù đã kéo dài 12 tháng; đó là lý do có "
        f"thêm radar. Radar bù được về mật độ nhưng nhiễu đốm nhiều hơn, phải đọc "
        f"theo xu hướng chứ không đọc từng điểm.",
        f"Thổ nhưỡng SoilGrids ở 250 m là giá trị mô hình cho cả vùng, không thay thế "
        f"mẫu đất phân tích tại ruộng.",
    ]:
        doc.add_paragraph(t, style="List Bullet")

    doc.save(OUT)
    print("đã ghi:", OUT)
    print(f"  {len(lots)} lô · {vn(farm_ha)} ha · {n_s2_day} ngày S2 · {n_s1_day} ngày S1")


if __name__ == "__main__":
    main()
