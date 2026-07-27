# Installation

Tài liệu này hướng dẫn bạn set up Sankit monorepo trên máy của bạn. Hoàn thành
[PREREQUISITES.md](./PREREQUISITES.vi.md) trước (Node 24, pnpm 11.9.0, `gh` đã đăng nhập).

---

## 1. Clone repository

```sh
gh repo clone SANKIT-PRODUCT/sankitmono
cd sankitmono
```

## 2. Chọn Node 24

Repository ghim phiên bản Node trong `.nvmrc`:

```fish
nvm use          # reads .nvmrc → Node 24
```

## 3. Cài dependency

```sh
pnpm install
```

> Repository set `node-linker=hoisted` trong `.npmrc` và `pnpm-workspace.yaml`. Expo/Metro **bắt
> buộc** cần setting này để resolve workspace dependency. Không được bỏ nó.

## 4. Kiểm tra workspace xanh

```sh
pnpm build      # turbo run build — all workspaces
pnpm lint       # oxlint over the repo
pnpm test       # turbo run test — Vitest per workspace
```

Kiểm tra rằng mỗi lệnh exit với code `0`. Lệnh `pnpm test` bao gồm check `GET /health` → 200 của
sk-backend. Nó cũng bao gồm các test render và các smoke test Cloudflare Worker của các web app.

---

## Chạy một app ở chế độ dev

| App                  | Command                               | Kết quả                                               |
| -------------------- | ------------------------------------- | ----------------------------------------------------- |
| `sk-backend` (Hono)  | `pnpm --filter sk-backend dev`        | `http://localhost:8787/health` → `{ "status": "ok" }` |
| `sk-ops` (Web Admin) | `pnpm --filter sk-ops dev`            | Vite dev server → **"Web Admin"**                     |
| `sk-coop` (Web HTX)  | `pnpm --filter sk-coop dev`           | Vite dev server → **"Web HTX"**                       |
| `sk-go` (Expo)       | `pnpm --filter sk-go exec expo start` | Expo dev server (bấm `i` / `a`, hoặc scan QR)         |

---

## Format code

Chỉ dùng **oxlint + oxfmt** cho lint và format. Không dùng ESLint hoặc Prettier.

```sh
pnpm format        # oxfmt . (writes)
pnpm format:check  # oxfmt --check . (CI / pre-PR)
```

---

## Troubleshooting

| Triệu chứng                                                                   | Cách xử lý                                                                                                                               |
| ----------------------------------------------------------------------------- | ---------------------------------------------------------------------------------------------------------------------------------------- |
| Binary của workspace báo `Permission denied` (exit 126) sau `pnpm add/remove` | Hoisted linker có thể xoá exec bit trên binary của workspace. Chạy clean install: `rm -rf node_modules && pnpm install`.                 |
| Expo báo "Unable to resolve module" hoặc React bị trùng                       | Kiểm tra rằng `node-linker=hoisted` còn nguyên và `apps/sk-go/metro.config.js` vẫn có. Sau đó chạy lại `pnpm install`.                   |
| `pnpm` dừng với `Cannot use 'in' operator ... 'integrity'`                    | `package.json` ở root phải dùng string `packageManager`, **không** dùng `devEngines` (bug của pnpm 11.9.0). Không thêm lại `devEngines`. |
| Test Cloudflare Worker báo `ERR_FUTURE_COMPATIBILITY_DATE`                    | `compatibility_date` trong `wrangler.jsonc` không được mới hơn `workerd` đi kèm. Hạ ngày xuống, hoặc update `workerd`.                   |
| `pnpm` sai phiên bản                                                          | Chạy `corepack prepare pnpm@11.9.0 --activate`.                                                                                          |

---

Đọc [CONTRIBUTING.md](../CONTRIBUTING.vi.md) trước khi bạn thay đổi gì.
