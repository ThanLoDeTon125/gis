# Sankit — Next Gen Farming

Tài liệu và sản phẩm cho dự án/cuộc thi **Sankit Next Gen Farming** (hạng mục University).

Web giám sát 12 lô RiTi Farm là file tĩnh `farm-lo/web/ban-do.html` — không cần Node, `pnpm`, hay build.

---

## Khởi động web (local)

Cần **Python 3** và **một** cổng 8080 trống. Mở bằng **Chrome hoặc Edge** (Simple Browser trong Cursor dễ chỉ hiện ảnh nền).

### Windows (PowerShell)

```powershell
cd "c:\Users\BabyTiger\Downloads\sankitmono-gis-farm-lo\sankitmono-gis-farm-lo\apps\bao_sankit_may2"
python -m http.server 8080
```

### macOS / Linux

```sh
cd apps/bao_sankit_may2
python3 -m http.server 8080
```

Rồi mở trình duyệt:

- http://127.0.0.1:8080/
- hoặc http://127.0.0.1:8080/farm-lo/web/ban-do.html

Dùng `127.0.0.1` thay vì `localhost` trên Windows.

**Không** chạy lệnh `python -m http.server 8080` lần thứ hai khi server đã sống — hai process cùng cổng sẽ bị Connection reset.

Dừng server: `Ctrl+C` trong terminal đang chạy.

Web đủ chức năng khi thấy **ô màu 12 lô**, **danh sách lô** (cột phải hoặc panel đáy), bấm lô ra chi tiết, và các nút Độ xanh cây / Loại cây / Cần chú ý / So sánh lô.

### Cách nhanh (không cần server)

Mở thẳng file bằng Chrome/Edge:

`farm-lo/web/ban-do.html`

File này tự chứa ảnh + dữ liệu + JS. Cách HTTP ở trên khớp đường dẫn deploy (`/` → bản đồ).

---

## Deploy

Static site. Root deploy phải là thư mục **`bao_sankit_may2`** (chỗ có `vercel.json` và `index.html`), không phải cả monorepo.

### Vercel (đã có `vercel.json`)

```powershell
cd apps/bao_sankit_may2
npx vercel
```

- Framework: Other
- Build command: để trống
- Output directory: để trống

Production: `npx vercel --prod`

Nếu gắn GitHub, **Root Directory** = `sankitmono-gis-farm-lo/apps/bao_sankit_may2`.

`/` được rewrite sang `/farm-lo/web/ban-do.html`.

Gói tối thiểu: `index.html`, `vercel.json`, `farm-lo/web/`. Không cần `gis/`, `books/`, `data/` để site chạy.

---

## Sửa giao diện rồi dựng lại HTML

Sửa nguồn trong `farm-lo/scripts/` (`_ban_do.html`, `_ban_do.js`, `_ban_do.css`), rồi:

```powershell
cd farm-lo
python scripts\dung_ban_do.py
```

Cần Pillow (thường có trong `gis/.venv`). Kết quả ghi đè `farm-lo/web/ban-do.html`.

Sinh lại dữ liệu (không bắt buộc để xem web):

```powershell
cd farm-lo
python scripts\sinh_du_lieu.py
python scripts\kiem_tra.py
```

---

## Nội dung thư mục

- `farm-lo/web/ban-do.html` — giao diện giám sát
- `index.html` · `vercel.json` — vào `/` thì tới bản đồ
- `farm-lo/` — dữ liệu lô, schema, tài liệu mô hình
- `gis/` — pipeline Python (không phải web)
- `Sankit_Next_Gen_Farming_Report_Round_1_University_Category.pdf` — báo cáo vòng 1
- `books/`, `docs/`, `DESIGN.md`, `HUONG_DAN_CHUP_SACH.md`

`rag_duocdien/` là dự án riêng — [RAG_DUOC_DIEN_1](https://github.com/quocbao271207/RAG_DUOC_DIEN_1) — không nằm trong repo này.
