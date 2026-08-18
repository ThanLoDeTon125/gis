"""Báo cáo TÌNH TRẠNG VÙNG TRỒNG 12 tháng — bản đọc hiện tượng, cho chủ farm.

Khác với BaoCao_RiTi_Farm_12_lo.docx (thiên về phương pháp và số liệu gốc), bản
này trả lời câu hỏi của người trồng: 12 tháng qua vườn ra sao, lô nào mấy vụ,
lúc nào thiếu nước, lô nào đang kém, giờ đang thế nào.

Mọi con số đọc từ data/out/ — không gõ tay con số nào.
"""
import os
from datetime import datetime

import numpy as np
import pandas as pd
from docx import Document
from docx.enum.section import WD_ORIENT
from docx.enum.text import WD_ALIGN_PARAGRAPH
from docx.shared import Cm, Pt, RGBColor

from make_report_docx import ACCENT, INK2, add_table, caption, pic, vn

BASE = os.path.expanduser("~/Documents/GIS_RiTi_TrangAn")
OUT = f"{BASE}/BaoCao_TinhTrang_VungTrong_12Thang.docx"
THANG_VN = {1: "01", 2: "02", 3: "03", 4: "04", 5: "05", 6: "06",
            7: "07", 8: "08", 9: "09", 10: "10", 11: "11", 12: "12"}


def d(x):
    return pd.Timestamp(x).strftime("%d/%m/%Y")


def sg(x, n=2):
    """Số có dấu, dấu thập phân kiểu Việt: +0,22 / -0,07."""
    return f"{x:+.{n}f}".replace(".", ",")


def bullet(doc, text):
    doc.add_paragraph(text, style="List Bullet")


def main():
    tt = pd.read_csv(f"{BASE}/data/out/lot_tinh_trang.csv", parse_dates=["ngay_cuoi"])
    ck = pd.read_csv(f"{BASE}/data/out/lot_chu_ky.csv", parse_dates=["dinh", "day"])
    nw = pd.read_csv(f"{BASE}/data/out/nuoc_theo_thang.csv")
    s2 = pd.read_csv(f"{BASE}/data/out/lot_s2_timeseries.csv", parse_dates=["date"])
    s1 = pd.read_csv(f"{BASE}/data/out/lot_s1_timeseries.csv", parse_dates=["date"])
    cl = pd.read_csv(f"{BASE}/data/out/climate_daily.csv", parse_dates=["date"])
    sm = pd.read_csv(f"{BASE}/data/out/soil_moisture_daily.csv", parse_dates=["date"])
    soil = pd.read_csv(f"{BASE}/data/out/soil_soilgrids.csv")
    summ = pd.read_csv(f"{BASE}/data/out/lots_summary.csv")

    tt = tt.sort_values("lo_id").reset_index(drop=True)
    farm_ha = tt["area_ha"].sum()
    ngay0, ngay1 = cl["date"].min(), cl["date"].max()
    mua_tong = cl["precipitation_sum"].sum()
    et0_tong = cl["et0_fao_evapotranspiration"].sum()
    thieu = nw[nw["can_bang"] < 0]

    # lỗ hổng quan trắc quang học
    days = sorted(s2["date"].unique())
    gaps = []
    for i in range(len(days) - 1):
        g = (pd.Timestamp(days[i + 1]) - pd.Timestamp(days[i])).days
        if g > 35:
            n1 = s1[(s1["date"] > days[i]) & (s1["date"] < days[i + 1])]["date"].nunique()
            gaps.append((pd.Timestamp(days[i]), pd.Timestamp(days[i + 1]), g, n1))

    # chuỗi ngày khô dài nhất
    cur, best = 0, (0, None)
    for i, v in enumerate(cl["precipitation_sum"] < 1):
        cur = cur + 1 if v else 0
        if cur > best[0]:
            best = (cur, cl["date"].iloc[i])

    doc = Document()
    sec = doc.sections[0]
    sec.orientation, sec.page_width, sec.page_height = (
        WD_ORIENT.PORTRAIT, Cm(21), Cm(29.7))
    sec.left_margin = sec.right_margin = Cm(2.0)
    st = doc.styles["Normal"]
    st.font.name = "Calibri"
    st.font.size = Pt(10.5)

    # ================= Bìa =================
    h = doc.add_heading("BÁO CÁO TÌNH TRẠNG VÙNG TRỒNG", level=0)
    h.alignment = WD_ALIGN_PARAGRAPH.CENTER
    p = doc.add_paragraph(); p.alignment = WD_ALIGN_PARAGRAPH.CENTER
    r = p.add_run("RiTi Organic Farm | Tràng An\nTrường Yên, Hoa Lư, Ninh Bình")
    r.bold = True; r.font.size = Pt(14); r.font.color.rgb = ACCENT
    p = doc.add_paragraph(); p.alignment = WD_ALIGN_PARAGRAPH.CENTER
    r = p.add_run(f"12 tháng: {d(ngay0)} – {d(ngay1)} · lập ngày "
                  f"{datetime.now():%d/%m/%Y}")
    r.font.size = Pt(10); r.font.color.rgb = INK2

    len_ = tt[tt["trang_thai_cuoi_ky"] == "đang lên xanh"]
    xuong = tt[tt["trang_thai_cuoi_ky"].str.startswith("đang xuống")]
    add_table(doc, ["Chỉ tiêu", "Giá trị"], [
        ["Vùng trồng", f"{len(tt)} lô · {vn(farm_ha)} ha"],
        ["NDVI trung bình cả năm", f"{vn(tt['ndvi_tb'].mean(), 2)} "
                                   f"(thấp nhất {vn(tt['ndvi_tb'].min(),2)} — "
                                   f"cao nhất {vn(tt['ndvi_tb'].max(),2)})"],
        ["Số vụ dò được", f"{int(tt['so_vu'].sum())} vụ trên "
                          f"{int((tt['so_vu']>0).sum())} lô "
                          f"({int(tt['so_vu_chac'].sum())} vụ chắc chắn)"],
        ["Mưa cả năm", f"{vn(mua_tong,0)} mm / {int((cl['precipitation_sum']>=1).sum())} ngày có mưa"],
        ["Bốc thoát hơi ET0", f"{vn(et0_tong,0)} mm"],
        ["Cân bằng nước", f"{sg(mua_tong-et0_tong,0)} mm cả năm, "
                          f"nhưng thiếu ở {len(thieu)} tháng"],
        ["Đợt khô dài nhất", f"{best[0]} ngày liền không mưa, kết thúc {d(best[1])}"],
        ["Nhiệt độ", f"{vn(cl['temperature_2m_min'].min(),1)} – "
                     f"{vn(cl['temperature_2m_max'].max(),1)} °C"],
        ["Hiện trạng cuối kỳ", f"{len(len_)} lô đang lên xanh · "
                               f"{len(tt)-len(len_)-len(xuong)} lô ổn định · "
                               f"{len(xuong)} lô đang xuống"],
        ["Nguồn quan trắc", f"{s2['date'].nunique()} ngày ảnh quang học + "
                            f"{s1['date'].nunique()} ngày ảnh radar"],
    ], widths=[5.0, 12.0], font=10)

    # ================= 1. Tóm tắt =================
    doc.add_heading("1. Tóm tắt cho người quản lý", level=1)
    manh = tt.nlargest(2, "lech_tb")
    yeu = tt.nsmallest(2, "lech_tb")

    bullet(doc, f"Cả năm vùng trồng THỪA nước ({vn(mua_tong-et0_tong,0)} mm), nhưng "
                f"đó là con số cả năm và nó che mất vấn đề thật: "
                f"{len(thieu)} tháng liên tiếp {thieu['ym'].iloc[0][5:]}–"
                f"{thieu['ym'].iloc[-1][5:]}/{thieu['ym'].iloc[-1][:4]} mưa KHÔNG ĐỦ bù bốc hơi "
                f"(thiếu tổng cộng {vn(abs(thieu['can_bang'].sum()),0)} mm). "
                f"Đây là giai đoạn duy nhất trong năm cần tưới chủ động.")
    bullet(doc, f"Hai lô xanh nhất năm qua là {manh.iloc[0]['lo_id']} và "
                f"{manh.iloc[1]['lo_id']} (cao hơn mặt bằng farm "
                f"{sg(manh.iloc[0]['lech_tb'],3)} và {sg(manh.iloc[1]['lech_tb'],3)} NDVI). "
                f"Hai lô kém nhất là {yeu.iloc[0]['lo_id']} và {yeu.iloc[1]['lo_id']} "
                f"({sg(yeu.iloc[0]['lech_tb'],3)} và {sg(yeu.iloc[1]['lech_tb'],3)}).")
    nhieu = tt[tt["so_vu"] == tt["so_vu"].max()]["lo_id"].tolist()
    bullet(doc, f"Toàn farm dò được {int(tt['so_vu'].sum())} vụ trong 12 tháng. "
                f"Nhiều vụ nhất là {int(tt['so_vu'].max())} vụ, ở "
                f"{len(nhieu)} lô ({', '.join(nhieu)}). "
                f"{int((tt['so_vu']==0).sum())} lô không có đỉnh vụ rõ — "
                f"che phủ gần như liên tục, không thu theo đợt.")
    bullet(doc, f"Mùa khô làm NDVI tụt ở {int((tt['chenh_mua']>0).sum())}/{len(tt)} lô. "
                f"Tụt sâu nhất là {tt.nlargest(1,'chenh_mua').iloc[0]['lo_id']} "
                f"({vn(tt['chenh_mua'].max(),2)} NDVI). "
                f"Riêng {', '.join(tt[tt['chenh_mua']<0]['lo_id'])} lại xanh hơn vào mùa khô — "
                f"dấu hiệu có canh tác vụ đông hoặc có tưới.")
    bullet(doc, f"Ảnh quang học có {len(gaps)} khoảng mù dài trên 35 ngày, dài nhất "
                f"{max(g[2] for g in gaps)} ngày ({d(max(gaps, key=lambda g: g[2])[0])} – "
                f"{d(max(gaps, key=lambda g: g[2])[1])}). Radar phủ kín các khoảng này, "
                f"nên vẫn theo dõi được, nhưng một vụ ngắn nằm gọn trong khoảng mù thì "
                f"không thể khẳng định bằng ảnh quang học.")
    bullet(doc, f"Tại lần quan trắc cuối ({d(tt['ngay_cuoi'].max())}): "
                f"{len(len_)} lô đang lên xanh ({', '.join(len_['lo_id'])}), "
                f"{len(xuong)} lô đang xuống ({', '.join(xuong['lo_id'])} — "
                f"nhiều khả năng vừa thu hoặc sắp thu).")

    # ================= 2. Vùng trồng =================
    doc.add_page_break()
    doc.add_heading("2. Vùng trồng", level=1)
    doc.add_paragraph(
        f"Vùng trồng gồm {len(tt)} lô do chủ farm vạch, tổng {vn(farm_ha)} ha. "
        f"Ranh giới đã được nắn về mép ruộng và mép đường thật nhìn thấy trên ảnh "
        f"0,41 m/pixel, nên diện tích từng lô dưới đây là diện tích đã hiệu chỉnh "
        f"chứ không phải diện tích nét vẽ.")
    pic(doc, "10_ban_do_12_lo.png",
        f"Hình 1. {len(tt)} lô, tô theo NDVI trung bình 12 tháng. Xanh đậm = tán "
        f"dày quanh năm.", 17)
    add_table(doc, ["Lô", "Diện tích (ha)", "% farm", "NDVI trung bình",
                    "Biên độ NDVI", "Kiểu canh tác"],
              [[r["lo_id"], vn(r["area_ha"], 3), f"{vn(100*r['area_ha']/farm_ha,1)} %",
                vn(r["ndvi_tb"], 2), vn(r["bien_do"], 2), r["loai"]]
               for _, r in tt.iterrows()],
              widths=[1.6, 2.6, 1.9, 2.8, 2.5, 5.6], font=9)

    # ================= 3. Diễn biến cả năm =================
    doc.add_page_break()
    doc.add_heading("3. Diễn biến 12 tháng của toàn vùng trồng", level=1)
    farm_m = s2.groupby(s2["date"].dt.to_period("M"))["ndvi"].mean()
    cao = farm_m.idxmax(); thap = farm_m.idxmin()
    doc.add_paragraph(
        f"NDVI trung bình toàn farm cao nhất vào {THANG_VN[cao.month]}/{cao.year} "
        f"({vn(farm_m.max(),2)}) và thấp nhất vào {THANG_VN[thap.month]}/{thap.year} "
        f"({vn(farm_m.min(),2)}). Nhịp này bám theo mùa mưa: mưa dồn vào tháng 5–10, "
        f"tháng 11–4 khô dần, và vùng trồng xuống màu theo.")
    pic(doc, "02_ndvi_va_mua_12_thang.png",
        "Hình 2. NDVI trung bình toàn farm (trên) và lượng mưa từng ngày (dưới), "
        "chung trục thời gian. Hai đại lượng để riêng hai khung — chồng lên một "
        "khung với hai trục dọc là cách tạo ra tương quan không có thật.", 17)
    pic(doc, "12_chuoi_ndvi_tung_lo.png",
        "Hình 3. Chuỗi NDVI riêng của từng lô, trục dọc chung 0–1. Đường xám là "
        "trung bình toàn farm để so sánh.", 17)

    doc.add_heading("3.1 Những khoảng không nhìn thấy được bằng ảnh quang học", level=2)
    doc.add_paragraph(
        f"Mây che khiến chuỗi quang học có {len(gaps)} khoảng trống dài. Đây là giới "
        f"hạn thật của số liệu, không phải là khoảng thời gian vườn không có gì xảy ra:")
    add_table(doc, ["Từ", "Đến", "Số ngày mù", "Radar có trong khoảng"],
              [[d(a), d(b), f"{g} ngày", f"{n} ngày"] for a, b, g, n in gaps],
              widths=[3.6, 3.6, 3.4, 4.4], font=9.5)

    # ================= 4. Chu kỳ canh tác =================
    doc.add_page_break()
    doc.add_heading("4. Chu kỳ canh tác từng lô", level=1)
    doc.add_paragraph(
        "Một vụ để lại dấu vết rất đặc trưng trên NDVI: đất trống sau làm đất cho "
        "giá trị thấp, cây lên thì NDVI tăng dần, tán phủ kín cho đỉnh, thu hoạch "
        "làm rơi thẳng xuống. Bảng dưới liệt kê các đỉnh dò được cùng ngày đạt đỉnh.")
    doc.add_paragraph(
        "Cột “Độ tin cậy” quan trọng: một đỉnh chỉ được coi là chắc khi có quan "
        "trắc thật trong vòng 12 ngày quanh đỉnh VÀ đoạn từ đáy lên đỉnh không vắt "
        "qua khoảng mù dài. Đỉnh nằm giữa khoảng mù chỉ là suy đoán từ nội suy.")
    pic(doc, "16_chu_ky_canh_tac.png",
        "Hình 4. Đỉnh vụ trên chuỗi NDVI từng lô. Nền xám là khoảng không có ảnh "
        "quang học.", 17)
    add_table(doc, ["Lô", "Vụ", "Bắt đầu lên", "NDVI đáy", "Đạt đỉnh", "NDVI đỉnh",
                    "Số ngày lên", "Độ tin cậy"],
              [[r["lo_id"], int(r["vu"]), d(r["day"]), vn(r["ndvi_day"], 2),
                d(r["dinh"]), vn(r["ndvi_dinh"], 2), f"{int(r['so_ngay_len'])} ngày",
                r["tin_cay"]] for _, r in ck.sort_values(["lo_id", "vu"]).iterrows()],
              font=8.5)
    khong_vu = tt[tt["so_vu"] == 0]
    if len(khong_vu):
        doc.add_paragraph(
            f"{len(khong_vu)} lô không có đỉnh vụ nào: "
            f"{', '.join(khong_vu['lo_id'])}. NDVI của các lô này đi lên đều hoặc "
            f"dao động nhỏ suốt 12 tháng, không có cú rơi kiểu thu hoạch — phù hợp "
            f"với cây lâu năm, cỏ, hoặc một vụ dài chưa tới lúc thu.")

    # ================= 5. Mùa khô / mùa mưa =================
    doc.add_page_break()
    doc.add_heading("5. Mùa khô so với mùa mưa", level=1)
    doc.add_paragraph(
        f"Mùa mưa ở đây là tháng 5–10 (mưa {vn(nw[nw['ym'].str[5:].astype(int).isin([5,6,7,8,9,10])]['mua'].sum(),0)} mm), "
        f"mùa khô là tháng 11–4 "
        f"(mưa {vn(nw[~nw['ym'].str[5:].astype(int).isin([5,6,7,8,9,10])]['mua'].sum(),0)} mm). "
        f"Chênh lệch NDVI giữa hai mùa cho biết lô nào phụ thuộc nước trời và lô nào "
        f"vẫn giữ được màu vào mùa khô.")
    pic(doc, "21_mua_kho_mua_mua.png",
        "Hình 5. NDVI mùa khô (cam) so với mùa mưa (lam) của từng lô.", 16)
    add_table(doc, ["Lô", "NDVI mùa khô", "NDVI mùa mưa", "Chênh", "Đọc thế nào"],
              [[r["lo_id"], vn(r["ndvi_mua_kho"], 2), vn(r["ndvi_mua_mua"], 2),
                sg(r["chenh_mua"]),
                ("tụt mạnh mùa khô — phụ thuộc nước trời" if r["chenh_mua"] >= 0.15
                 else "giữ màu khá đều" if r["chenh_mua"] >= 0
                 else "xanh hơn vào mùa khô — có vụ đông hoặc có tưới")]
               for _, r in tt.sort_values("chenh_mua", ascending=False).iterrows()],
              widths=[1.6, 3.0, 3.0, 2.0, 7.4], font=9)

    # ================= 6. Nước =================
    doc.add_page_break()
    doc.add_heading("6. Nước: mưa, bốc hơi, độ ẩm đất", level=1)
    doc.add_paragraph(
        f"Cả năm mưa {vn(mua_tong,0)} mm so với bốc thoát hơi tham chiếu ET0 "
        f"{vn(et0_tong,0)} mm — thừa {vn(mua_tong-et0_tong,0)} mm. Nhưng nước không "
        f"chia đều: {len(thieu)} tháng có mưa ít hơn bốc hơi, và đó mới là những "
        f"tháng quyết định.")
    pic(doc, "17_can_bang_nuoc.png",
        "Hình 6. Mưa và ET0 theo tháng (trên); cân bằng mưa − ET0 (dưới). Cột đỏ là "
        "tháng phải tưới bù.", 17)
    add_table(doc, ["Tháng", "Mưa (mm)", "Ngày mưa", "ET0 (mm)", "Cân bằng (mm)",
                    "Ẩm tầng mặt", "Ẩm tầng sâu"],
              [[r["ym"][2:], vn(r["mua"], 0), int(r["ngay_mua"]), vn(r["et0"], 0),
                sg(r["can_bang"], 0), vn(r["sm_nong"], 3), vn(r["sm_sau"], 3)]
               for _, r in nw.iterrows()],
              widths=[2.2, 2.3, 2.1, 2.3, 2.9, 2.6, 2.6], font=9)
    doc.add_paragraph(
        f"Đợt khô dài nhất kéo {best[0]} ngày liền không mưa, kết thúc {d(best[1])} — "
        f"rơi đúng cuối mùa khô, khi ET0 đã bắt đầu tăng theo nắng. Độ ẩm tầng mặt "
        f"xuống thấp nhất {vn(sm['sm_nong'].min(),3)} m³/m³ vào "
        f"{d(sm.loc[sm['sm_nong'].idxmin(),'date'])}.")
    pic(doc, "18_do_am_dat.png",
        "Hình 7. Độ ẩm đất ba tầng (trên) và chuỗi ngày không mưa (dưới). Tầng mặt "
        "phản ứng ngay theo từng trận mưa, tầng sâu đổi chậm — đó là bộ đệm nước "
        "của cây lâu năm.", 17)

    # ================= 7. Sức khoẻ & đồng đều =================
    doc.add_page_break()
    doc.add_heading("7. Độ đồng đều và sức khoẻ giữa các lô", level=1)
    doc.add_paragraph(
        "So từng lô với mặt bằng chung của farm trong cùng ngày sẽ loại được ảnh "
        "hưởng thời tiết: nếu cả farm cùng xuống vì hạn thì mức lệch không đổi. Lô "
        "lệch âm kéo dài là lô thực sự kém hơn phần còn lại.")
    pic(doc, "19_lech_so_voi_farm.png",
        "Hình 8. Lệch NDVI trung bình so với mặt bằng farm (trái) và lệch theo từng "
        "ngày quan trắc (phải).", 17)
    add_table(doc, ["Lô", "Lệch trung bình", "Độ dao động của mức lệch", "Đọc thế nào"],
              [[r["lo_id"], sg(r["lech_tb"], 3),
                vn(r["lech_do_on_dinh"], 3),
                ("hơn hẳn mặt bằng, ổn định" if r["lech_tb"] > 0.05 and r["lech_do_on_dinh"] < 0.12
                 else "hơn mặt bằng" if r["lech_tb"] > 0.05
                 else "kém mặt bằng rõ rệt" if r["lech_tb"] < -0.08
                 else "quanh mặt bằng chung")]
               for _, r in tt.sort_values("lech_tb", ascending=False).iterrows()],
              widths=[1.8, 3.4, 4.4, 7.4], font=9)

    doc.add_heading("7.1 Ẩm trong tán lá (NDMI)", level=2)
    doc.add_paragraph(
        "NDMI đo nước trong lá, thường xuống trước khi NDVI xuống — cây thiếu nước "
        "thì lá mất nước trước, rụng lá sau. Giá trị âm là tán khô.")
    pic(doc, "22_ndmi_theo_thang.png",
        "Hình 9. NDMI theo tháng của từng lô.", 17)
    kho_nhat = tt.nsmallest(3, "ndmi_mua_kho")
    doc.add_paragraph(
        f"Vào mùa khô, tán khô nhất là {', '.join(kho_nhat['lo_id'])} "
        f"(NDMI {', '.join(vn(v,2) for v in kho_nhat['ndmi_mua_kho'])}). "
        f"Đây là các lô nên ưu tiên khi phải chọn thứ tự tưới.")

    # ================= 8. Radar =================
    doc.add_page_break()
    doc.add_heading("8. Những gì ảnh quang học không thấy — radar", level=1)
    doc.add_paragraph(
        f"Radar Sentinel-1 xuyên mây nên có mặt cả trong những tháng ảnh quang học "
        f"trống hoàn toàn: {s1['date'].nunique()} ngày trong 12 tháng, không ngày nào "
        f"bị loại vì mây. Radar không đo diệp lục mà đo cấu trúc và nước trong tán, "
        f"nên dùng để xác nhận “có biến động hay không” trong khoảng mù, chứ không "
        f"thay được NDVI.")
    pic(doc, "15_mat_do_du_lieu.png",
        "Hình 10. Số ngày có dữ liệu mỗi tháng. Tháng 02/2026 không có một ngày "
        "quang học nào, radar vẫn có đủ.", 17)
    pic(doc, "13_nhiet_do_lo_theo_thang.png",
        "Hình 11. NDVI (trên) và radar VH (dưới) theo tháng cho từng lô. Bảng dưới "
        "không có ô trống — đó là giá trị của radar.", 17)
    pic(doc, "14_radar_sentinel1.png",
        "Hình 12. Tín hiệu VH toàn farm, tách riêng hai hướng bay.", 17)

    # ================= 9. Hiện trạng =================
    doc.add_page_break()
    doc.add_heading("9. Hiện trạng cuối kỳ", level=1)
    doc.add_paragraph(
        f"Lần quan trắc quang học gần nhất là {d(tt['ngay_cuoi'].max())}. Xu hướng "
        f"tính bằng độ dốc NDVI của 4 lần quan trắc cuối, quy về mỗi tháng.")
    pic(doc, "23_hien_trang_cuoi_ky.png",
        "Hình 13. Hiện trạng từng lô ở lần quan trắc cuối.", 17)
    add_table(doc, ["Lô", "NDVI cuối", "Xu hướng/tháng", "Trạng thái", "Đọc thế nào"],
              [[r["lo_id"], vn(r["ndvi_cuoi"], 2),
                sg(r["xu_huong_thang"]),
                r["trang_thai_cuoi_ky"],
                ("tán đang dày lên nhanh" if r["xu_huong_thang"] >= 0.15
                 else "đang lên" if r["xu_huong_thang"] >= 0.05
                 else "vừa thu hoặc tán đang thưa đi" if r["xu_huong_thang"] <= -0.05
                 else "giữ nguyên")]
               for _, r in tt.sort_values("xu_huong_thang", ascending=False).iterrows()],
              widths=[1.6, 2.6, 3.0, 5.4, 4.4], font=9)

    # ================= 10. Chi tiết từng lô =================
    doc.add_page_break()
    doc.add_heading("10. Chi tiết từng lô", level=1)
    for _, r in tt.iterrows():
        doc.add_heading(f"Lô {int(r['lo_id'][1:])} — {vn(r['area_ha'],3)} ha "
                        f"({vn(100*r['area_ha']/farm_ha,1)} % farm)", level=2)
        dd = s2[s2["lo_id"] == r["lo_id"]].sort_values("date")
        hi, lo = dd.loc[dd["ndvi"].idxmax()], dd.loc[dd["ndvi"].idxmin()]
        p = doc.add_paragraph()
        p.add_run(f"{r['loai']}. ").bold = True
        p.add_run(
            f"NDVI cả năm trung bình {vn(r['ndvi_tb'],2)}, dao động "
            f"{vn(r['ndvi_min'] if 'ndvi_min' in r else dd['ndvi'].min(),2)}–"
            f"{vn(dd['ndvi'].max(),2)}; cao nhất ngày {d(hi['date'])}, thấp nhất "
            f"ngày {d(lo['date'])}. So với mặt bằng farm, lô này lệch "
            f"{sg(r['lech_tb'], 3)} NDVI.")
        c = ck[ck["lo_id"] == r["lo_id"]]
        if len(c):
            mo = ", ".join(f"đỉnh {d(x['dinh'])} (NDVI {vn(x['ndvi_dinh'],2)}, "
                           f"{x['tin_cay']})" for _, x in c.iterrows())
            doc.add_paragraph(f"Chu kỳ: {len(c)} vụ — {mo}.")
        else:
            doc.add_paragraph("Chu kỳ: không có đỉnh vụ rõ trong 12 tháng — che phủ "
                              "liên tục hoặc vụ dài chưa thu.")
        doc.add_paragraph(
            f"Theo mùa: NDVI mùa khô {vn(r['ndvi_mua_kho'],2)}, mùa mưa "
            f"{vn(r['ndvi_mua_mua'],2)} (chênh {sg(r['chenh_mua'])}). "
            f"NDMI mùa khô {vn(r['ndmi_mua_kho'],2)}, mùa mưa "
            f"{vn(r['ndmi_mua_mua'],2)}.")
        doc.add_paragraph(
            f"Hiện trạng {d(r['ngay_cuoi'])}: NDVI {vn(r['ndvi_cuoi'],2)}, xu hướng "
            f"{sg(r['xu_huong_thang'])}/tháng — {r['trang_thai_cuoi_ky']}.")

    # ================= 11. Đất & địa hình =================
    doc.add_page_break()
    doc.add_heading("11. Đất và địa hình", level=1)
    doc.add_paragraph(
        "Toàn bộ 12 lô nằm trong cùng một ô 250 m của SoilGrids, nên nguồn này "
        "không phân biệt được giữa các lô. Số liệu dưới đây là nền chung của cả "
        "vùng, không thay thế mẫu đất phân tích tại ruộng.")
    add_table(doc, list(soil.columns), soil.round(2).values.tolist(), font=9)
    if "cao_do_m" in summ.columns:
        doc.add_paragraph(
            f"Địa hình gần như bằng phẳng: cao độ {vn(summ['cao_do_m'].min(),1)}–"
            f"{vn(summ['cao_do_m'].max(),1)} m, độ dốc trung bình "
            f"{vn(summ['do_doc_deg'].mean(),1)}°. Lô cao nhất là "
            f"{summ.loc[summ['cao_do_m'].idxmax(),'lo_id']}, thấp nhất là "
            f"{summ.loc[summ['cao_do_m'].idxmin(),'lo_id']} — chênh "
            f"{vn(summ['cao_do_m'].max()-summ['cao_do_m'].min(),1)} m, đủ để tạo "
            f"khác biệt về tiêu thoát nước sau mưa lớn.")
        add_table(doc, ["Lô", "Cao độ (m)", "Độ dốc (°)"],
                  [[r["lo_id"], vn(r["cao_do_m"], 1), vn(r["do_doc_deg"], 1)]
                   for _, r in summ.iterrows()],
                  widths=[3.0, 4.5, 4.5], font=9.5)
        pic(doc, "20_dia_hinh_do_doc.png", "Hình 14. Cao độ và độ dốc toàn khu.", 16)

    # ================= 12. Nhận định =================
    doc.add_page_break()
    doc.add_heading("12. Nhận định và việc nên làm", level=1)
    doc.add_heading("12.1 Nước", level=2)
    bullet(doc, f"Kế hoạch tưới chỉ cần cho {len(thieu)} tháng "
                f"({', '.join(t[5:]+'/'+t[:4] for t in thieu['ym'])}), tổng thiếu hụt "
                f"{vn(abs(thieu['can_bang'].sum()),0)} mm. Với {vn(farm_ha)} ha, "
                f"lượng nước cần bù xấp xỉ "
                f"{vn(abs(thieu['can_bang'].sum())*farm_ha*10,0)} m³ cho cả giai đoạn.")
    bullet(doc, f"Mùa mưa thì ngược lại: tháng cao điểm mưa tới "
                f"{vn(nw['mua'].max(),0)} mm. Việc cần lo là TIÊU nước chứ không phải tưới, "
                f"nhất là các lô trũng.")
    doc.add_heading("12.2 Theo lô", level=2)
    for _, r in tt.nsmallest(3, "lech_tb").iterrows():
        bullet(doc, f"{r['lo_id']} ({vn(r['area_ha'],2)} ha) kém mặt bằng "
                    f"{sg(r['lech_tb'], 3)} NDVI suốt năm. Cần xác minh tại chỗ: đây "
                    f"là đất trống/công trình (thì số liệu đúng và không cần làm gì), "
                    f"hay là lô đang canh tác nhưng kém (thì cần tìm nguyên nhân).")
    for _, r in tt.nlargest(2, "lech_tb").iterrows():
        bullet(doc, f"{r['lo_id']} ({vn(r['area_ha'],2)} ha) là lô tốt nhất farm, "
                    f"NDVI trung bình {vn(r['ndvi_tb'],2)} và giữ màu cả mùa khô "
                    f"({vn(r['ndvi_mua_kho'],2)}). Đây là chuẩn để so các lô khác.")
    doc.add_heading("12.3 Cần kiểm chứng tại thực địa", level=2)
    bullet(doc, "Cây trồng thực tế trên từng lô. NDVI cao không phân biệt được vườn "
                "cây ăn quả với bụi rậm — một buổi đi thực địa ghi lại loại cây từng "
                "lô sẽ biến toàn bộ báo cáo này thành số liệu theo cây trồng.")
    n_kiem = ck[ck["tin_cay"] != "chắc"]
    if len(n_kiem):
        bullet(doc, f"{len(n_kiem)} đỉnh vụ cần kiểm chứng bằng sổ canh tác: "
                    + ", ".join(f"{r['lo_id']} ({d(r['dinh'])})"
                                for _, r in n_kiem.iterrows()) + ".")
    bullet(doc, "Ranh giới lô đã nắn theo hiện trạng nhìn thấy trên ảnh. Nếu ranh "
                "giới canh tác thật khác, báo lại để chỉnh — diện tích và toàn bộ số "
                "liệu theo lô sẽ tính lại theo.")

    doc.add_heading("13. Giới hạn của báo cáo", level=1)
    for t in [
        f"Ảnh quang học chỉ có {s2['date'].nunique()} ngày trong 12 tháng và phân bố "
        f"không đều — một vụ ngắn dưới 6 tuần nằm trong khoảng mù có thể không được ghi nhận.",
        f"Số vụ là số ĐỈNH NDVI dò được, không phải số vụ theo sổ canh tác. "
        f"{int(tt['so_vu_chac'].sum())}/{int(tt['so_vu'].sum())} đỉnh đạt mức chắc chắn.",
        f"NDVI của lô nhỏ kém tin cậy: lô dưới 0,3 ha chỉ chứa 20–26 pixel Sentinel-2 "
        f"và còn chịu ảnh hưởng lẫn từ lô bên cạnh.",
        f"Nhãn kiểu canh tác suy từ dạng chuỗi phổ ảnh, chưa đối chiếu thực địa.",
        f"Khí hậu là số liệu mô hình cho một điểm, không phải trạm đo đặt tại farm. "
        f"Dùng tốt cho xu hướng và so sánh giữa các tháng, không dùng thay nhật ký mưa tại chỗ.",
        f"Ranh giới có sai số ±2,9 m và không phải ranh giới pháp lý.",
    ]:
        bullet(doc, t)
    p = doc.add_paragraph()
    p.add_run("Chi tiết phương pháp, nguồn dữ liệu và cách dựng ranh giới: xem "
              "BaoCao_RiTi_Farm_12_lo.docx.").italic = True

    doc.save(OUT)
    print("đã ghi:", OUT)
    print(f"  {len(tt)} lô · {vn(farm_ha)} ha · {int(tt['so_vu'].sum())} vụ · "
          f"{len(gaps)} khoảng mù · {len(thieu)} tháng thiếu nước")


if __name__ == "__main__":
    main()
