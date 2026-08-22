# sk-coop — Nạp lớp GIS theo lô (review + extract + Q&A)

Ghi chép khi đối chiếu bộ dữ liệu GIS 12 lô của RiTi Farm với prototype `sk-coop` và
hợp đồng dùng chung, **trước khi** dựng màn Registry (§3.4 của brief). Đây là chỗ giải
thích *vì sao* `src/features/registry-plots/` sẽ có hình dạng như vậy — đổi gì thì sửa
file này trước, rồi mới sửa code cho khớp.

Cùng vai trò với [`../sk-ops/DESIGN_TOKENS.md`](../sk-ops/DESIGN_TOKENS.md) bên sk-ops.

Nguồn đã đọc:
- `_prototype/Coop Dashboard.dc.html` — prototype sk-hub, màn **“Bản đồ thửa”**
- `_prototype/uploads/sk-shared-contract.md` — hợp đồng dùng chung (§2 từ vựng, §4 gate/issue, §5 thực thể, §6 token)
- `_prototype/uploads/ui-sk-hub-coop-dashboard.md` — brief sk-hub, **§3.4 Registry management**
- `_prototype/ban-do-lo.html` — bản dựng chạy được của lớp GIS (mới, đi kèm lần nạp này)
- `_prototype/uploads/*.md` — báo cáo dữ liệu, mô hình miền, hợp đồng dữ liệu, luật cảnh báo
- `../sk-ops/DESIGN_TOKENS.md` — kết quả nạp token bên sk-ops (§2 đã trích sẵn giá trị của sk-coop/sk-go)

---

## 1. Prototype sk-coop đã chừa sẵn chỗ cho GIS

Màn “Bản đồ thửa” trong `Coop Dashboard.dc.html` **không phải chỗ trống** — nó đã khai
báo đủ bộ khung, chỉ thiếu dữ liệu:

| Biến trong prototype | Ý đồ | Lần nạp này cấp gì |
|---|---|---|
| `mapRef` | khung bản đồ cao 300 px, nền `#e7edea` | ảnh nền vệ tinh Esri đã georeference + 12 polygon |
| `gisMapped` / `gisUnmapped` / `gisTotal` | đếm thửa đã/chưa đo ranh | **12/12 đã đo**, sai số ±2,9 m |
| `onDrawToggle` / `drawBtnLabel` / `confirmSavePlot` | chế độ vẽ tay ranh giới | — (xem **Q7**) |
| `searchQ` / `hasResults` | tìm địa điểm để nhảy tới | — (cần geocoder, xem **Q9**) |
| `plots[]` với `p.area`, `p.crop`, `p.batch` | danh sách thửa | diện tích đo được, cây trồng, vụ |
| `onLoadSample` | nạp dữ liệu mẫu | `_prototype/du-lieu/` |

Chú giải bản đồ trong prototype mới có hai trạng thái: *“Đã đo ranh”* và *“Bị chặn”*.
Lần nạp này thêm bốn lớp tô: **độ xanh cây · loại cây · cần chú ý · ảnh gốc**.

## 2. Lần nạp này mang vào gì

| Lớp | Nội dung | Nguồn | Sửa được không |
|---|---|---|---|
| Ranh giới thửa | 12 polygon EPSG:4326, ±2,9 m | ảnh vệ tinh Esri + bản vẽ chủ farm | **không** — đo được |
| Quan trắc vệ tinh | 249 bản ghi quang (Sentinel-2), 684 radar (Sentinel-1) | ESA | **không** |
| Khí hậu | 366 ngày liên tục | Open-Meteo (ERA5) | **không** |
| Địa hình, thổ nhưỡng | cao độ, độ dốc, thành phần đất | Copernicus DEM, SoilGrids | **không** |
| Mùa vụ, đợt thu | 18 vụ · 25 đợt thu | **mô phỏng**, suy từ chuỗi NDVI thật | có |
| Nhật ký đồng ruộng | 584 bản ghi | **mô phỏng** | có |
| Lô hàng, bịch, cây có tem | 101 · 120 · 92 | **mô phỏng** (4 cây có hồ sơ thật) | có |
| Cảnh báo | 89, từ 6 luật chạy trên số đo thật | dẫn xuất | — |

Chi tiết phân định thật/mô phỏng: [`_prototype/uploads/that-va-mau.md`](_prototype/uploads/that-va-mau.md).

## 3. Từ vựng — hợp đồng §2 thắng, không đặt từ mới

Hợp đồng dùng chung ghi rõ: *“Never invent a new user-facing noun in an app doc.”*
Bộ dữ liệu này đến từ ngoài hệ Sankit nên mang bộ từ riêng. Ánh xạ bắt buộc:

| Trong bộ dữ liệu | Khái niệm nội bộ (hợp đồng §2) | Nhãn sk-hub | Ghi chú |
|---|---|---|---|
| `lo_dat` (`L01`…`L12`) | Registry site | **Plot / Thửa** | `lo_id` chính là `Plot.id`, ổn định qua các vụ |
| `vu` (chu kỳ trồng) | Crop | **Crop / Cây trồng** | xem **Q3** |
| `dot_thu` (một lượt hái) | *(chưa có trong §2)* | — | xem **Q3** |
| `lo_hang` (`SK-L-…`) | Batch | **Batch / Lô hàng** | xem **Q3** |
| `nhat_ky` (một việc đã làm) | Observation (completed) | **Record** | không gọi là “nhật ký” trên màn hình |
| `bang_chung` (`CÂN` `GPS` `ẢNH` `DUYỆT`) | Provenance | **Verified ✓** | xem **Q10** |
| `canh_bao` (R1–R6) | Rule violation / gap | **Issue** | xem **Q1** — **không** đặt từ “Cảnh báo” |
| `nhan_su` | Operator | **Staff** | nhân vật hư cấu, phải thay |
| `cay_ca_the` (`SK-C-…`) | *(chưa có trong §2)* | — | tem cắm ngoài vườn, khái niệm riêng của mảng QR |

Trong bản dựng `ban-do-lo.html` hiện còn dùng “cảnh báo”, “nhật ký”, “lô hàng” —
**đó là ngôn ngữ của prototype, không phải nhãn chốt.** Khi dựng code phải đổi theo bảng trên.

## 4. Thực thể — khớp hợp đồng §5

| Hợp đồng §5 | Trường yêu cầu | Bộ dữ liệu có | Thiếu |
|---|---|---|---|
| **Plot / Site** | `id`, `name`, `boundary/GPS`, `coop`, `season` | `lo_id`, `ten`, `lo_ranh_gioi.geojson`, — , — | `coop`, `season` |
| **Crop / Batch** | `id`, `species`, `plot`, `planting date` | `vu_id`, `ma_cay_trong`, `lo_id`, `ngay_xuong_giong` | đủ |
| **Operator** | `id`, `name`, `role`, `coop` | `ma`, `ten`, `vai_tro`, — | `coop` |
| **Observation** | `id`, `type`, `payload`, `provenance`, `links`, `status` | `nk_id`, `loai_viec`, mô tả, `bang_chung`, `lo_id`/`vu_id`, — | `status`, provenance có cấu trúc |

Hợp đồng §5 nhấn: *“ID must stay stable across seasons — rule correctness depends on it.”*
`lo_id` đã thoả — nó cũng chính là đoạn khu trong mã cây `SK-C-CUC25-**L01**-0007-P` đã in ra tem.

## 5. Token giao diện — bản dựng KHÔNG thắng

`ban-do-lo.html` tự chọn bộ token riêng (nền đất sét lạnh, nhấn nâu đỏ laterite, chữ
Avenir Next / SF Mono, bo góc 8 px). **Bỏ toàn bộ.** Dùng giá trị của sk-coop, giống
hệt cách sk-ops đã làm (xem `../sk-ops/DESIGN_TOKENS.md` §3):

| Vai trò (hợp đồng §6) | Giá trị sk-coop | Trong bản dựng — bỏ đi |
|---|---|---|
| Primary / action | `#128173` teal (đậm `#0e6a5f`, nhạt `#e7f2ef`) | `#8a4a2c` |
| Ink / body / muted | `#12211d` / `#45534e` / `#85938d`, `#a3aeaa` | `#15180f` / `#565e4f` / `#848c79` |
| Canvas / surface / line | `#eef2f0`, `#f6f8f7` / `#f2f6f4` / `#dbe3e0` | `#e9ebe4` / `#f6f7f1` / `#dde0d3` |
| Success / Verified | `#2f9e5b` (đậm `#1f7a45`) | `#0ca30c` |
| Caution / at-risk | `#cf8a0d` | `#fab219`, `#ec835a` |
| Danger / hard-gate | `#cf4436` | `#d03b3b` |
| Chữ tiêu đề / thân / số liệu | Plus Jakarta Sans / Barlow / IBM Plex Mono | Avenir Next / SF Mono |
| Bo góc | **4 px** (198/209 chỗ trong prototype) | 8 px |

## 6. Bảng màu mã hoá dữ liệu — cái này thì GIỮ

Khác với token thương hiệu, đây là **tầng mã hoá dữ liệu**, đã chạy qua trình kiểm mù
màu (`ΔE` CVD, sàn thị lực thường, tương phản nền) và **đạt toàn bộ ở cả hai chế độ sáng/tối**.
Đổi tay là hỏng khả năng đọc của người mù màu.

```
Nhóm cây (3 sắc, kiểm theo mọi cặp):
  dược liệu   #b8801a sáng / #bc8a20 tối
  họ đậu      #00805c sáng / #2fa179 tối
  cây lâu năm #3563b8 sáng / #5786d6 tối
Thang độ xanh (một sắc lục, 5 bước, tối→sáng theo độ xanh, đọc trên nền ảnh vệ tinh):
  #4a7d55  #40a165  #5ec077  #96dc95  #cdf0be
```

Ngưỡng chia 5 mức đặt theo phân bố thật của farm này (`ban-do-lo.html`, hằng `BANDS`):
`< 0,25` đất trống · `0,25–0,40` cây thưa · `0,40–0,55` trung bình · `0,55–0,70` xanh
tốt · `≥ 0,70` rất xanh. Thấp nhất đo được cả farm là 0,147; cao nhất 0,905.

Xem **Q6** — sắc lục `#00805c` của nhóm họ đậu nằm gần teal thương hiệu `#128173`.

## 7. Ngôn ngữ hiển thị — luật bắt buộc

Người dùng sk-hub là cán bộ hợp tác xã, không phải kỹ sư viễn thám.
**Không có thuật ngữ kỹ thuật nào được đi thẳng ra màn hình.**

| Trong dữ liệu | Hiện ra cho người dùng |
|---|---|
| `NDVI` | Độ xanh của cây |
| `NDMI` | Độ ẩm trong lá |
| `VH`, Sentinel-1 | Ảnh radar (loại ảnh xuyên được mây) |
| `Kc × ET0` | Cây cần bao nhiêu nước |
| `mưa hiệu quả` | Lượng mưa thấm được xuống đất |
| `LST` | Nhiệt mặt đất (ước tính) |
| `quan trắc` | Lần chụp ảnh |
| `R1`…`R6` | Tên việc: thiếu nước, cây xuống đột ngột, mây che… |

Bảng dịch chạy được nằm ở `ban-do-lo.html`, hằng `TU_DIEN` và `LUAT`. Mỗi Issue **phải
kèm một câu nên làm gì** (`LUAT[*].lam`) — Issue không nói được phải làm gì thì người
dùng bỏ qua từ lần thứ hai.

---

## 8. Chưa chốt — đọc hết trước khi mở ticket dựng UI

### Q1 · Cảnh báo từ vệ tinh có phải là “Issue” không?
Hợp đồng §4 định nghĩa Flag/Issue là **Rule tác giả trong sk-ops** bắn ra tại thời điểm
một hành động. 89 cảnh báo ở đây sinh từ **số đo vệ tinh**, không gắn với hành động nào
của người, và không có Requirement nào đứng sau.

Ba hướng: (a) coi là Issue, vào cùng vòng đời `open → in progress → resolved`, thêm một
`source` để phân biệt; (b) khái niệm mới → phải thêm một dòng vào hợp đồng §2 trước;
(c) không hiện cho manager, chỉ dùng nội bộ.

**Chặn:** toàn bộ màn Issue, và câu hỏi lớn hơn — mô hình này có bán được cho tổ chức
chứng nhận không. Đề xuất (a).

### Q2 · Diện tích nào là diện tích chính thức?
Mỗi lô có **hai** con số: chủ farm vẽ tay, và bản nắn theo mép thửa nhìn thấy trên ảnh.
Chênh nhau tới **+31 %** ở lô L10. Prototype chỉ có một trường `p.area`.
Hợp đồng §5 nói ranh giới ảnh hưởng trực tiếp tới tính đúng của Rule.
**Chặn:** mọi phép tính theo diện tích — sản lượng/ha, lượng nước tưới, định mức vật tư.

### Q3 · “Batch” trong hợp đồng ứng với cái gì?
Hợp đồng §5 có đúng một khái niệm **Crop / Batch**. Bộ dữ liệu này cần **ba** tầng:
`vụ` (một chu kỳ trồng) → `đợt thu` (một lượt hái trong vụ) → `lô hàng` (`SK-L-…`, đơn vị
thương mại có tem QR). Gộp `vụ` với `đợt thu` là chỗ mô hình gãy — bất biến I4 trong
[`hop-dong-du-lieu.md`](_prototype/uploads/hop-dong-du-lieu.md) bắt được 12 cặp vi phạm ở bản dựng đầu.
**Chặn:** schema, và mã `SK-L-…` đã in lên tem.

### Q4 · sk-coop chưa hề theme, mà sk-ops đã theme theo sk-coop
`apps/sk-coop/src/index.css` hiện vẫn là scaffold shadcn mặc định với **Geist**, trong
khi `sk-ops` đã đổi sang Plus Jakarta Sans / Barlow / IBM Plex Mono + teal `#128173`
*lấy từ chính prototype của sk-coop*. Hai app đang lệch nhau.
**Chặn:** mọi việc UI trong sk-coop. Nên có một ticket theme sk-coop chạy **trước**.

### Q5 · Màu trạng thái đang lệch ở hai tầng
**Trong chính prototype sk-coop:** chú giải bản đồ dùng `#2fd08a` (xanh) và `#ff6b57`
(đỏ), trong khi phần còn lại dùng `#2f9e5b` và `#cf4436` cho cùng vai trò Success/Danger.

**Giữa hai app:** `sk-ops/src/index.css` đã chốt `--warning: #b7791f`, kèm chú thích
*“success/warning/danger taken verbatim from sk-go's design tokens”* — trong khi prototype
sk-coop dùng `#cf8a0d` cho đúng vai trò đó (21 lần). Hợp đồng §6 yêu cầu giá trị phải
**giống hệt nhau ở cả ba app**; hiện chưa giống.

**Chặn:** chốt một giá trị cho vai trò Caution rồi sửa cả hai app. Nếu để sk-coop tự chọn
`#cf8a0d` thì phá luật “ba app là một sản phẩm”. Việc này nên gộp vào ticket theme sk-coop
ở **Q4** chứ không để lẫn vào ticket dựng màn Registry.

### Q6 · Teal thương hiệu đụng màu chuỗi dữ liệu
Primary `#128173` nằm gần `#00805c` — màu của nhóm cây họ đậu trên bản đồ. Trên cùng một
màn hình, người dùng sẽ không phân biệt được “màu thương hiệu” với “màu mã hoá loại cây”.
Đổi màu chuỗi thì phải **chạy lại trình kiểm mù màu**, không đổi tay được.
Đề xuất: giữ bảng đã kiểm, và **cấm dùng teal cho bất kỳ mảng tô nào trên bản đồ**.

### Q7 · Vẽ tay ranh giới có được ghi đè bản đo không?
Prototype có `onDrawToggle` cho manager tự vẽ. Nếu vẽ tay ghi đè lên ranh giới đã nắn
theo ảnh (±2,9 m) thì mất luôn lớp đo được — mà đó là thứ làm cho cả mô hình đứng vững.
Đề xuất: giữ hai lớp riêng, vẽ tay là `boundary_declared`, đo được là `boundary_measured`,
và hiện chênh lệch giữa hai lớp thay vì để một cái đè cái kia.

### Q8 · Dữ liệu mẫu 1,2 MB có nên nằm trong repo không?
`_prototype/du-lieu/` đang chiếm 1,2 MB. Ba hướng: để nguyên trong `_prototype` (chỉ là
tài liệu, không vào bundle) · đẩy lên R2 · viết script seed. Hiện chọn hướng đầu vì
`_prototype/` vốn đã không vào build.

### Q9 · Ảnh nền bản đồ lấy từ đâu khi lên sản phẩm?
Bản dựng nhúng thẳng ảnh Esri World Imagery dạng base64 (253 KB) — đủ cho prototype,
không dùng được cho sản phẩm. Cần chốt nguồn tile, điều khoản sử dụng, và dòng ghi công.
Ô tìm địa điểm (`searchQ`) cũng cần một geocoder.

### Q10 · `bang_chung` phải hiện thành con dấu Verified ✓
Nhật ký hiện mang nhãn `CÂN` `GPS` `ẢNH` `DUYỆT` — đúng bằng bốn tín hiệu provenance mà
hợp đồng §3 mô tả (ai · lúc nào · ở đâu · ảnh). Phải render bằng **con dấu Verified ✓ dùng
chung**, và bản ghi thiếu GPS phải ra trạng thái *“Chưa xác thực”* màu Caution, không được
mang con dấu.
