# Đẩy lớp GIS theo lô vào `sankitmono`

Thư mục này là **payload đã dựng sẵn theo đúng cây thư mục của monorepo**. Chép vào repo
là xong, không phải sắp xếp lại gì.

Làm theo đúng quy trình mà `sk-ops` đã đi (`feat/sk-ops-ingest-prototype` → `…-ui-prototype`
→ `…-component-base`): **nạp trước, dựng sau**.

> ⚠ `qr/` **không** nằm trong monorepo — nó ở repo riêng `quocbao271207/bao_sankit_may2`.
> Quy trình chép ở đây là quy trình nạp prototype của `sk-ops`/`sk-coop`/`sk-go`, không
> phải quy trình của `qr`.

---

## 0. Trước khi bắt đầu

`CONTRIBUTING.md §1`: **không có ticket thì không mở PR.** Cần tạo trước trên Linear:

| Ticket | Nội dung | Ước lượng |
|---|---|---|
| **A** — `sk-coop: nạp lớp GIS theo lô vào _prototype` | tài liệu + bản dựng + dữ liệu, không đụng code | nửa ngày |
| **B** — `types: kiểu dữ liệu cho lớp GIS theo lô` | `packages/types` | nửa ngày |
| **C** — `sk-coop: màn Registry — bản đồ thửa` | dựng UI thật, **mở sau khi chốt Q1–Q10** | chưa ước lượng |

Ticket **C** cố ý chưa mô tả chi tiết: [`apps/sk-coop/FARM_LO_INGEST.md`](apps/sk-coop/FARM_LO_INGEST.md) §8
có 10 câu chưa chốt, trong đó **Q3** (Batch ứng với cái gì) và **Q4** (sk-coop chưa theme)
chặn thẳng việc dựng UI.

Kiểm trước khi bắt đầu, đúng như CONTRIBUTING §0 yêu cầu:

```sh
cd ~/Documents/sankitmono
pnpm install && pnpm build && pnpm lint && pnpm test
```

---

## 1. PR A — nạp prototype (không đụng code)

```sh
cd ~/Documents/sankitmono
git switch main && git pull
git switch -c SAN-<A>-sk-coop-ingest-farm-lo

# bản dựng chạy được + tài liệu + dữ liệu
cp -R ~/Documents/Sankit/farm-lo/monorepo/apps/sk-coop/_prototype/. apps/sk-coop/_prototype/
git add apps/sk-coop/_prototype
git commit -m "docs(sk-coop): đưa bản dựng GIS theo lô và bộ dữ liệu RiTi vào _prototype"

# ghi chép nạp
cp ~/Documents/Sankit/farm-lo/monorepo/apps/sk-coop/FARM_LO_INGEST.md apps/sk-coop/
git add apps/sk-coop/FARM_LO_INGEST.md
git commit -m "docs(sk-coop): ghi chép nạp lớp GIS — token, từ vựng, 10 câu chưa chốt"

git push -u origin HEAD
```

**Không cần chạy lại gate.** `_prototype/` đã bị loại khỏi cả ba: `.oxlintrc.json`
(`ignorePatterns`), `.prettierignore`, và `tsconfig.app.json` (`include: ["src"]`).
PR này không đổi một dòng code nào.

**Title PR:** `SAN-<A>: sk-coop — nạp lớp GIS theo lô vào _prototype`

<details><summary>Mô tả PR (chép nguyên)</summary>

```
Nạp bộ dữ liệu GIS 12 lô của RiTi Farm vào _prototype của sk-coop, để dựng màn
Registry (brief §3.4). Không đụng code, không đổi build.

Vào những gì
- _prototype/ban-do-lo.html — bản dựng chạy được: bản đồ ảnh vệ tinh, 12 lô bấm
  được, thanh 13 tháng, 4 lớp tô, thanh bên chi tiết từng lô. Một file tự chứa,
  mở bằng trình duyệt là chạy.
- _prototype/du-lieu/ — dữ liệu: 249 quan trắc quang (Sentinel-2), 684 radar
  (Sentinel-1), 366 ngày khí hậu, ranh giới 12 lô ±2,9 m, cộng lớp canh tác mô phỏng.
- _prototype/uploads/ — báo cáo dữ liệu, mô hình miền, hợp đồng dữ liệu (12 bất
  biến), luật cảnh báo, bảng phân định thật/mô phỏng.
- FARM_LO_INGEST.md — ghi chép nạp, cùng vai trò với sk-ops/DESIGN_TOKENS.md.

Phát hiện đáng chú ý
- Prototype Coop Dashboard ĐÃ chừa sẵn chỗ cho GIS: mapRef, gisMapped/gisUnmapped,
  onDrawToggle, ô tìm địa điểm. Lần nạp này cấp đúng phần dữ liệu còn thiếu.
- Bộ token của bản dựng bị BỎ, dùng giá trị sk-coop (teal #128173, Plus Jakarta
  Sans / Barlow / IBM Plex Mono, bo góc 4px) — giống cách sk-ops đã làm.
- Bảng màu mã hoá dữ liệu thì GIỮ: đã qua trình kiểm mù màu, đạt toàn bộ ở cả hai
  chế độ sáng/tối. Đổi tay là hỏng.

10 câu chưa chốt ở FARM_LO_INGEST.md §8. Chặn nặng nhất:
- Q1 cảnh báo từ vệ tinh có phải là Issue không (hợp đồng §4 chỉ định nghĩa Issue
  do Rule trong sk-ops bắn ra)
- Q3 hợp đồng §5 có một khái niệm Crop/Batch, bộ này cần ba tầng vụ → đợt thu → lô hàng
- Q4 sk-coop vẫn đang là scaffold Geist mặc định, trong khi sk-ops đã theme theo
  chính prototype của sk-coop

Đã test: mở _prototype/ban-do-lo.html bằng Chrome/Safari, sáng + tối, 1440px và 520px.
```
</details>

---

## 2. PR B — kiểu dữ liệu dùng chung

```sh
git switch main && git pull
git switch -c SAN-<B>-types-farm-lo

cp ~/Documents/Sankit/farm-lo/monorepo/packages/types/src/farm-lo.ts packages/types/src/
cp ~/Documents/Sankit/farm-lo/monorepo/packages/types/src/index.ts   packages/types/src/

pnpm build && pnpm lint && pnpm test        # phải xanh cả ba
git add packages/types/src
git commit -m "feat(types): thêm kiểu cho lớp GIS theo lô — thửa, vụ, quan trắc, Issue"
git push -u origin HEAD
```

26 kiểu, đã kiểm sẵn bằng đúng công cụ của repo:

| Gate | Kết quả |
|---|---|
| `tsc 6.0.3 --strict` với `@sankit/config/tsconfig.base.json` | không lỗi, emit được cả `.js` lẫn `.d.ts` |
| `oxlint` | sạch |
| `oxfmt --check` | sạch (đã chạy `oxfmt` một lần) |

**Một khác biệt với `extraction-eval` — cần team quyết.** `packages/extraction-eval`
import kèm đuôi (`from "./align.ts"`) và bật `allowImportingTsExtensions` trong tsconfig
riêng. `packages/types` **chưa** bật cờ đó, nên `index.ts` ở đây import không đuôi
(`from "./farm-lo"`). Cách này chạy đúng với tsconfig hiện tại, **không phải sửa config gì**.
Nếu muốn thống nhất kiểu import toàn repo thì tách một ticket riêng — đừng gộp vào PR này.

**Title PR:** `SAN-<B>: types — kiểu dữ liệu cho lớp GIS theo lô`

---

## 3. PR C — dựng màn Registry (sau khi chốt Q1–Q10)

Chưa dựng sẵn, cố ý. Đi theo đúng bố cục mà `sk-ops` đã dùng:

```
apps/sk-coop/src/
  components/
    layout/          app-shell · header · sidebar · nav-items
    ui/              shadcn: card · badge · table · select · tooltip · separator
    design-system/   status-pill · progress-ring · kpi-card · tag   (dùng chung, hợp đồng §6)
  features/
    registry-plots/
      registry-plots-page.tsx     màn "Bản đồ thửa"
      plot-map.tsx                bản đồ + polygon + pan/zoom
      plot-detail-panel.tsx       thanh bên
      plot-data.ts                dữ liệu seed, có kiểu   ← giống fleet-data.ts của sk-ops
      plot-status.ts              tính tình trạng thửa thành một câu
```

Chỗ đáng lấy thẳng từ bản dựng `_prototype/ban-do-lo.html`:

| Cần gì | Lấy ở đâu |
|---|---|
| Chiếu toạ độ lô lên ảnh nền | `scripts/dung_ban_do.py` của gói gốc, hàm `to_px` — **Mercator**, không phải nội suy tuyến tính theo vĩ độ |
| Ngưỡng chia 5 mức độ xanh | hằng `BANDS` |
| Bảng dịch thuật ngữ ra tiếng người dùng | hằng `TU_DIEN` |
| Câu “nên làm gì” cho từng luật | hằng `LUAT[*].lam` |
| Tính tình trạng thửa thành một câu | hàm `tinhTrang` |
| Bảng màu mã hoá đã kiểm mù màu | hằng `RAMP`, `NHOM_MAU` |

**Đừng chép token giao diện của bản dựng** — xem `FARM_LO_INGEST.md` §5.

---

## 4. Trước khi request review (CONTRIBUTING §3)

- [ ] `pnpm build` · `pnpm lint` · `pnpm test` xanh
- [ ] Nhánh tách từ `main`, tên có ticket ID
- [ ] Commit theo Conventional Commits, scope là `sk-coop` / `types`
- [ ] PR title `SAN-<id>: <đổi cái gì>`, có link Linear
- [ ] Ảnh chụp màn hình cho mọi thay đổi UI
- [ ] **Squash merge**, title commit squash = title PR
- [ ] Xoá nhánh sau khi merge

---

## 5. Cập nhật lại khi dữ liệu đổi

Bộ dữ liệu sinh lại được từ đầu, kết quả y hệt mỗi lần chạy:

```sh
cd ~/Documents/Sankit/farm-lo
python3 scripts/sinh_du_lieu.py     # đọc ../gis/data/out/, không ghi đâu khác
python3 scripts/kiem_tra.py         # JSON Schema + 12 bất biến, thoát mã 1 nếu sai
../gis/.venv/bin/python scripts/dung_ban_do.py   # dựng lại bản đồ
```

Rồi chép lại vào `_prototype/` như bước 1. **Sửa `FARM_LO_INGEST.md` trước, code sau** —
đúng luật mà `sk-ops/DESIGN_TOKENS.md` đã đặt ra.
