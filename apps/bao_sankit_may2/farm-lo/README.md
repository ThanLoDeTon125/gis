# sankit-farm-lo — Mô hình kiểm soát farm theo lô

Gói bàn giao cho đội web: **dữ liệu vệ tinh THẬT của 12 lô RiTi Farm, cộng một lớp
canh tác MÔ PHỎNG neo vào chính số liệu thật đó**, kèm mô hình miền, hợp đồng dữ liệu,
API và danh sách màn hình.

Ghép ba thứ đang rời nhau: `Sankit/gis` (đo được, không biết trồng gì) ·
`Sankit/qr` (truy xuất nguồn gốc, không biết đất ra sao) · `sankitmono` (khung chạy
được, chưa có nghiệp vụ). Khoá nối là **`lo_id`** — đã tồn tại sẵn ở cả hai đầu, không
phải sinh mã mới, không phải di trú gì.

**Bắt đầu ở đây → [BAO_CAO_DU_LIEU.md](BAO_CAO_DU_LIEU.md)**

---

## Chạy thử trong 20 giây

```bash
cd ~/Documents/Sankit/farm-lo
python3 scripts/sinh_du_lieu.py     # sinh lại toàn bộ — kết quả y hệt mỗi lần chạy
python3 scripts/kiem_tra.py         # schema + 12 bất biến, thoát mã 1 nếu sai
open web/ban-do.html                # giao diện giám sát — mở thẳng bằng trình duyệt
```

Dựng lại giao diện sau khi dữ liệu đổi (cần `Pillow` — có sẵn trong `.venv` của GIS):

```bash
../gis/.venv/bin/python scripts/dung_ban_do.py
```

`sinh_du_lieu.py` chỉ **đọc** từ `../gis/data/out/`. Không ghi
vào `Sankit/gis`, không ghi vào `Sankit`, không cần cài gói nào ngoài thư viện
chuẩn. `kiem_tra.py` cần `jsonschema` (có sẵn trong `.venv` của GIS).

## Có gì trong này

| | |
|---|---|
| [`BAO_CAO_DU_LIEU.md`](BAO_CAO_DU_LIEU.md) | báo cáo chính — dữ liệu thật, lịch canh tác mô phỏng, 4 ca kiểm chứng chéo, giới hạn, 6 việc cần chốt |
| [`docs/01_MO_HINH_MIEN.md`](docs/01_MO_HINH_MIEN.md) | 10 thực thể, quan hệ, và chỗ mô hình gãy |
| [`docs/02_HOP_DONG_DU_LIEU.md`](docs/02_HOP_DONG_DU_LIEU.md) | khoá, kiểu, đơn vị, 12 bất biến |
| [`docs/03_API_VA_MAN_HINH.md`](docs/03_API_VA_MAN_HINH.md) | bề mặt API `sk-backend` + màn hình `sk-coop`/`sk-ops`/`sk-go` + thứ tự dựng |
| [`docs/04_LUAT_CANH_BAO.md`](docs/04_LUAT_CANH_BAO.md) | 6 luật, ngưỡng, và vì sao đặt ngưỡng đó |
| [`docs/05_THAT_VA_MAU.md`](docs/05_THAT_VA_MAU.md) | phân định từng lớp: thật / mô phỏng / dẫn xuất, kèm công thức |
| [`monorepo/`](monorepo/) | **payload đã dựng sẵn theo cây thư mục sankitmono** — chép vào repo là xong. Kèm [HUONG_DAN_DAY_LEN.md](monorepo/HUONG_DAN_DAY_LEN.md): tên nhánh, commit, mô tả PR, checklist gate |
| [`web/ban-do.html`](web/ban-do.html) | **giao diện giám sát chạy được** — bản đồ vệ tinh 12 lô, bấm vào lô ra toàn bộ thông tin. Một file tự chứa, mở bằng trình duyệt là chạy, không cần server, không gọi mạng |
| [`schema/sankit-farm-lo.d.ts`](schema/sankit-farm-lo.d.ts) | kiểu TypeScript — chép thẳng vào `packages/types` |
| [`schema/sankit-farm-lo.schema.json`](schema/sankit-farm-lo.schema.json) | JSON Schema draft 2020-12 |

## Dữ liệu

```
data/that/        ĐO ĐƯỢC — vệ tinh, DEM, khí hậu. Chỉ đọc, KHÔNG sửa.
  lo_ranh_gioi.geojson    12 lô, EPSG:4326, sai số ±2,9 m
  lo_ho_so.json           hồ sơ 12 lô: diện tích, địa hình, NDVI/NDMI/radar tổng hợp
  quan_trac_quang.csv     249 bản ghi Sentinel-2 (lô × ngày)
  quan_trac_radar.csv     684 bản ghi Sentinel-1 (lô × ngày × hướng bay)
  khi_hau_ngay.csv        366 ngày Open-Meteo (ERA5)
  khi_hau_thang.csv       mưa, ET0, cân bằng nước, độ ẩm đất theo tháng
  chu_ky_ndvi.csv         17 chu kỳ dò tự động
  tho_nhuong.json         SoilGrids — 250 m, KHÔNG phân biệt được lô

data/mo_phong/    DỰNG — thay bằng dữ liệu thật khi HTX bắt đầu nhập
  vu_canh_tac.json        18 vụ
  dot_thu_hoach.json      25 đợt thu
  cay_trong.json          7 loại cây: Kc FAO-56, năng suất tham chiếu
  nhat_ky_dong_ruong.csv  584 bản ghi
  lo_hang.json            101 lô hàng, mã đã qua ISO 7064
  bich.json               120 bịch có hồ sơ (31 765 theo số đếm)
  cay_ca_the.json         92 cây có tem (4 lấy từ hồ sơ THẬT của Sankit)
  nhan_su.json            6 người — NHÂN VẬT HƯ CẤU
  lech_co_y.json          2 bản ghi cắm SAI có chủ ý, để dựng màn hình cảnh báo

data/dan_xuat/    TÍNH RA từ hai lớp trên, công thức ở docs/05
  lo_thang.csv                    156 hàng (12 lô × 13 tháng) ← bảng dùng nhiều nhất
  canh_bao.json                   89 cảnh báo từ 6 luật
  doi_chieu_nhat_ky_ve_tinh.json  22 đợt thu đối chiếu lời khai với ảnh
```

## Ba điều đừng làm

1. **Đừng sửa `data/that/`.** Đó là lớp đo được. Cả mô hình đứng được là nhờ nó không
   qua tay ai. API cũng không được mở đường ghi vào lớp này (bất biến I8).
2. **Đừng dựng phiếu kiểm nghiệm.** Cả 101 lô hàng đều `kiem_nghiem: null` — cố ý, đúng
   luật `nguon` của `Sankit/qr`. Mục trống có chú thích trung thực hơn mục biến mất.
3. **Đừng bỏ nhãn `nguon`.** Mọi bản ghi mang `that` | `mau` | `dan_xuat`. Trang phải
   gắn nhãn *"dữ liệu mẫu"* lên khối `mau` và *"ước tính"* lên khối `dan_xuat`.

## Sáu việc cần chốt trước khi code

Chi tiết ở [§8 của báo cáo](BAO_CAO_DU_LIEU.md). Tóm tắt:

| | |
|---|---|
| Q1 | định nghĩa lại "lô hàng" ở quy mô thương mại |
| Q2 | thêm 4 mã giống `CCO` `LAC` `BCA` `UOM` — sửa **hai chỗ** trong `Sankit/qr` |
| Q3 | có thêm tầng `khoảnh` dưới `lô` không |
| Q4 | vùng trồng ở Nho Quan hay Hoa Lư — CC-06 vẫn chưa có câu trả lời |
| Q5 | ai nhập nhật ký, và engine sync offline nào cho `sk-go` |
| Q6 | ảnh vệ tinh cập nhật tự động kiểu gì |
