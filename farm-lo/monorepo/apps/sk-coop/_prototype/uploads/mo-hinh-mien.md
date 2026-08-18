# 01 — Mô hình miền

## 1. Chín thực thể

```
                    ┌──────────────┐
                    │    VUON      │  hợp tác xã, chứng nhận, địa chỉ
                    └──────┬───────┘
                           │ 1..n
                    ┌──────▼───────┐
      ┌─────────────┤   LO_DAT     ├─────────────┐   ← ĐO ĐƯỢC (GIS)
      │             │  L01 … L12   │             │     ranh giới, diện tích,
      │             └──────┬───────┘             │     cao độ, độ dốc
      │ 1..n               │ 1..n                │ 1..n
┌─────▼──────┐      ┌──────▼───────┐      ┌──────▼──────┐
│ QUAN_TRAC  │      │      VU      │      │  NHAT_KY    │  ← LỜI KHAI
│ ndvi/ndmi  │      │ một chu kỳ   │      │ gieo, bón,  │
│ vv/vh      │      │ gieo→kết thúc│      │ tưới, hái   │
│ ĐO ĐƯỢC    │      └──────┬───────┘      └─────────────┘
└────────────┘             │ 1..n
                    ┌──────▼───────┐
                    │   DOT_THU    │  một lượt hái trong vụ
                    └──────┬───────┘
                           │ 1..n
                    ┌──────▼───────┐        ┌─────────────┐
                    │   LO_HANG    │◄───────┤  CAY_CA_THE │  tem cắm ngoài vườn
                    │  SK-L-…      │  n..n  │  SK-C-…     │
                    └──────┬───────┘        └─────────────┘
                           │ 1..n
                    ┌──────▼───────┐        ┌─────────────┐
                    │     BICH     │        │  CANH_BAO   │  ← DẪN XUẤT
                    │   SK-B-…     │        │  R1 … R6    │
                    └──────────────┘        └─────────────┘
```

| Thực thể | Khoá | Lớp dữ liệu | File |
|---|---|---|---|
| `VUON` | `ma` | thật | `Sankit/qr/data/vuon/` |
| `LO_DAT` | **`lo_id`** | **thật — đo được** | `data/that/lo_ho_so.json` + `lo_ranh_gioi.geojson` |
| `QUAN_TRAC_QUANG` | `(lo_id, ngay)` | **thật** | `data/that/quan_trac_quang.csv` |
| `QUAN_TRAC_RADAR` | `(lo_id, ngay, huong_bay)` | **thật** | `data/that/quan_trac_radar.csv` |
| `KHI_HAU` | `ngay` | **thật** | `data/that/khi_hau_ngay.csv` |
| `VU` | `vu_id` | mô phỏng | `data/mo_phong/vu_canh_tac.json` — **18** bản ghi |
| `DOT_THU` | `dot_id` | mô phỏng | `data/mo_phong/dot_thu_hoach.json` — **25** bản ghi |
| `NHAT_KY` | `nk_id` | mô phỏng | `data/mo_phong/nhat_ky_dong_ruong.csv` |
| `LO_HANG` | `SK-L-…` | mô phỏng | `data/mo_phong/lo_hang.json` |
| `BICH` | `SK-B-…` | mô phỏng | `data/mo_phong/bich.json` |
| `CAY_CA_THE` | `SK-C-…` | 4 thật · 88 mô phỏng | `data/mo_phong/cay_ca_the.json` |
| `CANH_BAO` | `cb_id` | dẫn xuất | `data/dan_xuat/canh_bao.json` |

## 2. Hai loại sự thật, đừng trộn

Mô hình này đứng được là nhờ tách rạch ròi hai thứ:

| | **Đo được** | **Khai báo** |
|---|---|---|
| Là gì | vệ tinh, DEM, khí hậu | nhật ký người nhập |
| Ai tạo | máy, không qua tay farm | farm |
| Sửa được không | không | có |
| Ví dụ | `QUAN_TRAC_*`, `LO_DAT`, `KHI_HAU` | `VU`, `NHAT_KY`, `LO_HANG` |

**`CANH_BAO` là chỗ hai loại gặp nhau.** Mọi giá trị của sản phẩm nằm ở đó. Nếu app cho
phép sửa lớp "đo được" thì cả mô hình mất nghĩa — lúc đó chỉ còn là một cuốn sổ điện tử.

Hệ quả kỹ thuật: **lớp đo được phải chỉ-đọc ở tầng API**, không phải chỉ ở tầng UI.

## 3. Chỗ mô hình này gãy — `lô` quá thô

Ca 2.2 trong [BAO_CAO_DU_LIEU.md](../BAO_CAO_DU_LIEU.md): lô L02 rộng 0,9172 ha, cúc chi
chỉ chiếm khoảng một phần ba. Một đợt thu hoạch **có thật, có hồ sơ** không làm NDVI
trung bình cả lô nhúc nhích (+0,038). Radar bắt được (−0,74 dB), nhưng đó là may.

Ba lô nữa cùng dạng: **L10** (vườn ươm xen luống cúc), **L03** (ba vụ khác cây trong 14
tháng), **L08** (một nửa còn đang cải tạo).

Ba hướng, chưa chốt — đây là **Q3** trong báo cáo:

| Hướng | Được | Mất |
|---|---|---|
| Giữ `lô` là đơn vị nhỏ nhất | schema đơn giản, khớp mã `SK-C-…-L01-…` đã in | mất khả năng kiểm chứng ở lô trồng hỗn hợp; 4/12 lô bị ảnh hưởng |
| Thêm `KHOANH` dưới `LO_DAT`, có ranh giới riêng | kiểm chứng được tới từng luống | phải vẽ lại ranh giới trong lô; ranh giới khoảnh KHÔNG đo được từ ảnh 10 m |
| Không thêm bảng, chỉ thêm `ti_le_dien_tich` cho mỗi `VU` | rẻ, đủ để hạ ngưỡng cảnh báo theo tỉ lệ | vẫn không biết phần nào của lô; không vẽ được lên bản đồ |

Bộ dữ liệu này đang đi hướng thứ ba (`VU.ti_le_gieo`) vì nó không đụng tới mã đã in.
Đó là lựa chọn tạm, không phải kết luận.

## 3b. `VU` không phải `DOT_THU` — lỗi này bắt được bằng bất biến

Bản dựng đầu gộp hai khái niệm này làm một, và `scripts/kiem_tra.py` bắn đỏ **12 cặp**
vi phạm bất biến I4.

| | `VU` | `DOT_THU` |
|---|---|---|
| Là gì | một chu kỳ trồng: gieo → kết thúc | một lượt hái trong chu kỳ đó |
| Ví dụ | L11 bồ công anh, gieo 15/06/2025, lưu gốc | 4 lứa cắt: 10/2025 · 12/2025 · 03/2026 · 08/2026 |
| Ví dụ | L07 vườn chanh, trồng 2021 | 2 đợt thu quả: thu 2025 · hè 2026 |
| Ví dụ | L01 cúc chi 2025, gieo 10/07 | 1 đợt kéo 5 tuần (hoa nở dần, hái nhiều lượt) |
| Gắn với gì | nhật ký làm đất, bón lót, xuống giống | `LO_HANG`, phép đối chiếu vệ tinh |

Đếm trong bộ này: **18 vụ · 25 đợt thu**. Gộp làm một thì L11 thành "4 vụ chồng nhau
trên cùng 0,423 ha", và mọi phép tính diện tích gieo đều sai gấp bốn.

**Luật kèm theo:** cây lưu niên **không** mặc nhiên chiếm lô mãi mãi. Vụ lưu niên chỉ
để `ngay_ket_thuc: null` khi lô chưa được gieo thứ khác sau đợt thu cuối. Bồ công anh
vụ đông ở L03 kết thúc 30/12/2025 vì lạc xuân vào ngay sau đó — dù `BCA` mang cờ
`luu_nien: true`.

## 4. Quan hệ hai chiều đã có sẵn — giữ nguyên

`Sankit/qr` đã thiết kế mọi liên kết đi được hai chiều: lô hàng ↔ bịch ↔ cây. Ghép GIS
vào **thêm một chiều nữa**, và chiều này quan trọng nhất với bên mua sỉ:

```
SK-B-CUC26-0417-6  (bịch)
   └── lo_che_bien → SK-L-CUC25-10-S  (lô hàng)
          ├── nguon_cay → SK-C-CUC25-L01-0007-P …
          └── lo_dat_id → L01                       ← MỚI
                 ├── ranh giới, diện tích, độ dốc        (đo được)
                 ├── NDVI/NDMI/radar suốt vụ             (đo được)
                 ├── mưa, ET0, GDD tích luỹ cả vụ        (đo được)
                 └── nhật ký đồng ruộng + đối chiếu ảnh  (khai báo + kiểm)
```

Trường `trang_thai_lo_dat_luc_hai` và `khi_hau_ca_vu` đã có sẵn trong mỗi bản ghi
`lo_hang.json` — đội web dựng trang B2B là dùng được ngay, không phải join.

## 5. Vòng đời `LO_HANG`

```
dang_thu_hoach → dang_say → dang_phan_loai → dang_dong_goi
                                                   │
                                          cho_kiem_nghiem
                                                   │
                                          da_niem_ho_so ──► chỉ đọc, QR kích hoạt
                                                   │
                                              da_giao
```

`da_niem_ho_so` là mốc không đảo ngược: từ đó hồ sơ chỉ đọc và tem QR mới quét ra nội
dung. Trước đó quét vào không ra gì — đúng như `Sankit/qr` đang làm.

Phân bố trong bộ dữ liệu: 41 `da_giao` · 7 `cho_kiem_nghiem` · 4 `dang_thu_hoach` ·
2 `dang_dong_goi` · 1 `dang_say` · 1 `da_niem_ho_so` (còn lại là chanh bán tươi).

## 6. Ba app dùng thực thể nào

| | `sk-coop` (HTX) | `sk-ops` (Sankit Admin) | `sk-go` (hiện trường) |
|---|---|---|---|
| `LO_DAT` | xem + bản đồ | xem, sửa ranh giới | xem, định vị GPS |
| `QUAN_TRAC` | xem biểu đồ | chạy lại pipeline | xem số mới nhất |
| `VU` | **tạo, sửa** | duyệt | xem |
| `NHAT_KY` | xem, duyệt | xem | **nhập tại ruộng, offline** |
| `LO_HANG` | **tạo, niêm** | duyệt, đình chỉ | quét mã, cân |
| `CANH_BAO` | **xử lý** | cấu hình ngưỡng | nhận đẩy |
| `CAY_CA_THE` | quản lý tem | — | **gắn tem, chụp ảnh** |
