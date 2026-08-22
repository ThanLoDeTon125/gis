# 05 — Thật, mô phỏng, dẫn xuất

Luật `nguon` của `Sankit/qr` (`that` | `mau`) là cột sống của tính trung thực trong dự
án đó. Bộ này giữ nguyên luật ấy và **thêm một giá trị thứ ba**: `dan_xuat` — tính ra
từ số thật bằng một công thức viết rõ, không phải đo, cũng không phải bịa.

## Bảng phân định

| Lớp | `nguon` | Nguồn gốc | Đổi được khi nào |
|---|---|---|---|
| Ranh giới lô, diện tích, chu vi, trọng tâm | `that` | PDF chủ farm + nắn theo Esri World Imagery | khi farm vẽ lại hoặc đo GPS thực địa |
| Cao độ, độ dốc | `that` | Copernicus GLO-30 DEM | — |
| NDVI / NDMI theo lô theo ngày | `that` | Sentinel-2 L2A | mỗi 5 ngày, khi có ảnh mới |
| VV / VH / RVI theo lô theo ngày | `that` | Sentinel-1 RTC | mỗi 6–12 ngày |
| Khí hậu ngày | `that` | Open-Meteo (ERA5) | hằng ngày |
| Thổ nhưỡng | `that` ⚠ | SoilGrids v2.0, 250 m | khi có mẫu đất thật theo lô |
| Chu kỳ NDVI dò tự động | `that` | `analyze_condition.py` trên chuỗi 12 tháng | khi chuỗi dài thêm |
| 4 cá thể cây có tem | `that` | `Sankit/qr/data/cay/` | — |
| **Cây trồng của từng lô, ngày gieo, ngày thu** | `mau` | suy từ dạng chuỗi NDVI — `scripts/ke_hoach_lo.py` | **một buổi đi thực địa là gỡ được toàn bộ** |
| Nhật ký đồng ruộng, vật tư, nhân sự | `mau` | dựng theo lịch nông vụ + tháng thiếu nước THẬT | khi `sk-go` chạy và HTX nhập thật |
| Lô hàng, bịch, sản lượng | `mau` | năng suất tham chiếu × diện tích gieo THẬT | khi có phiếu cân thật |
| 88 cá thể cây mô phỏng | `mau` | rải theo số tem giả định mỗi lô | khi gắn tem thật ngoài vườn |
| Nhiệt độ bề mặt theo lô | `dan_xuat` | Tmax THẬT + che phủ từ NDVI THẬT — công thức §2 | khi kéo Landsat TIRS / Sentinel-3 LST |
| Nhu cầu nước theo lô | `dan_xuat` | ET0 THẬT × Kc FAO-56 − mưa hiệu quả THẬT | khi có Kc đo tại chỗ |
| Che phủ ước tính (%) | `dan_xuat` | NDVI THẬT qua công thức FVC | — |
| 89 cảnh báo | `dan_xuat` | luật R1–R6 chạy trên quan trắc THẬT | mỗi lần có ảnh mới |
| **Phiếu kiểm nghiệm** | `khong_co` | **cố ý để trống** | khi RiTi gửi phiếu thật |

## 2. Công thức của lớp dẫn xuất — không có chỗ nào giấu

### Che phủ thực vật (FVC)

```
FVC = clamp( (NDVI − NDVI_đất_trống) / (NDVI_tán_kín − NDVI_đất_trống), 0, 1 ) ²
NDVI_đất_trống = 0,15     ← nhỏ nhất đo được cả farm là 0,147 (L01)
NDVI_tán_kín   = 0,90     ← lớn nhất đo được cả farm là 0,905 (L07)
```

Bình phương là dạng chuẩn của phương pháp tam giác NDVI–FVC (Carlson & Ripley 1997).
Hai hằng số **lấy từ chính farm này**, không mượn từ bài báo nào.

### Nhiệt độ bề mặt ước tính

```
T_bề_mặt ≈ T_không_khí_max + 9,0 × (1 − FVC)
```

Đất trống giữa trưa nóng hơn không khí cỡ 9 °C, tán kín thì gần bằng. Đây là **ước
lượng bậc nhất, không phải đo**. Giá trị cao nhất trong bộ dữ liệu là 47,5 °C (lô đất
trống, tháng 4/2026) — con số này hợp lý cho đất trống ở Ninh Bình cuối mùa khô, nhưng
**không được trích ra như một phép đo**.

Muốn số thật: Landsat 8/9 TIRS (100 m, 16 ngày) hoặc Sentinel-3 SLSTR (1 km, hằng ngày),
cả hai miễn phí. Chưa kéo về vì 1 km quá thô cho lô 0,2 ha, còn 16 ngày thì quá thưa.

### Nhu cầu nước

```
ETc          = Kc × ET0                                    (Kc theo FAO-56, theo pha sinh trưởng)
mưa_hiệu_quả = P × (125 − 0,2·P) / 125     nếu P < 250 mm   (USDA-SCS)
             = 125 + 0,1·P                 nếu P ≥ 250 mm
thiếu        = max(0, ETc − mưa_hiệu_quả)
nước_tưới    = thiếu (mm) × 10 × diện_tích_gieo (ha)  →  m³
```

Bảng Kc dùng cho 7 loại cây nằm trong `scripts/ke_hoach_lo.py`, hằng `CAY_TRONG`.

## 3. Vì sao không có phiếu kiểm nghiệm nào

`Sankit/qr/docs/02_MO_HINH_DU_LIEU.md` đã chốt: chỗ nào chưa có văn bản của RiTi thì để
`null`, đừng đoán. Bộ này giữ nguyên. Cả 101 lô hàng đều có `kiem_nghiem: null` kèm
`ly_do_kiem_nghiem_rong`.

Lý do không phải hình thức: một trang trông y hệt hồ sơ chất lượng thật mà không ghi rõ
là mô phỏng thì vừa hỏng uy tín, vừa có thể bị coi là quảng cáo sai sự thật. Người quét
QR chụp màn hình được, gửi lại cho người khác được, quét lại sau nhiều tháng được.

## 4. Nhân sự trong nhật ký là hư cấu

Sáu người trong `data/mo_phong/nhan_su.json` **không có thật**, mỗi bản ghi mang cờ
`nhan_vat_hu_cau: true`. Có tên để giao diện dựng được cột "người thực hiện". Thay bằng
danh sách thật trước khi demo cho RiTi.

## 5. Hai bản ghi sai được cắm cố ý

`data/mo_phong/lech_co_y.json` ghi rõ hai bản ghi nhật ký cố tình sai:

1. Khai thu hoạch trên **L06** — khu công trình, không có vụ nào.
2. Khai thu hoạch trên **L09** ngày 10/02/2026, trong khi vụ đậu mãi 20/05/2026 mới gieo
   và NDVI không hề tụt.

Không có chúng thì bảng cảnh báo loại R5 gần như trống, vì lịch mô phỏng vốn được suy
TỪ đường NDVI nên tự khớp. Xoá hai bản ghi này là mất nội dung để dựng màn hình.

## 6. Cách kiểm bộ dữ liệu này

```bash
python3 scripts/sinh_du_lieu.py          # sinh lại — kết quả y hệt mỗi lần chạy
```

Mọi mã `SK-L-…`, `SK-B-…`, `SK-C-…` trong bộ đều đi qua được trình kiểm tra thật của
Sankit:

```bash
python3 - <<'EOF'
import json, sys
sys.path.insert(0, '/Users/trinhquocbao/Documents/Sankit/qr/tools')
import ma_dinh_danh as md
ds = sum((json.load(open(f'data/mo_phong/{f}.json')) for f in ('lo_hang','bich','cay_ca_the')), [])
xau = [x['id'] for x in ds if not md.hop_le(x['id'])]
print('mã sai:', xau or 'không có')
EOF
```
