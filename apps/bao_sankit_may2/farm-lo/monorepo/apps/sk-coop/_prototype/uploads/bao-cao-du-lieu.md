# Báo cáo dữ liệu — Mô hình kiểm soát farm theo lô

**RiTi Organic Farm · Trường Yên, Hoa Lư, Ninh Bình · kỳ 12/08/2025 – 12/08/2026**

Tài liệu này gộp ba thứ đang rời nhau thành một mô hình:

| Đang có | Là gì | Thiếu gì |
|---|---|---|
| `GIS_RiTi_TrangAn` | 12 lô đất có ranh giới đo được, 933 bản ghi vệ tinh, 366 ngày khí hậu | không biết lô đó **trồng gì**, ai làm gì trên đó |
| `Sankit/qr` | truy xuất nguồn gốc cây → bịch → lô hàng, đã chạy thật trên `sankitvn.site` | không biết mảnh đất sinh ra lô hàng đó **ở đâu và tình trạng ra sao** |
| `sankitmono` | khung chạy được: 3 app, 4 package, chưa có nghiệp vụ nào | chưa có mô hình miền để đổ vào |

Chỗ nối là **`lo_id`**. GIS đánh số lô `L01`–`L12`. Hồ sơ cây trong `Sankit/qr` khai
`vi_tri.khu` bằng đúng những chuỗi đó, và cấu trúc mã cây `SK-C-CUC25-**L01**-0007-P`
đã dành sẵn 3 ký tự cho khu. **Không phải sửa mã nào, không phải di trú dữ liệu nào.**

---

## 1. Cái mà mô hình này làm được, còn QR hiện tại thì không

Trang QR hiện tại trả lời *"bịch trà này từ đâu ra"*. Nó lấy câu trả lời từ **lời khai
của farm**. Không có gì kiểm chứng lời khai đó.

Ghép GIS vào thì mỗi lô hàng mang theo **trạng thái đo được của mảnh đất trong suốt vụ**:
NDVI lúc thu hoạch, tổng mưa, tổng ET0, GDD tích luỹ, các đợt hạn đã đi qua. Và quan
trọng hơn: **ảnh vệ tinh trở thành bên thứ ba đối chiếu nhật ký đồng ruộng.**

Chạy phép đối chiếu đó trên 22 đợt thu hoạch đã có nhật ký (trong tổng số 25 đợt):

| Kết quả | Số đợt | Nghĩa |
|---|---:|---|
| `xac_nhan` | 7 | NDVI tụt đúng mức mà loại cây đó phải tụt |
| `xac_nhan_bang_radar` | 3 | ảnh quang không thấy, nhưng VH radar thấy |
| `can_nguoi_xac_minh` | 3 | cả quang lẫn radar đều không đổi — có chuyện |
| `chua_ket_luan_duoc` | 5 | không có ảnh ở một phía của mốc thu hoạch |
| `khong_ap_dung` | 4 | hái quả trên cây lưu niên — vệ tinh không kiểm được |

Đây là thứ bán được cho bên mua sỉ và cho tổ chức chứng nhận hữu cơ: **không phải "farm
nói vậy", mà "farm nói vậy và ảnh vệ tinh độc lập cũng nói vậy".**

---

## 2. Bốn ca kiểm chứng chéo — số thật, không dựng

### 2.1 Hồ sơ cây thật khớp đường NDVI thật

Hồ sơ `SK-C-CUC25-L01-0007-P` trong `Sankit/qr/data/cay/` khai: cúc chi, **khu L01**,
xuống giống 10/07/2025, **thu hái 18/11/2025**. Không ai gõ số này từ ảnh vệ tinh —
nó có trước, do farm khai.

Đường NDVI của lô L01 trong GIS, đo độc lập từ Sentinel-2:

```
04/10/2025   0,7384      đỉnh vụ
13/11/2025   0,4117
20/11/2025   0,3458      ← hồ sơ khai thu hái 18/11
23/11/2025   0,3070
18/12/2025   0,3145      đáy
```

Sụt **−0,424** vắt qua đúng mốc thu hoạch được khai.

**Nghĩa là:** lô `L01` trong GIS và khu `L01` trong hồ sơ cây là **cùng một mảnh đất**,
và đồng hồ của hai hệ thống chạy khớp nhau. Đây là cơ sở kỹ thuật để ghép bằng `lo_id`.

**KHÔNG nghĩa là:** không phải bằng chứng nhân quả. Ba cây có tem chỉ cho 1,24 kg hoa
tươi — không đủ làm nhúc nhích NDVI của 1,7496 ha. Cú tụt đó là thu hoạch quy mô cả lô.

### 2.2 Một lần thu hoạch THẬT mà ảnh quang KHÔNG thấy

Hồ sơ `SK-C-CUC25-L02-0003-3` khai thu hái **20/11/2025** ở khu **L02**. NDVI lô L02:
0,4927 (20/11) → 0,4380 (23/11) → 0,5306 (18/12). Đỉnh–đáy chỉ **+0,038**. Không thấy gì.

Radar Sentinel-1 thì thấy: VH đổi **−0,74 dB**, qua ngưỡng −0,5 dB.

**Cách giải thích khớp nhất:** cúc chi chỉ chiếm khoảng một phần ba lô L02 (0,92 ha),
phần còn lại là cúc cổ lưu gốc — nên trung bình NDVI cả lô không nhúc nhích. Đúng với
việc L02 có **biên độ NDVI nhỏ nhất farm (0,348)** trong khi vẫn có 2 chu kỳ dò được.

**Bài học cho mô hình dữ liệu:** `lô` là đơn vị quá thô. Phải có tầng **`khoảnh`/`luống`**
bên dưới. Xem [docs/01_MO_HINH_MIEN.md](docs/01_MO_HINH_MIEN.md) §3.

**Bài học cho kiến trúc:** đừng bỏ Sentinel-1. Đây là ca radar cứu được kết luận.

### 2.3 Đợt hạn tháng 4/2026 — luật cảnh báo bắt đúng, cách tính tháng thì trượt

Khí hậu thật: **18 ngày liên tiếp mưa dưới 1 mm, từ 30/03/2026**. Tháng 4/2026 có ET0
cao nhất năm (125,2 mm), cân bằng nước âm nhất năm (−46,3 mm), Tmax 38,7 °C.

Ảnh vệ tinh thật, cùng lúc đó: **8/12 lô sụt NDVI hơn 0,10**, trung bình −0,134.
Nặng nhất là hai vườn chanh — L04 **−0,318**, L07 **−0,286**.

Nhưng nếu tính cân bằng nước **theo tháng** thì L04 và L07 chỉ hụt 18,7 mm — **dưới
ngưỡng, không báo động**. Vì đợt hạn 18 ngày vắt qua hai tháng nên bị chia đôi và biến mất.

Chuyển sang **cửa sổ trượt 15 ngày trên khí hậu ngày**, L07 lập tức ra cảnh báo mức
`cao`: *hụt 51 mm trong 15 ngày (30/03 → 17/04)*. Đó là lý do luật R1 trong bộ này chạy
theo ngày, không theo tháng. Xem [docs/04_LUAT_CANH_BAO.md](docs/04_LUAT_CANH_BAO.md).

### 2.4 Luật bắt được lỗi của chính người viết lịch mô phỏng

Lịch canh tác mô phỏng ban đầu đặt vụ lạc L01 thu hoạch 02–08/07/2026. Luật R2 lập tức
báo: *NDVI tụt 0,741 (06/06) → 0,298 (21/06) mà nhật ký không ghi việc gì.*

Ảnh đúng, lịch sai. Vụ thu thật rơi vào **giữa tháng 6**, không phải đầu tháng 7 — và
gieo 05/02 + ~130 ngày cũng ra giữa tháng 6. Lịch đã được sửa lại theo ảnh.

Ghi lại ca này vì nó cho thấy vòng lặp mà sản phẩm phải chạy được: **ảnh sửa lời khai,
không phải lời khai sửa ảnh.**

---

### 2.5 Trình kiểm tra bắt được một lỗi mô hình

Bất biến I4 — *hai vụ chồng thời gian trên cùng một lô thì tổng tỉ lệ gieo không được
quá 1* — bắn đỏ 12 cặp ở lần chạy đầu.

Nguyên nhân: **`vụ` và `đợt thu hoạch` đang bị gộp làm một.** Cúc chi hái nhiều lượt vì
hoa nở dần; bồ công anh cắt bốn lứa trên cùng gốc; chanh lưu niên thu quả năm này qua
năm khác. Coi mỗi lượt hái là một "vụ" thì L11 hoá ra có bốn vụ chồng lên nhau trên
cùng 0,423 ha.

Đã tách thành hai thực thể: **18 vụ · 25 đợt thu**. Kèm một luật nữa — cây lưu niên
*không* mặc nhiên chiếm lô mãi mãi: nếu lô đã được gieo thứ khác sau đợt thu cuối thì
vụ đó đã kết thúc (trường hợp bồ công anh vụ đông ở L03, xong là nhường chỗ cho lạc xuân).

Ghi lại vì đây là loại lỗi mà đội web sẽ đâm vào ở ticket đầu tiên nếu không tách sẵn.

---

## 3. Dữ liệu thật đang có

| Lớp | Số lượng | Nguồn | Độ phân giải |
|---|---:|---|---|
| Ranh giới lô | 12 lô · 8,8458 ha | PDF vẽ tay của chủ farm, nắn theo Esri World Imagery | ±2,9 m |
| NDVI / NDMI theo lô theo ngày | **249** bản ghi · 22 ngày dùng được | Sentinel-2 L2A (ESA) | 10 m |
| Radar VV/VH theo lô theo ngày | **684** bản ghi · 57 ngày, không ngày nào bị mây loại | Sentinel-1 RTC | 10 m |
| Khí hậu ngày | **366** ngày liên tục | Open-Meteo (ERA5) | điểm |
| Địa hình | cao độ 8,41–13,42 m · độ dốc 0,26–3,92° | Copernicus GLO-30 DEM | 30 m |
| Thổ nhưỡng | sét 32,4 % · limon 39,0 % · cát 28,6 % · pH 5,9 · OC 27,7 g/kg · CEC 22 | SoilGrids v2.0 | 250 m ⚠ |
| Chu kỳ NDVI dò tự động | 17 vụ, 12 vụ mức "chắc" | tính trên chuỗi 12 tháng | — |

⚠ SoilGrids ở 250 m: **cả 12 lô nằm trong cùng một ô**. Nguồn này không phân biệt được
lô với lô. Muốn có thổ nhưỡng theo lô thì phải lấy mẫu đất thật.

### Khí hậu và mật độ ảnh theo tháng

| Tháng | NDVI farm | Mưa mm | ET0 mm | Cân bằng mm | Tmax °C | Tmin °C | Ngày có ảnh quang |
|---|---:|---:|---:|---:|---:|---:|---:|
| 2025-08 | 0.592 | 422.4 | 56.7 | +365.7 | 33.5 | 23.0 | 2 |
| 2025-09 | 0.503 | 454.7 | 104.2 | +350.5 | 34.8 | 23.0 | 1 |
| 2025-10 | 0.565 | 247.1 | 94.0 | +153.1 | 32.8 | 17.2 | 1 |
| 2025-11 | 0.539 | 97.5 | 78.3 | +19.2 | 29.0 | 11.8 | 3 |
| 2025-12 | 0.490 | 78.1 | 67.4 | +10.7 | 28.3 | 12.5 | 1 |
| 2026-01 | — | 33.5 | 69.7 | -36.2 | 27.0 | 9.7 | 0 |
| 2026-02 | — | 38.2 | 58.0 | -19.8 | 29.0 | 11.9 | 0 |
| 2026-03 | 0.470 | 57.8 | 86.8 | -29.0 | 36.5 | 14.7 | 1 |
| 2026-04 | 0.347 | 78.9 | 125.2 | -46.3 | 38.7 | 21.1 | 2 |
| 2026-05 | 0.563 | 212.8 | 129.3 | +83.5 | 37.5 | 20.0 | 1 |
| 2026-06 | 0.541 | 196.3 | 137.8 | +58.5 | 38.0 | 23.1 | 3 |
| 2026-07 | 0.536 | 305.9 | 118.9 | +187.0 | 35.1 | 23.7 | 3 |
| 2026-08 | 0.609 | 123.5 | 48.2 | +75.3 | 35.8 | 24.5 | 1 |


Tháng **01/2026 và 02/2026 không có ngày ảnh quang nào dùng được** — 01/2026 có một
ngày nhưng chỉ 2/12 lô đủ pixel quang, đã loại. Radar vẫn có mặt suốt. Đó là lý do
Sentinel-1 nằm trong pipeline chứ không phải để cho đủ món.

---

## 4. Dữ liệu mô phỏng — lô nào trồng gì, từ tháng nào

Toàn bộ lịch dưới đây là **mô phỏng**, nhưng **không có mốc nào đặt tuỳ ý**. Mỗi vụ đều
neo vào một con số cụ thể trong dữ liệu thật, ghi trong `scripts/ke_hoach_lo.py` ở trường
`can_cu`. Ba ngày gieo được lấy thẳng từ hồ sơ cây thật của Sankit.

| Lô | 25/08 | 25/09 | 25/10 | 25/11 | 25/12 | 26/01 | 26/02 | 26/03 | 26/04 | 26/05 | 26/06 | 26/07 | 26/08 |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| **L01** | CÚC∙ | CÚC● | CÚC▼ | CÚC▼ | · | · | LẠC˙ | LẠC∙ | LẠC● | LẠC● | LẠC▼ | CÚC˙ | CÚC˙ |
| **L02** | CÚC∙ | CÚC∙ | CÚC● | CÚC▼ | CÚC▼ | cổ● | cổ● | cổ▼ | · | · | · | · | · |
| **L03** | · | · | BCA˙ | BCA∙ | BCA▼ | · | LẠC˙ | LẠC∙ | LẠC∙ | LẠC● | LẠC▼ | LẠC▼ | CÚC∙ |
| **L04** | chanh● | chanh▼ | chanh▼ | chanh▼ | chanh● | chanh● | chanh● | chanh● | chanh● | chanh▼ | chanh▼ | chanh▼ | chanh▼ |
| **L05** | BCA˙ | BCA∙ | BCA● | BCA▼ | BCA● | BCA● | BCA● | BCA▼ | BCA● | BCA● | BCA● | BCA● | BCA▼ |
| **L06** | ▨ | ▨ | ▨ | ▨ | ▨ | ▨ | ▨ | ▨ | ▨ | ▨ | ▨ | ▨ | ▨ |
| **L07** | chanh● | chanh▼ | chanh▼ | chanh▼ | chanh● | chanh● | chanh● | chanh● | chanh● | chanh● | chanh▼ | chanh▼ | chanh▼ |
| **L08** | · | · | · | · | · | · | · | · | · | · | · | BCA˙ | BCA∙ |
| **L09** | · | · | · | · | · | · | · | · | · | đậu˙ | đậu∙ | đậu∙ | đậu● |
| **L10** | · | CÚC˙ | CÚC∙ | CÚC▼ | CÚC▼ | ươm˙ | ươm● | ươm▼ | · | · | · | · | · |
| **L11** | BCA∙ | BCA● | BCA▼ | BCA● | BCA▼ | BCA● | BCA● | BCA▼ | BCA● | BCA● | BCA● | BCA● | BCA▼ |
| **L12** | CÚC˙ | CÚC∙ | CÚC● | CÚC▼ | CÚC▼ | · | · | · | · | · | · | CÚC˙ | CÚC˙ |

`˙` mới xuống giống · `∙` đang lớn · `●` đỉnh sinh trưởng · `▼` đang thu · `·` đất nghỉ · `▨` công trình

| Lô | ha | Mục đích | Cây trồng trong kỳ | NDVI tb | Biên độ | NDMI | Vụ dò được |
|---|---:|---|---|---:|---:|---:|---:|
| **L01** Ruộng lớn Đông | 1.7496 | canh_tac | Cúc chi, Lạc (đậu phộng) | 0.433 | 0.650 | -0.051 | 2 |
| **L02** Vườn cúc hỗn hợp | 0.9172 | canh_tac | Cúc chi, Cúc cổ (trà hoa cúc cổ) | 0.478 | 0.348 | -0.046 | 2 |
| **L03** Ruộng giữa | 0.8107 | canh_tac | Bồ công anh, Cúc chi, Lạc (đậu phộng) | 0.483 | 0.495 | -0.018 | 2 |
| **L04** Khối chanh cây mẹ | 0.2056 | luu_nien | Chanh | 0.720 | 0.562 | +0.283 | 1 |
| **L05** Luống bồ công anh Bắc | 0.2631 | canh_tac | Bồ công anh | 0.577 | 0.541 | +0.158 | 2 |
| **L06** Khu công trình | 0.2513 | cong_trinh | — | 0.381 | 0.339 | +0.052 | 0 |
| **L07** Vườn chanh lớn | 1.9084 | luu_nien | Chanh | 0.723 | 0.579 | +0.318 | 2 |
| **L08** Thửa cải tạo Nam | 0.2499 | canh_tac | Bồ công anh | 0.371 | 0.650 | +0.064 | 1 |
| **L09** Thửa nghỉ luân canh | 0.5200 | dat_nghi | Đậu che phủ (cây phân xanh) | 0.466 | 0.593 | +0.158 | 0 |
| **L10** Vườn ươm + luống cúc đông | 0.3439 | vuon_uom | Cúc chi, Luống ươm cây giống | 0.382 | 0.442 | +0.107 | 2 |
| **L11** Luống rau thuốc cắt lứa | 0.4230 | canh_tac | Bồ công anh | 0.569 | 0.434 | +0.165 | 2 |
| **L12** Ruộng lớn Tây | 1.2031 | canh_tac | Cúc chi | 0.415 | 0.489 | +0.094 | 1 |

### Vài ví dụ cách suy ra

**L07 — vườn chanh lưu niên.** NDMI trung bình **0,318**, cao nhất farm, gấp gần ba lần
mặt bằng. NDMI là ẩm trong tán; giữ cao quanh năm chỉ có tán gỗ mới làm được. NDVI ≥ 0,73
ở 15/21 ngày. Máy dò ra "2 vụ" nhưng với cây lưu niên đó là hai đợt ra lộc — vì NDVI đáy
không bao giờ về mức đất trống, và 1,91 ha không đổi suốt kỳ.

**L08 — thửa mới khai hoang.** Biên độ NDVI 0,65, cao nhất farm, nhưng trung bình chỉ
0,371. NDVI 0,832 (20/08/2025) → 0,195 (20/11/2025) → giữ phẳng 0,18–0,29 suốt tám
tháng → 0,511 (10/08/2026). **Một lần rơi rồi phẳng dài** là dạng phát dọn, không phải
dạng thu hoạch theo vụ. Lịch mô phỏng: bụi cây tự nhiên → phát dọn cuối 11/2025 → đất
nghỉ → lên luống lại 07/2026.

**L06 — khu công trình.** Không dò được vụ nào trong 12 tháng. Độ dốc 3,88°, dốc nhất
farm, dạng nền san. NDVI dao động 0,207–0,547 nhưng không theo dạng gieo–lớn–thu.
Kết luận: nhà lưới + sân phơi + kho, phần dao động là vành cỏ quanh công trình.

**L09 — đất nghỉ.** Không dò được vụ nào. Chênh NDVI mùa mưa − mùa khô = **+0,251**,
lớn nhất farm. Thảm xanh đi theo mưa chứ không theo lịch của người.

### Sản lượng và lô hàng mô phỏng

| | |
|---|---:|
| Lô hàng (tem B2B `SK-L-…`) | **101** |
| Hoa cúc khô | 2 118 kg |
| Bồ công anh khô | 3 166 kg |
| Lạc khô | 3 983 kg |
| Chanh tươi | 36 399 kg |
| Bịch bán lẻ 20 g | 31 765 (có hồ sơ đầy đủ: 120) |
| Cá thể cây có tem | 92 (4 đã có hồ sơ thật) |
| Bản ghi nhật ký đồng ruộng | 584 |

> **Chênh lệch quy mô cần biết trước khi demo.** Lô hàng thật duy nhất đang có trong
> `Sankit/qr` — `SK-L-CUC25-03-Q` — nặng **1,24 kg hoa tươi từ 3 cây**. Đó là lô thử.
> Bộ mô phỏng này ở **quy mô thương mại**: trung vị 259 kg tươi/lô hàng. Khoảng cách đó
> chính là khoảng trống mà nền tảng phải lấp. Mã lô hàng mô phỏng đánh số **từ 10 trở lên**
> để chừa 01–09 cho mã Sankit đã in.

---

## 5. Cảnh báo — luật chạy trên dữ liệu THẬT

89 cảnh báo sinh ra từ 6 luật, chạy trên quan trắc thật, không phải trên số bịa.

| Luật | Số | Bắt cái gì |
|---|---:|---|
| `R1_THIEU_NUOC` | 56 | ETc (Kc FAO-56 × ET0 thật) vượt mưa hiệu quả ≥ 25 mm trong cửa sổ trượt 15 ngày |
| `R2_SUT_NDVI_KHONG_RO_LY_DO` | 5 | NDVI tụt ≥ 0,20 giữa hai lần quan trắc mà nhật ký không ghi việc gì |
| `R3_MAT_DAU_QUANG_HOC` | 5 | ≥ 30 ngày không ảnh quang; gộp về mức farm khi ≥ 8/12 lô cùng thủng |
| `R4_KEM_MAT_BANG_FARM` | 11 | 3 lần quan trắc liên tiếp thấp hơn trung vị farm ≥ 0,15 |
| `R5_NHAT_KY_KHONG_KHOP_ANH` | 11 | khai thu hoạch mà cả quang lẫn radar đều không thấy tán giảm |
| `R6_CHUOI_NGAY_KHONG_MUA` | 1 | ≥ 14 ngày liên tiếp mưa dưới 1 mm — mức farm |

Mức độ: 22 `cao` · 55 `trung_binh` · 12 `thap`. Phạm vi: 84 theo lô · 5 theo farm.

Ngưỡng sụt NDVI của R5 **khác nhau theo cây**, vì thu hoạch mỗi loại lấy đi lượng tán
khác nhau: lạc −0,25 · cúc chi −0,20 · cúc cổ và bồ công anh −0,08 · **chanh: không áp
dụng** (hái quả không đụng tới tán, vệ tinh không kiểm được — phải dựa vào cân tại vườn).
Không có phần này thì mọi đợt hái chanh đều thành báo động giả.

---

## 6. Bàn giao gì cho đội web

```
sankit-farm-lo/
├── BAO_CAO_DU_LIEU.md          ← đang đọc
├── docs/01_MO_HINH_MIEN.md     thực thể, quan hệ, chỗ mô hình hiện tại gãy
├── docs/02_HOP_DONG_DU_LIEU.md khoá, kiểu, ràng buộc — hợp đồng giữa các app
├── docs/03_API_VA_MAN_HINH.md  API sk-backend + màn hình sk-coop / sk-ops / sk-go
├── docs/04_LUAT_CANH_BAO.md    6 luật, ngưỡng, và vì sao đặt ngưỡng đó
├── docs/05_THAT_VA_MAU.md      bảng phân định từng lớp: thật / mô phỏng / dẫn xuất
├── data/that/       (8 file)   dữ liệu đo được — KHÔNG sửa
├── data/mo_phong/   (9 file)   dữ liệu dựng — thay bằng dữ liệu thật khi có
├── data/dan_xuat/   (3 file)   tính ra từ hai lớp trên
├── schema/                     JSON Schema + kiểu TypeScript cho @sankit/types
└── scripts/  sinh_du_lieu.py   sinh lại toàn bộ, kết quả y hệt mỗi lần chạy
           kiem_tra.py       schema + 12 bất biến + ký tự kiểm tra mã Sankit
```

Tổng **749 KB**. Chạy lại và tự kiểm:

```bash
python3 scripts/sinh_du_lieu.py     # đọc từ GIS_RiTi_TrangAn/data/out/, không ghi đâu khác
python3 scripts/kiem_tra.py         # thoát mã 1 nếu sai — cắm vào CI được
```

Kiểu TypeScript trong `schema/sankit-farm-lo.d.ts` đã qua `tsc 6.0.3 --strict` (đúng
phiên bản `sankitmono` ghim). Mọi mã `SK-…` đã qua trình kiểm tra thật của
`Sankit/qr/tools/ma_dinh_danh.py`.

Bảng dùng nhiều nhất sẽ là **`data/dan_xuat/lo_thang.csv`** — 156 hàng, mỗi hàng là một
(lô, tháng), gồm cây trồng, pha sinh trưởng, NDVI, NDMI, radar, nhiệt độ, mưa, ET0, Kc,
nhu cầu tưới. Đủ để dựng toàn bộ màn hình tổng quan mà không cần join gì thêm.

---

## 7. Giới hạn — đọc trước khi hứa với ai

1. **Ranh giới ±2,9 m, KHÔNG phải ranh giới pháp lý.** Không dùng cho hồ sơ địa chính.
2. **Lô nhỏ thì NDVI kém tin.** Bốn lô dưới 0,3 ha (L04, L05, L06, L08) chỉ chứa 20–26
   pixel Sentinel-2 và còn chịu ảnh hưởng lẫn từ lô bên cạnh.
3. **Nhãn cây trồng chưa ai ra thực địa xác nhận.** NDVI cao có thể là vườn chanh, cũng
   có thể là bụi rậm. Một buổi đi thực địa là gỡ được toàn bộ mục 4 của báo cáo này.
4. **Nhiệt độ bề mặt là ƯỚC TÍNH, không phải đo.** Công thức trong
   [docs/05](docs/05_THAT_VA_MAU.md). Muốn số đo thật thì lấy Landsat 8/9 TIRS hoặc
   Sentinel-3 LST — cả hai đều miễn phí, chưa kéo về.
5. **Thổ nhưỡng không phân biệt được lô** (SoilGrids 250 m).
6. **Không có phiếu kiểm nghiệm nào trong bộ này.** Cố ý để trống, không dựng phiếu giả —
   giữ đúng luật `nguon` của `Sankit/qr`.
7. **Nhân sự trong nhật ký là nhân vật hư cấu**, gắn cờ `nhan_vat_hu_cau: true`.
8. **Phép đối chiếu nhật ký ↔ vệ tinh trong bộ này gần như tự khớp**, vì lịch mô phỏng
   được suy TỪ đường NDVI. Giá trị thật của nó nằm ở nhật ký thật sau này. Hai bản ghi
   sai đã được cắm cố ý (`data/mo_phong/lech_co_y.json`) để màn hình cảnh báo có nội
   dung mà dựng.

---

## 8. Việc cần chốt trước khi code

| # | Việc | Chặn ai |
|---|---|---|
| Q1 | **"Lô hàng" định nghĩa lại thế nào?** `Sankit/qr` đang ghi *một mẻ sấy = một lô hàng*. Ở quy mô thương mại một ngày hái ra nhiều mẻ. Bộ này tạm dùng *(lô đất × cửa sổ 2–10 ngày hái)*. | cấu trúc mã `SK-L-…`, tem đã in |
| Q2 | **Thêm 4 mã giống**: `CCO` cúc cổ, `LAC` lạc, `BCA` bồ công anh, `UOM` luống ươm. Phải sửa hai chỗ cho khớp: `Sankit/qr/tools/ma_dinh_danh.py` hằng `GIONG` **và** `Sankit/qr/web/app.js` hằng `GIONG`. | sinh mã lô hàng cho cây không phải cúc/chanh |
| Q3 | **Có thêm tầng `khoảnh` dưới `lô` không?** Ca 2.2 cho thấy không có thì mất khả năng kiểm chứng ở lô trồng hỗn hợp. Thêm thì mọi màn hình phải chọn độ phân giải. | mô hình miền, toàn bộ schema |
| Q4 | **Vùng trồng ở đâu?** Doc RiTi ghi *Nho Quan*, giấy HACCP ghi *Tây Hoa Lư*, GIS đo ở *Trường Yên, Hoa Lư* (20,2580 N · 105,8543 E). Ba nguồn, hai huyện. Đây là CC-06 trong `Sankit/qr/docs/04_CHUA_CHOT.md`, vẫn chưa có câu trả lời. | mọi thứ hiển thị địa chỉ vùng trồng |
| Q5 | **Ai nhập nhật ký đồng ruộng?** `sk-go` (Expo) là app hiện trường nhưng chưa có sync offline — đây là rủi ro lớn nhất còn treo trong `docs/vision.md`. Không có nhật ký thì không có gì để đối chiếu với ảnh. | R2, R5, toàn bộ giá trị của mô hình |
| Q6 | **Ảnh vệ tinh cập nhật kiểu gì?** Hiện là script chạy tay. Sentinel-2 bay lại 5 ngày/lần. Cần cron + hàng đợi + chỗ lưu (R2 đã có trong kế hoạch monorepo). | tính "thời gian thực" của sản phẩm |
