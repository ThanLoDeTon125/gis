# Dữ liệu GIS theo lô — RiTi Organic Farm | Tràng An

12 lô do **chủ farm tự vạch** trên bản đồ (`map mới.pdf`), quanh toạ độ
**20.2579952 N, 105.854332 E** (Trường Yên, Hoa Lư, Ninh Bình).
Kỳ dữ liệu: **12/08/2025 – 12/08/2026** (12 tháng).

| Chỉ tiêu | Giá trị |
|---|---|
| Số lô | **12** (theo bản vẽ của chủ farm) |
| Diện tích sau hiệu chỉnh | **8,846 ha** — nét vẽ tay cho 8,624 ha, chênh **+0,222 ha (+2,6 %)** |
| Lô nhỏ nhất / lớn nhất | 0,206 ha (lô 4) / 1,908 ha (lô 7) |
| Ảnh quang học | 88 lượt bay Sentinel-2 → **24 ngày** có pixel quang (23 ngày đủ dùng ở mức lô) |
| Ảnh radar | 57 lượt bay Sentinel-1 → **57 ngày, không lượt nào bị mây loại** |
| Bản ghi lô × ngày | **249** (quang học) + **684** (radar) |
| Khí hậu | 366 ngày liên tục |
| Sai số ranh giới | **±2,9 m** (kiểm bằng nguồn độc lập) |
| Hệ toạ độ | EPSG:4326 (lưu trữ) / EPSG:32648 – UTM 48N (tính diện tích) |

Toàn bộ nguồn dữ liệu **miễn phí, không cần khoá API**.

---

## 1. Sản phẩm chính

| File | Nội dung |
|---|---|
| **`BaoCao_TinhTrang_VungTrong_12Thang.docx`** | **Báo cáo tình trạng vùng trồng** — 13 chương, 10 bảng, 14 hình: diễn biến cả năm, chu kỳ vụ từng lô, nước, sức khoẻ, hiện trạng, khuyến nghị |
| `BaoCao_RiTi_Farm_12_lo.docx` | Báo cáo kỹ thuật — phương pháp, nguồn, số liệu gốc (10 chương, 7 bảng, 8 hình) |
| `data/out/lot_chu_ky.csv` | 17 vụ dò được: ngày đáy, ngày đỉnh, số ngày lên, độ tin cậy |
| `data/out/lot_tinh_trang.csv` | Tình trạng mỗi lô: NDVI theo mùa, lệch so với farm, xu hướng, trạng thái cuối kỳ |
| `data/out/nuoc_theo_thang.csv` | Mưa, ET0, cân bằng nước, độ ẩm đất 3 tầng theo tháng |
| `data/out/lots.geojson` · `lots_area.csv` | 12 lô: diện tích vẽ tay, diện tích đã nắn, mức chênh |
| `data/out/lot_s2_timeseries.csv` | **249 bản ghi lô × ngày**: NDVI, NDMI, % diện tích quang |
| `data/out/lot_s1_timeseries.csv` | **684 bản ghi lô × ngày**: VV, VH (dB), RVI, hướng bay |
| `data/out/lot_ndvi_wide.csv` | Bảng ngang: hàng = ngày, cột = 12 lô (dán thẳng vào Excel) |
| `data/out/lots_summary.csv` | Tổng hợp mỗi lô: diện tích, NDVI tb/min/max, biên độ, radar, cao độ, độ dốc, phân loại |
| `data/out/aoi_riti.gpkg` | GeoPackage 2 lớp: `aoi` (ranh giới farm), `lots` (12 lô) |
| `images/` | Toàn bộ hình của báo cáo |

### Thư mục `images/`

```
01_kiem_nan_ranh_gioi.png      vàng = nét vẽ tay, lam = sau khi nắn (4 khung phóng to)
02_ndvi_va_mua_12_thang.png    NDVI toàn farm + mưa ngày, chung trục thời gian
10_ban_do_12_lo.png            bản đồ 12 lô, tô theo NDVI trung bình
12_chuoi_ndvi_tung_lo.png      12 khung nhỏ — chuỗi NDVI riêng của từng lô
13_nhiet_do_lo_theo_thang.png  bảng nhiệt lô × tháng: NDVI (trên) và radar VH (dưới)
14_radar_sentinel1.png         VH toàn farm, tách theo hướng bay
15_mat_do_du_lieu.png          số ngày có dữ liệu mỗi tháng, quang học vs radar
16_chu_ky_canh_tac.png         đỉnh vụ trên chuỗi NDVI từng lô, có đánh dấu khoảng mù
17_can_bang_nuoc.png           mưa vs ET0 theo tháng + cân bằng nước
18_do_am_dat.png               độ ẩm đất 3 tầng + chuỗi ngày không mưa
19_lech_so_voi_farm.png        lô nào hơn/kém mặt bằng chung, đều hay từng lúc
20_dia_hinh_do_doc.png         cao độ và độ dốc
21_mua_kho_mua_mua.png         NDVI mùa khô so với mùa mưa từng lô
22_ndmi_theo_thang.png         ẩm trong tán lá — dấu hiệu thiếu nước sớm hơn NDVI
23_hien_trang_cuoi_ky.png      bản đồ hiện trạng lần quan trắc cuối
99_ban_ve_goc_12_lo.png        bản vẽ gốc của chủ farm
```

---

## 2. Kết quả chính

### Hiệu chỉnh diện tích

Nét vẽ tay lệch mép thửa thật vài mét. Với lô nhỏ, vài mét đó là vài chục phần
trăm diện tích:

| Lô | Vẽ tay (ha) | Đã nắn (ha) | Chênh |
|---|---|---|---|
| 10 | 0,263 | 0,344 | **+31,0 %** |
| 4 | 0,162 | 0,206 | **+26,9 %** |
| 8 | 0,226 | 0,250 | +10,6 % |
| 2 | 0,849 | 0,917 | +8,1 % |
| … | … | … | … |
| 7 | 1,908 | 1,908 | 0,0 % |
| **Tổng** | **8,624** | **8,846** | **+2,6 %** |

Lô lớn gần như không đổi (nét dài, sai số hai bên bù nhau); lô nhỏ đổi mạnh.
Xem `images/01_kiem_nan_ranh_gioi.png` để đối chiếu tận mắt.

### Dữ liệu theo lô

| Lô | ha | NDVI tb | Biên độ | Phân loại |
|---|---|---|---|---|
| 7 | 1,908 | 0,72 | 0,58 | Luân canh rõ |
| 1 | 1,750 | 0,43 | 0,65 | Luân canh rõ |
| 12 | 1,203 | 0,41 | 0,49 | Luân canh rõ |
| 2 | 0,917 | 0,48 | 0,35 | Che phủ trung bình |
| 3 | 0,811 | 0,48 | 0,50 | Luân canh rõ |
| 9 | 0,520 | 0,47 | 0,59 | Luân canh rõ |
| 11 | 0,423 | 0,57 | 0,43 | Che phủ trung bình |
| 10 | 0,344 | 0,38 | 0,44 | Che phủ thưa / đất trống |
| 5 | 0,263 | 0,58 | 0,54 | Luân canh rõ |
| 6 | 0,251 | 0,38 | 0,34 | Che phủ thưa / đất trống |
| 8 | 0,250 | 0,37 | 0,65 | Luân canh rõ |
| 4 | 0,206 | 0,72 | 0,56 | Luân canh rõ |

Nhãn suy từ **dạng chuỗi 12 tháng**, không phải từ chênh lệch hai ngày.

### Mật độ dữ liệu

Tháng 02/2026 **không có một ngày quang học nào** — radar vẫn có 4 ngày. Đó là
lý do có Sentinel-1 trong pipeline: 57/57 lượt bay đều dùng được.

### Khí hậu 12 tháng

2.347 mm mưa so với 1.174 mm bốc thoát hơi → cân bằng nước **+1.172 mm**.
Nhiệt độ 9,7–38,7 °C. Mưa dồn vào tháng 8–10 và 5–7; tháng 1–3 khô rõ rệt.
Đất thịt pha sét (32,4 % sét · 39,0 % limon · 28,6 % cát), pH 5,9,
hữu cơ 27,7 g/kg, CEC 22 cmol(c)/kg.

---

## 3. Ranh giới lô được dựng thế nào

### Đọc nét vẽ từ PDF

Chủ farm vạch 12 lô bằng công cụ vẽ rồi xuất PDF. Nét nằm trong PDF dưới dạng
**đường vector**, không bị nướng vào ảnh — nên toạ độ đọc thẳng từ vector, chính
xác tuyệt đối. Dò lại nét trắng trên ảnh raster thì kém hơn nhiều: nét vẽ lẫn với
mái nhà lưới trắng và chữ nhãn của Google.

27 nét → hàn khe hở đầu nét → 12 vùng kín. Số lô đọc từ chính chữ số trong bản vẽ
rồi chiếu vào vùng chứa nó, không gán tay.

### Gắn toạ độ

Ảnh chụp màn hình không mang toạ độ. Phép biến đổi pixel → WGS84 xác định **tự
động** bằng tương quan chéo chuẩn hoá (NCC) với ảnh nền Esri World Imagery. Cả
hai ảnh lọc thông cao trước để bám **cạnh** thay vì màu — hai ảnh khác mùa nên
màu ruộng lệch hoàn toàn.

```
tỉ lệ chốt = 0,4060 m/pixel     đỉnh NCC = 0,170
kiểm chứng: ghim RiTi (lấy từ URL Google Maps, không tham gia georeference)
            rơi cách vị trí suy ra 2,9 m
```

### Nắn về mép thật

**Phân thuỷ có mầm** trên bản đồ độ dốc sáng của ảnh:

```
mầm       = mỗi lô co vào 12 px (~5 m), cả vùng ngoài farm cũng co vào
dải trống = vành ±12 px quanh nét vẽ — chính là biên độ cho phép dịch
phân thuỷ = biên chạy về sống núi độ dốc (mép ruộng, mép đường) trong dải đó
```

Chạy trên cả 12 lô cùng lúc chứ **không nắn từng lô riêng** — cạnh chung giữa hai
lô kề nhau phải dịch cùng nhau, nếu không mọi cạnh chung đều đẻ ra khe hở và
chồng lấn. Vì mầm giữ nguyên định danh lô nên tô pô không đổi.

---

## 4. Tách dữ liệu theo lô

**Lô nhỏ hơn pixel.** Lô 4 rộng 0,206 ha, ở lưới Sentinel-2 10 m chỉ khoảng 20
pixel, mà pixel ngoài rìa thì nửa trong nửa ngoài. Mỗi pixel 10 m được chia 4×4 ô
con 2,5 m, **trọng số** của pixel với lô = tỉ lệ ô con nằm trong lô. Sai số diện
tích quy đổi còn dưới 2 % thay vì cả chục phần trăm.

**Mây không phủ đều.** Có ngày lô này quang mà lô kia bị che. Từng lô tự xét: lô
nào đủ 60 % diện tích quang thì lô đó có số liệu ngày đó, thay vì vứt cả ngày.

**Radar phải lấy trung bình trên thang tuyến tính** rồi mới đổi sang dB — dB là
hàm log, lấy trung bình thẳng trên dB là sai. Hai hướng bay tách riêng vì cùng
một thửa, lượt bay lên và lượt bay xuống lệch nhau cả dB.

---

## 5. Nguồn dữ liệu

| Lớp | Nguồn | Độ phân giải |
|---|---|---|
| Ảnh đa phổ, NDVI/NDMI | Sentinel-2 L2A (ESA) qua STAC Element84 + AWS Open Data | 10 m |
| Radar VV/VH | Sentinel-1 **RTC** qua Microsoft Planetary Computer | 10 m |
| Ảnh nền phân giải cao | Ảnh chụp Google Maps do chủ farm cung cấp | 0,41 m |
| Ảnh nền tham chiếu toạ độ | Esri World Imagery (z18) | 0,56 m |
| Khí hậu | Open-Meteo (ERA5 tái phân tích + mô hình dự báo) | điểm |
| Địa hình | Copernicus GLO-30 DEM | 30 m |
| Thổ nhưỡng | SoilGrids v2.0 (ISRIC) | 250 m |

Bản RTC của Sentinel-1 đã hiệu chỉnh bức xạ và nắn theo địa hình. Bản GRD thô
trên AWS còn ở hình học nghiêng và nằm trong bucket requester-pays — phải tự nắn
bằng GCP và tự hiệu chỉnh bức xạ mới so sánh được giữa các ngày.

---

## 6. Chạy lại

```bash
cd ~/Documents/GIS_RiTi_TrangAn

.venv/bin/python scripts/fetch_basemap.py 18          # ảnh nền tham chiếu Esri
.venv/bin/python scripts/georef_image.py \
    data/raw/screenshot_clean.png data/out/georef_clean.json
.venv/bin/python scripts/parse_pdf_lots.py            # đọc nét vector từ PDF
PYTHONPATH=scripts .venv/bin/python scripts/build_lots.py   # 27 nét -> 12 vùng
PYTHONPATH=scripts .venv/bin/python scripts/snap_lots.py    # nắn + hiệu chỉnh diện tích
PYTHONPATH=scripts .venv/bin/python scripts/verify_lots.py  # hình kiểm chứng

.venv/bin/python scripts/fetch_sentinel2.py           # 88 lượt bay, 12 tháng
.venv/bin/python scripts/fetch_sentinel1.py           # 57 lượt radar
.venv/bin/python scripts/fetch_climate.py             # 366 ngày khí hậu
.venv/bin/python scripts/fetch_terrain_soil.py        # DEM, độ dốc, thổ nhưỡng

.venv/bin/python scripts/extract_lot_timeseries.py    # tách theo 12 lô
.venv/bin/python scripts/analyze_condition.py         # chu kỳ vụ, nước, sức khoẻ lô
PYTHONPATH=scripts .venv/bin/python scripts/make_lot_figures.py
PYTHONPATH=scripts .venv/bin/python scripts/make_condition_figures.py
.venv/bin/python scripts/make_report_docx.py                       # báo cáo kỹ thuật
PYTHONPATH=scripts .venv/bin/python scripts/make_report_condition.py  # báo cáo tình trạng
```

`build_lots.py` cần bản render của PDF (`data/out/_page_render.png`) để đọc chữ số:

```bash
pdftoppm -r 100 -png -singlefile "map mới.pdf" data/out/_page_render
```

Báo cáo DOCX đọc số liệu trực tiếp từ `data/out/` — **không có con số nào gõ
tay**, nên chạy lại pipeline là báo cáo tự cập nhật theo.

Đổi kỳ dữ liệu: sửa `DATE_RANGE` trong `fetch_sentinel2.py`/`fetch_sentinel1.py`
và `START`/`END` trong `fetch_climate.py`.

Môi trường Python 3.11 trong `.venv/`. Thư mục `_cu_73_lo/` giữ bản cũ — thời kỳ
farm còn được **máy tự cắt thành 73 lô** trước khi có bản vẽ 12 lô của chủ farm.

---

## 7. Giới hạn cần biết

- **Ranh giới ±2,9 m, KHÔNG phải ranh giới pháp lý.** Không dùng cho hồ sơ địa chính.
- **Ranh giới đã nắn bám mép thửa NHÌN THẤY TRÊN ẢNH**, không phải ranh giới sở
  hữu. Nếu ranh giới thật khác hiện trạng canh tác thì số liệu ở đây theo hiện trạng.
- **NDVI của lô nhỏ kém tin cậy.** 4 lô dưới 0,3 ha (L05, L06, L08, L04) chỉ chứa
  20–26 pixel Sentinel-2 và còn chịu ảnh hưởng lẫn từ lô bên cạnh.
- **Nhãn phân loại suy từ phổ ảnh**, chưa đối chiếu thực địa. NDVI cao có thể là
  vườn cây ăn quả, cũng có thể là bụi rậm — cần một lần đi thực địa để gán đúng
  cây trồng.
- **Chuỗi quang học vẫn thưa vào mùa mưa** dù đã kéo 12 tháng. Radar bù về mật độ
  nhưng nhiễu đốm nhiều hơn, phải đọc theo xu hướng chứ không đọc từng điểm.
- **Thổ nhưỡng SoilGrids ở 250 m**: cả 12 lô nằm trong cùng một ô, nên không có
  khác biệt theo lô từ nguồn này.
- **OSM không có thửa đất** ở khu vực này, nên không có nguồn vector độc lập để
  đối chiếu ranh giới lô.
