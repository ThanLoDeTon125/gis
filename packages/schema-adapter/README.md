# @sankit/schema-adapter

Cầu nối giữa **schema đích** và giới hạn structured outputs của model. Ticket
[SAN-79](https://linear.app/sankit/issue/SAN-79), thuộc epic
[SAN-72](https://linear.app/sankit/issue/SAN-72).

Đã chốt (10/08/2026): file JSON trong resource của
[SAN-78](https://linear.app/sankit/issue/SAN-78) là **schema đích** — đã về
repo cùng ngày tại [`schema/san78/`](./schema/san78):

| Module        | Việc                                                                                        |
| ------------- | ------------------------------------------------------------------------------------------- |
| `lint.ts`     | kiểm schema có dùng được với structured outputs không (danh sách chặn theo khảo sát SAN-80) |
| `flatten.ts`  | cây điều khoản ↔ mảng phẳng `ma`/`ma_cha` — đường né schema đệ quy                          |
| `validate.ts` | kiểm dữ liệu (gold của SAN-81, output model) theo schema đích                               |

## Schema đích — kết quả lint (10/08/2026)

File trong resource SAN-78 là **dữ liệu mẫu**, không phải JSON Schema hình
thức. Schema hình thức suy từ nó nằm ở `schema/schema-dich.json`: mảng tài
liệu, mỗi tài liệu `{source, document_type, language, chunks[{section,
content, tags[]}]}`.

| File                        | Là gì                                                  |
| --------------------------- | ------------------------------------------------------ |
| `schema/san78/output.json`  | exemplar gốc từ resource SAN-78 (3 tài liệu, 27 chunk) |
| `schema/san78/corpus.jsonl` | cùng dữ liệu, phẳng theo chunk, thêm `id`              |
| `schema/schema-dich.json`   | JSON Schema hình thức suy từ exemplar                  |

Phán quyết (đã chạy `cli -- lint` và `cli -- validate` trên file thật):

- Schema **phẳng, không đệ quy** → gửi thẳng cho structured outputs được:
  lint 0 lỗi 0 cảnh báo, exemplar validate 1/1.
- **Chưa cần** đường mảng phẳng của `flatten.ts` — giữ làm bảo hiểm nếu schema
  đích sau này thêm phân cấp điều khoản (`ma`/`ma_cha`).
- Mỗi lần gọi model trích MỘT tài liệu → schema gửi API là phần `items`
  (structured outputs cần root là object).
- Lưu ý cho team: exemplar KHÔNG có mã điều khoản, phân cấp, hay mức bắt buộc
  như khảo sát SAN-80 giả định — nếu rule-engine cần các field đó thì phải mở
  rộng schema đích, quyết định ở cấp epic SAN-72.

Kiểm gold trước khi dán nhãn hàng loạt (và output model trước khi vào rule-engine):

```bash
pnpm --filter @sankit/schema-adapter cli -- validate --schema schema/schema-dich.json data/gold
```

Exit code: 0 sạch, 1 có lỗi — cắm vào CI được.

## Vì sao tách package riêng

Harness đo ([`@sankit/extraction-eval`](../extraction-eval)) cố tình
schema-agnostic — không được biết schema đích. Ngược lại, mọi thứ ở đây xoay
quanh schema đích. Trộn hai package là harness mất tính agnostic; tách ra thì
bên đo và bên thi hành schema tiến hoá độc lập.

## Test

```bash
pnpm --filter @sankit/schema-adapter test
```

Chỉ dùng stdlib + vitest, không thêm dependency runtime nào.
