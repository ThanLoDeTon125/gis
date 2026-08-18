# 02 — Hợp đồng dữ liệu

Kiểu TypeScript ở [`schema/sankit-farm-lo.d.ts`](../schema/sankit-farm-lo.d.ts) — chép
thẳng vào `packages/types` của `sankitmono` được. JSON Schema ở
[`schema/sankit-farm-lo.schema.json`](../schema/sankit-farm-lo.schema.json).

## 1. `lo_id` — khoá nối, không phải khoá mới

```
L01 … L12          1 chữ cái + 2 chữ số
```

Đây **không phải khoá do bộ này đặt ra**. Nó đã tồn tại ở cả hai đầu:

| Nơi | Trường | Ví dụ |
|---|---|---|
| `../gis/data/out/lots.geojson` | `properties.lo_id` | `L01` |
| `Sankit/qr/data/cay/*.json` | `vi_tri.khu` | `L01` |
| `Sankit/qr` mã cây `SK-C-CUC25-**L01**-0007-P` | đoạn thứ 3 | regex `^[A-Z]\d{2}$` |

Ba chỗ đã khớp nhau về hình dạng. Ghép là **đổi kiểu `vi_tri.khu` từ chuỗi tự do thành
khoá ngoại trỏ `LO_DAT.lo_id`** — không sinh mã mới, không đụng tem đã in.

Ràng buộc phải thêm khi lên DB:

```sql
ALTER TABLE cay_ca_the
  ADD CONSTRAINT fk_cay_lo FOREIGN KEY (lo_id) REFERENCES lo_dat (lo_id);
```

Và một `CHECK` rằng đoạn khu trong `id` bằng đúng cột `lo_id` — hiện chưa có gì ép điều
đó, mã và trường vị trí lệch nhau vẫn lọt.

## 2. Bất biến — trình kiểm tra phải ép

| # | Bất biến | Vi phạm thì sao |
|---|---|---|
| I1 | `LO_HANG.nguon_cay ⊆ { CAY_CA_THE.id : lo_id = LO_HANG.lo_dat_id }` | lô hàng nhận hoa từ cây ở lô khác — sai truy xuất |
| I2 | `LO_HANG.nguon_cay` = **đúng hợp** `nguon_cay` các bịch của nó | `Sankit/qr` đã ép luật này, giữ nguyên |
| I3 | `VU.ngay_xuong_giong < VU.ngay_thu_tu ≤ VU.ngay_thu_den` | — |
| I3b | `DOT_THU.ngay_thu_tu ≥ VU.ngay_xuong_giong` của vụ nó thuộc về | đợt thu nằm ngoài vụ |
| I4 | hai `VU` cùng `lo_id` giao nhau về thời gian ⟹ tổng `ti_le_gieo` ≤ 1 | hai cây cùng chiếm cả lô |
| I4b | hai `DOT_THU` cùng `vu_id` **không được chồng thời gian** | đếm sản lượng hai lần |
| I5 | `NHAT_KY.ngay ∈ [VU.ngay_xuong_giong − 30, VU.ngay_thu_den + 30]` | việc ghi ngoài vụ mà lại gắn vào vụ |
| I11 | `VU.ngay_ket_thuc = null` ⟹ không có `VU` nào khác cùng lô gieo sau `ngay_thu_den` của nó | cây lưu niên chiếm lô mãi mãi, chặn mọi vụ sau |
| I6 | `LO_HANG.trang_thai = da_niem_ho_so` ⟹ bản ghi **chỉ đọc** | hồ sơ đã niêm mà sửa được thì niêm vô nghĩa |
| I7 | mọi bản ghi đều có `nguon ∈ {that, mau, dan_xuat}` | mất phân định thật/mẫu |
| I8 | `QUAN_TRAC_*` **không có đường ghi** ở tầng API | lớp đo được bị sửa thì cả mô hình mất nghĩa |
| I9 | `LO_HANG.khoi_luong_kho_kg ≤ LO_HANG.khoi_luong_tuoi_kg` | — |
| I10 | mã `SK-*` phải qua ISO 7064 MOD 37,36 | dùng lại `Sankit/qr/tools/ma_dinh_danh.py` |

Cài đặt: `scripts/kiem_tra.py` — chạy được cả JSON Schema lẫn 12 bất biến, thoát mã 1
khi có lỗi. I4 chính là bất biến bắt được lỗi gộp `VU`/`DOT_THU` ở bản dựng đầu.

## 3. Mã giống — phải thêm 4 mã, sửa hai chỗ

`Sankit/qr` hiện khai đúng hai mã: `CUC` (cúc chi), `CHA` (chanh). Bộ dữ liệu này dùng
thêm bốn:

| Mã | Loài | Dùng ở lô |
|---|---|---|
| `CCO` | Cúc cổ — *Chrysanthemum morifolium* Ramat. | L02 |
| `LAC` | Lạc — *Arachis hypogaea* L. | L01, L03 |
| `BCA` | Bồ công anh — *Lactuca indica* L. | L03, L05, L08, L11 |
| `UOM` | Luống ươm cây giống (không phải loài) | L10 |

Thêm giống mới phải sửa **hai chỗ cho khớp**, đúng như `docs/01_MA_DINH_DANH.md` của
`Sankit/qr` yêu cầu:

1. `Sankit/qr/tools/ma_dinh_danh.py` — hằng `GIONG`
2. `Sankit/qr/web/app.js` — hằng `GIONG`

Lệch một trong hai là sinh được mã mà trang không hiển thị tên giống.

`UOM` là chỗ gượng: nó không phải một loài. Cân nhắc tách `LO_DAT.muc_dich` gánh việc
này thay vì nhét vào mã giống — mã giống nằm trên tem đã in, đổi sau rất đắt.

## 4. Số học — đơn vị và độ chính xác

| Đại lượng | Đơn vị | Làm tròn | Ghi chú |
|---|---|---|---|
| `dien_tich_ha` | ha | 4 chữ số | tính trên EPSG:32648, không tính trên WGS84 |
| `ndvi`, `ndmi` | — | 4 chữ số | miền [−1, 1] |
| `vv_db`, `vh_db` | dB | 2 chữ số | **trung bình trên thang tuyến tính rồi mới đổi dB** |
| `mua`, `et0`, `thieu_nuoc` | mm | 1 chữ số | — |
| `nuoc_tuoi_can` | m³ | 1 chữ số | mm × 10 × ha |
| `khoi_luong_*` | kg | 1 chữ số | — |
| toạ độ | độ thập phân | 6 chữ số | ~0,1 m — quá mức cần thiết, ranh giới chỉ ±2,9 m |
| `cao_do_m` | m | 2 chữ số | GLO-30, sai số thẳng đứng vài m |

**Bẫy radar.** dB là hàm log. `mean(dB)` ≠ `dB(mean(linear))`. Mọi phép gộp VV/VH theo
tháng, theo lô, theo vụ đều phải đổi về tuyến tính trước. Cài đặt tham chiếu ở
`scripts/sinh_du_lieu.py`, hàm gộp `vh_thang` và `vh_tb`.

**Hai hướng bay radar phải tách riêng.** Cùng một thửa, lượt bay lên và lượt bay xuống
lệch nhau cả dB. Cột `huong_bay` (`asc`/`des`) đã có sẵn trong `quan_trac_radar.csv`.

## 5. Giá trị rỗng — ba loại khác nhau

| Giá trị | Nghĩa | Giao diện hiện gì |
|---|---|---|
| `null` | **chưa có** — chưa đo, chưa nhận văn bản | *"Chưa chốt"* + lý do |
| `""` (chuỗi rỗng trong CSV) | không áp dụng cho hàng này | để trống |
| thiếu ngày trong chuỗi quan trắc | mây che, lô không đủ 60 % pixel quang | **khoảng mù** trên biểu đồ, không nối đường thẳng qua |

Đừng vẽ đường liền qua khoảng mù. `data/dan_xuat/lo_thang.csv` có cột `nguon_ndvi` với
giá trị `quan_trac` | `noi_suy` | `khong_co` — 25/156 hàng là `noi_suy`. Giao diện phải
phân biệt được hai loại nét.

## 6. Cột `nguon` trên mọi bảng

Giữ nguyên luật của `Sankit/qr`, thêm một giá trị:

```
"that"      có bằng chứng đối chiếu được — ảnh vệ tinh, phiếu, file gốc
"mau"       dữ liệu dựng để demo
"dan_xuat"  tính ra từ số thật bằng công thức viết rõ (MỚI)
```

Trang phải gắn nhãn *"dữ liệu mẫu"* lên mọi khối `mau` và hiện dải cảnh báo ở đầu trang
chừng nào còn ít nhất một khối như vậy — như `Sankit/qr` đang làm. Khối `dan_xuat` cần
nhãn riêng: *"ước tính"* kèm link tới công thức.
