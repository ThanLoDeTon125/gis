# -*- coding: utf-8 -*-
"""Kế hoạch canh tác 12 lô — phần MÔ PHỎNG, neo vào số liệu vệ tinh THẬT.

Mỗi lô có một khối `can_cu`: con số thật nào trong ../gis/ dẫn tới
kết luận "lô này trồng cái đó, từ tháng đó tới tháng đó". Không có dòng nào
trong file này được đặt tuỳ ý — mọi mốc đều truy được về một ô trong
`data/out/lot_chu_ky.csv`, `lot_tinh_trang.csv` hoặc `lot_ndvi_wide.csv`.

Đọc cùng: docs/05_THAT_VA_MAU.md
"""

# ---------------------------------------------------------------- cây trồng
# Kc = hệ số cây trồng FAO-56, dùng để quy ET0 (thật) về nhu cầu nước của lô.
# ini / mid / end = ba pha của chu kỳ. Cây lưu niên dùng một giá trị.
CAY_TRONG = {
    "CUC": {
        "ten": "Cúc chi",
        "ten_khoa_hoc": "Chrysanthemum indicum L.",
        "nhom": "duoc_lieu_hoa",
        "luu_nien": False,
        "kc": {"ini": 0.50, "mid": 1.05, "end": 0.75},
        "chu_ky_ngay": 130,
        "nang_suat_tuoi_tan_ha": 3.1,
        "ti_le_thu_hoi": 0.21,
        "trong_ma_dinh_danh": True,
    },
    "CCO": {
        "ten": "Cúc cổ (trà hoa cúc cổ)",
        "ten_khoa_hoc": "Chrysanthemum morifolium Ramat.",
        "nhom": "duoc_lieu_hoa",
        "luu_nien": True,
        "kc": {"ini": 0.60, "mid": 0.95, "end": 0.80},
        "chu_ky_ngay": None,
        "nang_suat_tuoi_tan_ha": 2.4,
        "ti_le_thu_hoi": 0.22,
        "trong_ma_dinh_danh": False,
    },
    "LAC": {
        "ten": "Lạc (đậu phộng)",
        "ten_khoa_hoc": "Arachis hypogaea L.",
        "nhom": "cay_luan_canh_ho_dau",
        "luu_nien": False,
        "kc": {"ini": 0.40, "mid": 1.15, "end": 0.60},
        "chu_ky_ngay": 145,
        "nang_suat_tuoi_tan_ha": 2.6,
        "ti_le_thu_hoi": 0.72,
        "trong_ma_dinh_danh": False,
    },
    "BCA": {
        "ten": "Bồ công anh",
        "ten_khoa_hoc": "Lactuca indica L.",
        "nhom": "duoc_lieu_la_re",
        "luu_nien": True,
        "kc": {"ini": 0.60, "mid": 1.00, "end": 0.85},
        "chu_ky_ngay": None,
        "nang_suat_tuoi_tan_ha": 9.0,
        "ti_le_thu_hoi": 0.14,
        "trong_ma_dinh_danh": False,
    },
    "CHA": {
        "ten": "Chanh",
        "ten_khoa_hoc": "Citrus aurantiifolia (Christm.) Swingle",
        "nhom": "cay_an_qua_luu_nien",
        "luu_nien": True,
        "kc": {"ini": 0.65, "mid": 0.70, "end": 0.65},
        "chu_ky_ngay": None,
        "nang_suat_tuoi_tan_ha": 11.0,
        "ti_le_thu_hoi": 1.0,
        "trong_ma_dinh_danh": True,
    },
    "DAU": {
        "ten": "Đậu che phủ (cây phân xanh)",
        "ten_khoa_hoc": "Vigna unguiculata (L.) Walp.",
        "nhom": "cay_che_phu",
        "luu_nien": False,
        "kc": {"ini": 0.40, "mid": 0.90, "end": 0.50},
        "chu_ky_ngay": 100,
        "nang_suat_tuoi_tan_ha": 0.0,
        "ti_le_thu_hoi": 0.0,
        "trong_ma_dinh_danh": False,
    },
    "UOM": {
        "ten": "Luống ươm cây giống",
        "ten_khoa_hoc": None,
        "nhom": "vuon_uom",
        "luu_nien": False,
        "kc": {"ini": 0.55, "mid": 0.80, "end": 0.60},
        "chu_ky_ngay": 75,
        "nang_suat_tuoi_tan_ha": 0.0,
        "ti_le_thu_hoi": 0.0,
        "trong_ma_dinh_danh": False,
    },
}

# ------------------------------------------------------------------- 12 lô
# muc_dich : canh_tac | luu_nien | cong_trinh | dat_nghi | vuon_uom
# ti_le_gieo: phần diện tích lô thật sự xuống giống (trừ lối đi, bờ, mương)
# vu[] .pha : mốc sinh trưởng dùng để chọn Kc và để đối chiếu với NDVI
KE_HOACH = {
    "L01": {
        "ten": "Ruộng lớn Đông",
        "muc_dich": "canh_tac",
        "ti_le_gieo": 0.82,
        "mo_ta": "Thửa phẳng nhất farm (độ dốc 0,26°), luân canh cúc chi vụ đông ↔ lạc vụ xuân.",
        "can_cu": [
            "lot_chu_ky.csv: 2 vụ dò được — đáy 12/08/2025 (NDVI 0,269) → đỉnh 01/10/2025 (0,730); đáy 14/01/2026 (0,150) → đỉnh 29/05/2026 (0,796).",
            "lot_ndvi_wide.csv: 0,738 (04/10/2025) → 0,307 (23/11/2025); và 0,796 (29/05/2026) → 0,183 (11/07/2026) — hai lần tụt hơn 0,4 điểm, dạng thu hoạch gọn.",
            "lots_summary.csv: biên độ 0,65 — mức chỉ có ở lô có đất trống giữa hai vụ.",
            "Hồ sơ cây THẬT SK-C-CUC25-L01-0007-P khai khu L01, xuống giống 10/07/2025, thu hái 18/11/2025 — rơi đúng đoạn NDVI tụt.",
        ],
        "vu": [
            {
                "ma": "L01-2025-CUC",
                "cay": "CUC",
                "gieo": "2025-07-10",
                "thu_tu": "2025-10-20",
                "thu_den": "2025-11-26",
                "neo": {"day": "2025-08-12", "ndvi_day": 0.269, "dinh": "2025-10-01", "ndvi_dinh": 0.730},
                "ghi_chu": "Ngày gieo lấy thẳng từ hồ sơ cây THẬT SK-C-CUC25-L01-0007-P. Cúc chi hái "
                           "NHIỀU ĐỢT vì hoa nở dần, nên cửa sổ thu kéo 5 tuần chứ không phải 9 ngày — "
                           "khớp với việc NDVI đã bắt đầu xuống từ 04/10 (0,738) chứ không đợi tới 18/11.",
            },
            {
                "ma": "L01-2026-LAC",
                "cay": "LAC",
                "gieo": "2026-02-05",
                "thu_tu": "2026-06-10",
                "thu_den": "2026-06-18",
                "neo": {"day": "2026-01-14", "ndvi_day": 0.150, "dinh": "2026-05-29", "ndvi_dinh": 0.796},
                "ghi_chu": "Lạc xuân đồng bằng sông Hồng, gieo đầu tháng 2 + ~130 ngày. Ngày thu SỬA LẠI "
                           "sau khi luật R2 bắt được cú tụt 0,741 (06/06) → 0,298 (21/06): thu thật rơi giữa "
                           "tháng 6, không phải đầu tháng 7 như lịch đặt ban đầu.",
            },
            {
                "ma": "L01-2026-CUC",
                "cay": "CUC",
                "gieo": "2026-07-20",
                "thu_tu": "2026-11-20",
                "thu_den": "2026-11-28",
                "neo": {"day": "2026-07-11", "ndvi_day": 0.183, "dinh": None, "ndvi_dinh": None},
                "ghi_chu": "Vụ ĐANG CHẠY — chưa có đỉnh. NDVI 10/08/2026 = 0,650, xu hướng +0,489/tháng.",
            },
        ],
    },
    "L02": {
        "ten": "Vườn cúc hỗn hợp",
        "muc_dich": "canh_tac",
        "ti_le_gieo": 0.75,
        "mo_ta": "Luống cúc chi chiếm khoảng một phần ba lô, phần còn lại là cúc cổ lưu gốc. "
                 "Vì chỉ một phần lô đổi theo vụ nên NDVI trung bình cả lô gần như phẳng.",
        "can_cu": [
            "Hồ sơ cây THẬT SK-C-CUC25-L02-0003-3: cúc chi, khu L02, gieo 10/07/2025, THU 20/11/2025.",
            "lots_summary.csv: biên độ 0,348 — NHỎ NHẤT farm. Một lô 0,92 ha trồng kín cúc chi rồi thu sạch "
            "thì biên độ phải cỡ L01 (0,65). Chỉ giải thích được nếu phần đổi theo vụ chiếm thiểu số diện tích.",
            "lot_ndvi_wide.csv: 0,4927 (20/11) → 0,4380 (23/11) → 0,5306 (18/12). Có một lần thu hoạch "
            "ĐƯỢC GHI NHẬN THẬT mà ảnh vệ tinh KHÔNG thấy — đây là ca kiểm chứng quan trọng nhất của bộ dữ liệu.",
            "lot_tinh_trang.csv: trạng thái cuối kỳ 'ổn định', xu hướng +0,021/tháng.",
        ],
        "vu": [
            {
                "ma": "L02-2025-CUC",
                "cay": "CUC",
                "gieo": "2025-07-10",
                "thu_tu": "2025-11-20",
                "thu_den": "2025-12-05",
                "ti_le_gieo": 0.30,
                "neo": {"day": "2025-09-21", "ndvi_day": 0.432, "dinh": "2025-10-06", "ndvi_dinh": 0.537},
                "ghi_chu": "Gieo và thu lấy thẳng từ hồ sơ cây thật SK-C-CUC25-L02-0003-3.",
            },
            {
                "ma": "L02-2026-CCO",
                "cay": "CCO",
                "gieo": "2023-03-01",
                "thu_tu": "2026-03-10",
                "thu_den": "2026-03-24",
                "ti_le_gieo": 0.45,
                "neo": {"day": "2025-12-05", "ndvi_day": 0.311, "dinh": "2026-03-10", "ndvi_dinh": 0.547},
                "ghi_chu": "Gốc cúc cổ trồng trước kỳ quan trắc — ngày trồng 'khong_kiem_duoc'.",
            },
        ],
    },
    "L03": {
        "ten": "Ruộng giữa",
        "muc_dich": "canh_tac",
        "ti_le_gieo": 0.80,
        "mo_ta": "Bồ công anh vụ đông → lạc vụ xuân → cúc chi vụ đông 2026. Ba vụ trong 14 tháng.",
        "can_cu": [
            "Hồ sơ cây THẬT SK-C-CUC26-L03-0011-B: cúc chi, khu L03, gieo 05/07/2026, đang trồng.",
            "lot_chu_ky.csv: đỉnh 20/12/2025 (0,590) và đỉnh 03/06/2026 (0,748).",
            "lot_ndvi_wide.csv: 0,748 (01/06/2026) → 0,310 (11/07/2026) — tụt 0,44 điểm trong 40 ngày, dạng thu lạc.",
            "CẢNH BÁO ĐỌC SỐ: đáy 09/04/2026 mà máy chấm KHÔNG phải đất trống — đó là đáy hạn toàn farm. 8/12 lô cùng sụt trong khoảng 07–12/04, trung bình −0,134; trùng chuỗi 18 ngày mưa dưới 1 mm bắt đầu 30/03/2026 và tháng có cân bằng nước âm nhất năm (−46,3 mm). Ngày gieo mô phỏng vì vậy đặt theo lịch nông vụ (12/02), không đặt theo đáy này.",
        ],
        "vu": [
            {
                "ma": "L03-2025-BCA",
                "cay": "BCA",
                "gieo": "2025-10-20",
                "thu_tu": "2025-12-14",
                "thu_den": "2025-12-30",
                "neo": {"day": "2025-12-05", "ndvi_day": 0.323, "dinh": "2025-12-20", "ndvi_dinh": 0.590},
                "ghi_chu": None,
            },
            {
                "ma": "L03-2026-LAC",
                "cay": "LAC",
                "gieo": "2026-02-12",
                "thu_tu": "2026-06-25",
                "thu_den": "2026-07-05",
                "neo": {"day": "2026-04-09", "ndvi_day": 0.260, "dinh": "2026-06-03", "ndvi_dinh": 0.748},
                "ghi_chu": "Đáy 09/04 là đáy hạn toàn farm, không phải ngày gieo — xem can_cu.",
            },
            {
                "ma": "L03-2026-CUC",
                "cay": "CUC",
                "gieo": "2026-07-05",
                "thu_tu": "2026-11-10",
                "thu_den": "2026-12-10",
                "neo": {"day": "2026-07-11", "ndvi_day": 0.310, "dinh": None, "ndvi_dinh": None},
                "ghi_chu": "Ngày gieo lấy thẳng từ hồ sơ cây THẬT SK-C-CUC26-L03-0011-B (đang trồng). "
                           "Khớp với NDVI đi lên ngay sau đó: 0,310 (11/07) → 0,617 (10/08/2026).",
            },
        ],
    },
    "L04": {
        "ten": "Khối chanh cây mẹ",
        "muc_dich": "luu_nien",
        "ti_le_gieo": 0.90,
        "mo_ta": "Khối chanh nhỏ giữ làm cây mẹ lấy mắt ghép; cao nhất farm (13,4 m).",
        "can_cu": [
            "lots_summary.csv: NDMI trung bình 0,283 — cao thứ nhì farm (trung bình farm 0,11). NDMI cao quanh năm = tán gỗ giữ nước, không phải cây thảo.",
            "lot_ndvi_wide.csv: NDVI ≥ 0,73 ở 14/22 ngày quan trắc; giá trị nhỏ nhất 0,331 rơi đúng ngày 14/09/2025 mà cả farm cùng mù.",
            "lot_chu_ky.csv: chỉ 1 'vụ' dò được — với cây lưu niên thì đó là đợt ra lộc, không phải vụ gieo.",
        ],
        "vu": [
            {
                "ma": "L04-CHA-LUU-NIEN",
                "cay": "CHA",
                "gieo": "2022-04-15",
                "thu_tu": "2025-09-05",
                "thu_den": "2025-11-15",
                "neo": {"day": "2025-09-11", "ndvi_day": 0.390, "dinh": "2025-10-06", "ndvi_dinh": 0.825},
                "ghi_chu": "Trồng trước kỳ quan trắc — ngày trồng 'khong_kiem_duoc'.",
            },
            {
                "ma": "L04-CHA-LUU-NIEN-2026",
                "cay": "CHA",
                "gieo": "2022-04-15",
                "thu_tu": "2026-05-20",
                "thu_den": "2026-08-12",
                "neo": {"day": "2026-04-07", "ndvi_day": 0.415, "dinh": "2026-07-11", "ndvi_dinh": 0.892},
                "ghi_chu": None,
            },
        ],
    },
    "L05": {
        "ten": "Luống bồ công anh Bắc",
        "muc_dich": "canh_tac",
        "ti_le_gieo": 0.85,
        "mo_ta": "Bồ công anh lưu gốc, cắt nhiều lứa trong năm.",
        "can_cu": [
            "lot_chu_ky.csv: 2 đỉnh — 20/11/2025 (0,682) và 10/03/2026 (0,570).",
            "lot_tinh_trang.csv: NDMI mùa khô 0,122 / mùa mưa 0,182 — giữ ẩm tán khá, không về mức đất trống.",
            "lot_tinh_trang.csv: xu hướng cuối kỳ −0,077/tháng, trạng thái 'đang xuống — thu hoạch hoặc suy giảm' → đang trong lứa cắt tháng 8/2026.",
        ],
        "vu": [
            {
                "ma": "L05-2025-BCA-L1",
                "cay": "BCA",
                "gieo": "2025-08-20",
                "thu_tu": "2025-11-20",
                "thu_den": "2025-11-30",
                "neo": {"day": "2025-09-11", "ndvi_day": 0.295, "dinh": "2025-11-20", "ndvi_dinh": 0.682},
                "ghi_chu": None,
            },
            {
                "ma": "L05-2026-BCA-L2",
                "cay": "BCA",
                "gieo": "2025-08-20",
                "thu_tu": "2026-03-10",
                "thu_den": "2026-03-18",
                "neo": {"day": "2026-01-14", "ndvi_day": 0.419, "dinh": "2026-03-10", "ndvi_dinh": 0.570},
                "ghi_chu": "Cắt lứa 2 trên cùng gốc, không gieo lại.",
            },
            {
                "ma": "L05-2026-BCA-L3",
                "cay": "BCA",
                "gieo": "2025-08-20",
                "thu_tu": "2026-08-12",
                "thu_den": "2026-08-20",
                "neo": {"day": "2026-04-07", "ndvi_day": 0.357, "dinh": "2026-07-11", "ndvi_dinh": 0.799},
                "ghi_chu": "Lứa ĐANG CẮT tại thời điểm chốt dữ liệu (12/08/2026).",
            },
        ],
    },
    "L06": {
        "ten": "Khu công trình",
        "muc_dich": "cong_trinh",
        "ti_le_gieo": 0.0,
        "mo_ta": "Nhà lưới ươm, sân phơi, kho lạnh và vành cỏ quanh công trình. Không canh tác.",
        "can_cu": [
            "lot_chu_ky.csv: KHÔNG dò được vụ nào trong 12 tháng — lô duy nhất cùng L09 rơi vào nhóm này.",
            "lots_summary.csv: phân loại tự động 'Che phủ thưa / đất trống, công trình'; độ dốc 3,88° — dốc nhất farm, dạng nền san.",
            "lot_ndvi_wide.csv: NDVI dao động 0,207–0,547 nhưng không theo dạng gieo–lớn–thu; phần dao động là vành cỏ quanh công trình.",
        ],
        "vu": [],
    },
    "L07": {
        "ten": "Vườn chanh lớn",
        "muc_dich": "luu_nien",
        "ti_le_gieo": 0.88,
        "mo_ta": "Lô lớn nhất farm (1,91 ha), vườn chanh lưu niên trồng trước kỳ quan trắc.",
        "can_cu": [
            "lots_summary.csv: NDMI 0,318 — CAO NHẤT farm, gấp gần 3 lần trung bình. VH −13,07 dB, tán dày nhất trong nhóm lô lớn.",
            "lot_ndvi_wide.csv: NDVI ≥ 0,73 ở 15/21 ngày; thấp nhất 0,326 rơi vào ngày 08/12/2025 (ngày farm mù).",
            "lot_chu_ky.csv: 2 đỉnh 'chắc' (06/10/2025, 10/03/2026) — với cây lưu niên đây là hai đợt ra lộc, KHÔNG phải hai vụ gieo. Diện tích 1,91 ha không đổi suốt kỳ.",
        ],
        "vu": [
            {
                "ma": "L07-CHA-2025",
                "cay": "CHA",
                "gieo": "2021-03-20",
                "thu_tu": "2025-09-20",
                "thu_den": "2025-11-10",
                "neo": {"day": "2025-09-16", "ndvi_day": 0.434, "dinh": "2025-10-06", "ndvi_dinh": 0.823},
                "ghi_chu": "Trồng trước kỳ quan trắc — 'khong_kiem_duoc'.",
            },
            {
                "ma": "L07-CHA-2026",
                "cay": "CHA",
                "gieo": "2021-03-20",
                "thu_tu": "2026-06-15",
                "thu_den": "2026-08-30",
                "neo": {"day": "2025-12-25", "ndvi_day": 0.337, "dinh": "2026-03-10", "ndvi_dinh": 0.729},
                "ghi_chu": "Đợt thu ĐANG CHẠY tại thời điểm chốt dữ liệu.",
            },
        ],
    },
    "L08": {
        "ten": "Thửa cải tạo Nam",
        "muc_dich": "canh_tac",
        "ti_le_gieo": 0.78,
        "mo_ta": "Thửa mới khai hoang: 2025 còn bụi cây tự nhiên, phát dọn cuối 11/2025, để nghỉ, lên luống lại giữa 2026.",
        "can_cu": [
            "lots_summary.csv: biên độ 0,65 — CAO NHẤT farm cùng L01, nhưng NDVI trung bình chỉ 0,371 (thấp nhì farm).",
            "lot_ndvi_wide.csv: 0,832 (20/08/2025) → 0,195 (20/11/2025) → giữ 0,18–0,29 suốt 8 tháng → 0,511 (10/08/2026). Một lần rơi rồi phẳng dài — dạng phát dọn, không phải dạng thu hoạch theo vụ.",
            "lot_tinh_trang.csv: lệch so với mặt bằng farm −0,130 (kém nhất farm), xu hướng cuối kỳ +0,104/tháng.",
        ],
        "vu": [
            {
                "ma": "L08-2026-BCA",
                "cay": "BCA",
                "gieo": "2026-07-05",
                "thu_tu": "2026-10-10",
                "thu_den": "2026-10-20",
                "neo": {"day": "2026-06-21", "ndvi_day": 0.277, "dinh": None, "ndvi_dinh": None},
                "ghi_chu": "Vụ ĐANG CHẠY. Trước đó lô nghỉ từ 25/11/2025.",
            },
        ],
        "moc_dac_biet": [
            {"ngay": "2025-11-25", "viec": "Phát dọn bụi cây, thu gom sinh khối", "can_cu": "NDVI 0,825 (20/11 lô L04 tham chiếu) — lô L08 rơi từ 0,586 (13/11) xuống 0,195 (20/11)"},
            {"ngay": "2026-01-15", "viec": "Bón lót phân chuồng hoai, để đất nghỉ", "can_cu": "NDVI phẳng 0,24–0,28 suốt 01–06/2026"},
            {"ngay": "2026-06-28", "viec": "Lên luống, rải vôi", "can_cu": "NDVI bắt đầu lên từ 0,277 (21/06) → 0,414 (11/07)"},
        ],
    },
    "L09": {
        "ten": "Thửa nghỉ luân canh",
        "muc_dich": "dat_nghi",
        "ti_le_gieo": 0.70,
        "mo_ta": "Đang trong chu kỳ nghỉ đất; gieo đậu che phủ vào mùa mưa để giữ đất và cố định đạm.",
        "can_cu": [
            "lot_chu_ky.csv: KHÔNG dò được vụ nào — thảm xanh không theo lịch canh tác.",
            "lot_tinh_trang.csv: chênh NDVI mùa mưa − mùa khô = +0,251, LỚN NHẤT farm; NDMI mùa mưa 0,231 so với mùa khô 0,022. Thảm đi theo mưa chứ không theo người.",
            "lot_tinh_trang.csv: trạng thái cuối kỳ 'ổn định', xu hướng −0,012/tháng.",
        ],
        "vu": [
            {
                "ma": "L09-2026-DAU",
                "cay": "DAU",
                "gieo": "2026-05-20",
                "thu_tu": "2026-09-05",
                "thu_den": "2026-09-10",
                "neo": {"day": "2026-04-07", "ndvi_day": 0.306, "dinh": "2026-07-11", "ndvi_dinh": 0.749},
                "ghi_chu": "Không thu sản phẩm — cày vùi làm phân xanh. 'Thu' ở đây là ngày cày vùi (kế hoạch).",
            }
        ],
    },
    "L10": {
        "ten": "Vườn ươm + luống cúc đông",
        "muc_dich": "vuon_uom",
        "ti_le_gieo": 0.62,
        "mo_ta": "Luống ươm cây giống xen luống cúc vụ đông; nhiều lối đi và lưới che nên nền xanh luôn thấp.",
        "can_cu": [
            "lot_tinh_trang.csv: NDVI mùa KHÔ 0,407 > mùa MƯA 0,363 (chênh −0,044). Chỉ L10 và L12 có dấu hiệu này → hoạt động dồn vào mùa khô, ngược với thảm tự nhiên.",
            "lot_chu_ky.csv: 2 đỉnh — 20/11/2025 (0,563) và 10/03/2026 (0,526), cả hai đều thấp: có cây nhưng che phủ không kín.",
            "lots_area.csv: sai lệch diện tích +31,0 % — LỚN NHẤT farm. Lô nhỏ nhiều lối đi, nét vẽ tay lệch nhiều nhất.",
        ],
        "vu": [
            {
                "ma": "L10-2025-CUC",
                "cay": "CUC",
                "gieo": "2025-09-20",
                "thu_tu": "2025-11-25",
                "thu_den": "2025-12-05",
                "neo": {"day": "2025-09-16", "ndvi_day": 0.199, "dinh": "2025-11-20", "ndvi_dinh": 0.563},
                "ghi_chu": "Vụ muộn, gieo bằng cây giống ươm sẵn nên chu kỳ ngắn hơn L01.",
            },
            {
                "ma": "L10-2026-UOM",
                "cay": "UOM",
                "gieo": "2026-01-05",
                "thu_tu": "2026-03-15",
                "thu_den": "2026-03-20",
                "neo": {"day": "2025-12-25", "ndvi_day": 0.187, "dinh": "2026-03-10", "ndvi_dinh": 0.526},
                "ghi_chu": "'Thu' = ngày xuất cây giống sang lô khác.",
            },
        ],
    },
    "L11": {
        "ten": "Luống rau thuốc cắt lứa",
        "muc_dich": "canh_tac",
        "ti_le_gieo": 0.84,
        "mo_ta": "Bồ công anh và rau thuốc cắt nhiều lứa ngắn — cắt xong tái sinh từ gốc.",
        "can_cu": [
            "lot_chu_ky.csv: 2 'vụ' dò được chỉ dài 25 ngày và 10 ngày — quá ngắn cho một vụ gieo–thu, đúng dạng cắt rồi tái sinh.",
            "lots_summary.csv: NDVI trung bình 0,569 (cao thứ ba farm) nhưng biên độ chỉ 0,434 — nền xanh không bao giờ về đất trống.",
            "lot_tinh_trang.csv: xu hướng cuối kỳ −0,052/tháng, 'đang xuống — thu hoạch hoặc suy giảm'.",
        ],
        "vu": [
            {"ma": "L11-2025-BCA-L1", "cay": "BCA", "gieo": "2025-06-15", "thu_tu": "2025-10-06", "thu_den": "2025-10-12",
             "neo": {"day": "2025-09-11", "ndvi_day": 0.524, "dinh": "2025-10-06", "ndvi_dinh": 0.730}, "ghi_chu": None},
            {"ma": "L11-2025-BCA-L2", "cay": "BCA", "gieo": "2025-06-15", "thu_tu": "2025-12-20", "thu_den": "2025-12-24",
             "neo": {"day": "2025-12-10", "ndvi_day": 0.360, "dinh": "2025-12-20", "ndvi_dinh": 0.583}, "ghi_chu": "Lứa ngắn 10 ngày lên — cắt non."},
            {"ma": "L11-2026-BCA-L3", "cay": "BCA", "gieo": "2025-06-15", "thu_tu": "2026-03-20", "thu_den": "2026-03-26",
             "neo": {"day": "2026-04-07", "ndvi_day": 0.392, "dinh": "2026-03-13", "ndvi_dinh": 0.568}, "ghi_chu": None},
            {"ma": "L11-2026-BCA-L4", "cay": "BCA", "gieo": "2025-06-15", "thu_tu": "2026-08-05", "thu_den": "2026-08-11",
             "neo": {"day": "2026-06-21", "ndvi_day": 0.488, "dinh": "2026-07-11", "ndvi_dinh": 0.602}, "ghi_chu": "Lứa ĐANG CẮT tại thời điểm chốt dữ liệu."},
        ],
    },
    "L12": {
        "ten": "Ruộng lớn Tây",
        "muc_dich": "canh_tac",
        "ti_le_gieo": 0.80,
        "mo_ta": "Cúc chi vụ chính mỗi năm một vụ, giữa hai vụ để đất nghỉ.",
        "can_cu": [
            "lot_chu_ky.csv: 1 vụ 'chắc' — đáy 17/08/2025 (0,366) → đỉnh 10/11/2025 (0,731), 85 ngày lên. Đúng chu kỳ cúc chi.",
            "lot_ndvi_wide.csv: 0,722 (20/11/2025) → 0,636 (23/11) → 0,243 (08/12/2025). Tụt 0,49 điểm trong 15 ngày — dạng thu hoạch.",
            "lot_tinh_trang.csv: NDVI mùa khô 0,461 > mùa mưa 0,385 (chênh −0,077) — canh tác dồn vào mùa khô.",
            "lot_tinh_trang.csv: xu hướng cuối kỳ +0,069/tháng, 'đang lên xanh' → vụ 2026 đã xuống giống.",
        ],
        "vu": [
            {
                "ma": "L12-2025-CUC",
                "cay": "CUC",
                "gieo": "2025-08-05",
                "thu_tu": "2025-11-15",
                "thu_den": "2025-12-06",
                "neo": {"day": "2025-08-17", "ndvi_day": 0.366, "dinh": "2025-11-10", "ndvi_dinh": 0.731},
                "ghi_chu": None,
            },
            {
                "ma": "L12-2026-CUC",
                "cay": "CUC",
                "gieo": "2026-07-25",
                "thu_tu": "2026-11-25",
                "thu_den": "2026-12-03",
                "neo": {"day": "2026-06-01", "ndvi_day": 0.275, "dinh": None, "ndvi_dinh": None},
                "ghi_chu": "Vụ ĐANG CHẠY — NDVI 0,381 ngày 10/08/2026.",
            },
        ],
    },
}

# Ngày KHÔNG được đọc như sự kiện đồng ruộng.
# Tiêu chí: NDVI trung vị 12 lô hụt >= 0,15 so với trung vị nền cửa sổ +/-45 ngày,
# hoặc số lô có pixel quang <= 3. Tính lại được bằng scripts/sinh_du_lieu.py.
NGAY_DANG_NGO = {
    "2025-09-14": {"ly_do": "mu_khi_quyen", "hut": 0.279, "so_lo": 9},
    "2025-12-08": {"ly_do": "mu_khi_quyen", "hut": 0.244, "so_lo": 10},
    "2025-12-23": {"ly_do": "mu_khi_quyen_va_thua_lo", "hut": 0.254, "so_lo": 2},
    "2026-01-12": {"ly_do": "thua_lo", "hut": -0.019, "so_lo": 2},
}

# 07–12/04/2026 KHÔNG nằm trong danh sách trên: đó là đáy HẠN THẬT, không phải mù.
# Hụt trung vị chỉ 0,077–0,134 và cả 12 lô đều có pixel quang.
DOT_HAN_2026_04 = {
    "tu": "2026-03-30", "den": "2026-04-16",
    "so_ngay_mua_duoi_1mm": 18,
    "can_bang_nuoc_thang_mm": -46.3,
    "et0_thang_mm": 125.2,
    "tmax_thang_c": 38.7,
    "so_lo_sut_tren_0_10": 8,
    "sut_ndvi_trung_binh": -0.134,
}

KY_DU_LIEU = {"tu": "2025-08-12", "den": "2026-08-12"}
