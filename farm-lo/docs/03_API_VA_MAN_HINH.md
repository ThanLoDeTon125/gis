# 03 — API và màn hình

Bám đúng stack đã chốt trong `sankitmono/docs/vision.md`: Hono trên Cloudflare Workers,
OpenAPI 3.1 qua `hono-openapi` + Valibot, Vite + React + TanStack cho hai app web,
Expo cho app hiện trường. Không đề xuất đổi gì.

## 1. `sk-backend` — bề mặt API

Tất cả dưới `/v1`. Nhóm theo thực thể, không theo màn hình.

### Lô đất — chỉ đọc từ phía người dùng

```
GET  /v1/vuon/{vuon}/lo                        danh sách 12 lô + số liệu tổng hợp
GET  /v1/vuon/{vuon}/lo.geojson                FeatureCollection cho bản đồ
GET  /v1/lo/{lo_id}                            hồ sơ một lô
GET  /v1/lo/{lo_id}/quan-trac?tu=&den=&loai=   quang | radar | ca_hai
GET  /v1/lo/{lo_id}/thang?tu=&den=             bảng lô × tháng (nguồn chính của biểu đồ)
```

`POST`/`PATCH` lên `quan-trac` **không tồn tại**. Đó là bất biến I8 — lớp đo được chỉ do
pipeline vệ tinh ghi, qua đường riêng có xác thực dịch vụ.

### Mùa vụ và nhật ký — HTX ghi

```
GET    /v1/lo/{lo_id}/vu
POST   /v1/lo/{lo_id}/vu
PATCH  /v1/vu/{vu_id}
GET    /v1/vu/{vu_id}/nhat-ky
POST   /v1/vu/{vu_id}/nhat-ky            ← sk-go gọi, phải chịu được gửi lại (idempotent)
GET    /v1/lo/{lo_id}/nhat-ky?tu=&den=
```

`POST /nhat-ky` nhận `client_id` do máy sinh để chống ghi trùng khi app hiện trường mất
mạng rồi gửi lại. Đây là điều kiện tối thiểu cho sync offline, kể cả trước khi chốt
PowerSync hay ElectricSQL.

### Lô hàng, bịch, cây

```
GET   /v1/lo-hang?lo_dat=&trang_thai=&tu=&den=
POST  /v1/lo-hang
GET   /v1/lo-hang/{ma}                   ← trang QR B2B đọc chính endpoint này
POST  /v1/lo-hang/{ma}/niem               không đảo ngược
GET   /v1/bich/{ma}
GET   /v1/cay/{ma}
GET   /v1/ma/{ma}                        phân loại mã rồi chuyển tiếp — cho trang quét
```

`GET /v1/ma/{ma}` là điểm vào duy nhất của tem: đọc tiền tố `SK-L`/`SK-B`/`SK-C`, kiểm
ký tự ISO 7064, rồi trả về đúng loại. Trang quét khỏi phải tự đoán.

### Cảnh báo và đối chiếu

```
GET   /v1/vuon/{vuon}/canh-bao?muc_do=&ma_luat=&trang_thai=&lo_id=
PATCH /v1/canh-bao/{cb_id}               { trang_thai: da_xem | da_xu_ly | bo_qua, ghi_chu }
GET   /v1/vuon/{vuon}/doi-chieu          nhật ký ↔ vệ tinh
GET   /v1/vuon/{vuon}/luat               ngưỡng đang áp dụng
PATCH /v1/luat/{ma_luat}                 chỉ sk-ops
```

### Khí hậu

```
GET /v1/vuon/{vuon}/khi-hau/ngay?tu=&den=
GET /v1/vuon/{vuon}/khi-hau/thang
```

### Ba quy ước xuyên suốt

1. **Mọi phản hồi mang `nguon`** ở cấp bản ghi hoặc cấp khối, giá trị `that` | `mau` |
   `dan_xuat`. Client không được phép đoán.
2. **Phân trang bằng con trỏ**, không bằng `offset`. `bich` có 31 765 bản ghi trong bộ
   mô phỏng — phân trang theo offset sẽ chết ở trang sâu.
3. **Ngày là `YYYY-MM-DD` không kèm múi giờ.** Vệ tinh bay theo ngày UTC, việc đồng
   ruộng theo ngày địa phương. Trộn `Date` của JS vào đây là đẻ lỗi lệch một ngày.

## 1b. Bản tham chiếu chạy được — `web/ban-do.html`

Trong gói có sẵn **một giao diện giám sát hoàn chỉnh**, dựng từ chính bộ dữ liệu này:
bản đồ ảnh vệ tinh, 12 lô bấm được, thanh 13 tháng, bốn lớp tô màu, và thanh bên đủ
thông tin từng lô. Một file HTML tự chứa — mở bằng trình duyệt là chạy, không cần
server, không gọi mạng, không phụ thuộc thư viện nào.

Đây **không phải sản phẩm cuối**, mà là bản để đối chiếu khi dựng `sk-coop`:

| Thứ đáng lấy | Ở đâu trong bản dựng |
|---|---|
| Cách chiếu toạ độ lô lên ảnh nền | `scripts/dung_ban_do.py`, hàm `to_px` — Mercator, không phải nội suy tuyến tính theo vĩ độ |
| Ngưỡng chia mức "độ xanh" | `scripts/_ban_do.js`, hằng `BANDS` — 5 mức, đặt theo phân bố thật của farm |
| Bảng dịch thuật ngữ sang tiếng người dùng | `scripts/_ban_do.js`, hằng `TU_DIEN` và `LUAT` |
| Câu "nên làm gì" cho từng luật cảnh báo | `scripts/_ban_do.js`, hằng `LUAT[*].lam` |
| Cách viết tình trạng lô thành một câu | `scripts/_ban_do.js`, hàm `tinhTrang` |

Dựng lại: `../gis/.venv/bin/python scripts/dung_ban_do.py`

### Ngôn ngữ hiển thị — quy tắc bắt buộc

Người dùng `sk-coop` là cán bộ hợp tác xã, không phải kỹ sư viễn thám. **Không có thuật
ngữ kỹ thuật nào được đi thẳng ra màn hình.**

| Trong dữ liệu | Hiện ra cho người dùng |
|---|---|
| `NDVI` | Độ xanh của cây |
| `NDMI` | Độ ẩm trong lá |
| `VH`, radar, Sentinel-1 | Ảnh radar (loại ảnh xuyên được mây) |
| `Kc × ET0` | Cây cần bao nhiêu nước |
| `mưa hiệu quả` | Lượng mưa thấm được xuống đất |
| `LST` | Nhiệt mặt đất (ước tính) |
| `quan trắc` | Lần chụp ảnh |
| `R1`…`R6` | Tên việc: thiếu nước, cây xuống đột ngột, mây che… |

Và mỗi cảnh báo **phải kèm một câu nên làm gì**. Cảnh báo không nói được phải làm gì thì
người dùng bỏ qua từ lần thứ hai trở đi.

## 2. `sk-coop` — cổng HTX (Farm Manager)

Đây là app mang phần lớn giá trị. Bảy màn hình, thứ tự dựng theo mức cần thiết:

| # | Màn hình | Đọc từ | Ghi chú |
|---|---|---|---|
| 1 | **Bản đồ farm** — 12 lô tô theo NDVI / trạng thái vụ / số cảnh báo | `lo.geojson` + `lo_thang` | có thanh trượt thời gian 13 tháng; lô nhỏ nhất 0,2056 ha nên phải zoom được sâu |
| 2 | **Trang lô** | `lo/{id}` + `quan-trac` + `vu` + `nhat-ky` + `canh-bao` | biểu đồ NDVI/NDMI có **khoảng mù**, không nối đường qua |
| 3 | **Lịch mùa vụ** — Gantt 12 lô × 13 tháng | `lo_thang` | chính là bảng ở §4 báo cáo; một màn hình trả lời "lô nào trồng gì khi nào" |
| 4 | **Nhật ký đồng ruộng** | `nhat-ky` | 617 bản ghi trong bộ mẫu; lọc theo lô, loại việc, người |
| 5 | **Lô hàng** — danh sách + chi tiết + nút niêm | `lo-hang` | chi tiết phải hiện `trang_thai_lo_dat_luc_hai` và `khi_hau_ca_vu` — đây là chỗ GIS xuất hiện trước mặt bên mua |
| 6 | **Hộp cảnh báo** | `canh-bao` | 89 bản ghi; nhóm R1+R2+R6 cùng đợt hạn thành một sự kiện |
| 7 | **Nước và khí hậu** | `khi-hau` + `lo_thang` | mưa vs ET0 theo tháng, nhu cầu tưới theo lô |

**Màn hình 2 là trái tim.** Một lô, một trang, đủ ba lớp chồng lên nhau: đường NDVI đo
được, dải mùa vụ khai báo, và các mốc nhật ký cắm lên cùng trục thời gian. Nhìn một cái
là thấy lời khai có khớp với ảnh không — không cần đọc bảng.

## 3. `sk-ops` — Sankit Admin

| # | Màn hình | Việc |
|---|---|---|
| 1 | Danh sách vườn | nhiều HTX; hiện tại mới có RiTi |
| 2 | Trạng thái pipeline vệ tinh | lần kéo cuối, số ảnh mới, lô nào đang thiếu dữ liệu |
| 3 | Cấu hình ngưỡng luật | R1–R6 theo vườn, có lịch sử thay đổi |
| 4 | Kiểm định dữ liệu | tỉ lệ `that` / `mau` / `dan_xuat` từng vườn — chặn niêm hồ sơ khi còn quá nhiều `mau` |
| 5 | Duyệt / đình chỉ lô hàng | dùng khi cảnh báo R5 mức `cao` chưa xử lý |

## 4. `sk-go` — app hiện trường

Ràng buộc thật: ngoài ruộng thường không có sóng. Mọi thứ phải ghi được offline.

| # | Màn hình | Việc |
|---|---|---|
| 1 | Bản đồ + "tôi đang ở lô nào" | so GPS với `lo.geojson`; ranh giới ±2,9 m nên phải hiện cả sai số, đừng khẳng định chắc chắn khi đứng sát bờ |
| 2 | Ghi nhật ký | gieo · bón · tưới · làm cỏ · phun sinh học · thu hoạch; hàng đợi offline, gửi khi có mạng |
| 3 | Quét tem cây | `SK-C-…`, xem tiểu sử, cập nhật trạng thái |
| 4 | Cân và gán lô hàng | cân hoa tươi theo cây rồi đổ vào mẻ — đúng như `Sankit/qr` mô tả ở giai đoạn "tiếp nhận nguyên liệu" |
| 5 | Chụp ảnh có GPS | bằng chứng cho các mốc nhật ký |

**Đây là mắt xích yếu nhất của cả mô hình.** Không có nhật ký thật thì R2 và R5 không có
gì để đối chiếu, và toàn bộ luận điểm "ảnh vệ tinh kiểm chứng lời khai" rỗng. Đồng thời
đây cũng là phần rủi ro nhất về kỹ thuật: `docs/vision.md` của monorepo đã ghi rõ engine
sync offline (PowerSync / ElectricSQL / tự làm) **chưa quyết**.

## 5. Thứ tự nên dựng

```
1. Đổ data/that + data/mo_phong vào DB, dựng GET /v1/lo, /v1/lo/{id}/thang
2. sk-coop màn 1 (bản đồ) + màn 3 (lịch mùa vụ)     ← demo được sau bước này
3. sk-coop màn 2 (trang lô)                          ← trái tim sản phẩm
4. sk-coop màn 5 (lô hàng) + nối vào trang QR B2B đã chạy thật
5. @sankit/rule-engine: R1–R6 + màn 6 (hộp cảnh báo)
6. sk-go màn 2 (ghi nhật ký offline)                 ← chốt engine sync trước
7. sk-ops
```

Sau bước 2 đã có thứ mang đi nói chuyện được: bản đồ 12 lô thật, tô theo số liệu vệ tinh
thật, kèm lịch mùa vụ. Sau bước 4 thì bên mua sỉ quét tem ra được hồ sơ có cả nền GIS.
