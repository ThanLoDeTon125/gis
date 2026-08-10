# @sankit/schema-adapter

Cầu nối giữa **schema đích** và giới hạn structured outputs của model. Ticket
[SAN-79](https://linear.app/sankit/issue/SAN-79), thuộc epic
[SAN-72](https://linear.app/sankit/issue/SAN-72).

Đã chốt (10/08/2026): file JSON trong resource của
[SAN-78](https://linear.app/sankit/issue/SAN-78) là **schema đích**. File chưa
về repo — package này làm trước phần không phụ thuộc hình dạng schema, để ngày
file về là chạy được ngay:

| Module        | Việc                                                                                        |
| ------------- | ------------------------------------------------------------------------------------------- |
| `lint.ts`     | kiểm schema có dùng được với structured outputs không (danh sách chặn theo khảo sát SAN-80) |
| `flatten.ts`  | cây điều khoản ↔ mảng phẳng `ma`/`ma_cha` — đường né schema đệ quy                          |
| `validate.ts` | kiểm dữ liệu (gold của SAN-81, output model) theo schema đích                               |

## Ngày file JSON của SAN-78 về thì làm gì

```bash
pnpm --filter @sankit/schema-adapter cli -- lint schema-dich.json
```

- **Sạch** → gửi thẳng schema cho API, SAN-79 không cần tầng chuyển đổi.
- **Dính `recursive-ref`** → đi đường mảng phẳng: `treeToFlat` / `flatToTree`,
  đúng phương án khảo sát SAN-80 khuyến nghị.
- Các lỗi khác (`minLength`, `minimum`…) → bỏ ràng buộc khỏi schema gửi model,
  kiểm lại ở tầng ứng dụng bằng `validate.ts`.

Kiểm gold trước khi dán nhãn hàng loạt (và output model trước khi vào rule-engine):

```bash
pnpm --filter @sankit/schema-adapter cli -- validate --schema schema-dich.json data/gold
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
