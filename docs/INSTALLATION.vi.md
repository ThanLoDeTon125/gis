# Installation

Set up Sankit monorepo ở máy local. Giả định bạn đã làm xong [PREREQUISITES.md](./PREREQUISITES.vi.md)
(Node 24, pnpm 11.9.0, `gh` đã đăng nhập).

---

## 1. Clone

```sh
gh repo clone SANKIT-PRODUCT/sankitmono
cd sankitmono
```

## 2. Chọn Node 24

Repo ghim Node qua `.nvmrc`:

```fish
nvm use          # reads .nvmrc → Node 24
```

## 3. Cài dependencies

```sh
pnpm install
```

> `node-linker=hoisted` được set cho toàn repo (`.npmrc` + `pnpm-workspace.yaml`) — **bắt buộc** để
> Expo/Metro resolve được workspace dep. Đừng bỏ nó đi.

## 4. Kiểm tra workspace đã xanh

```sh
pnpm build      # turbo run build — all workspaces
pnpm lint       # oxlint over the repo
pnpm test       # turbo run test — Vitest per workspace
```

Cả ba đều phải exit `0`. `pnpm test` bao gồm cả check `GET /health` → 200 của api, và các smoke test
render + Cloudflare Worker của hai web app.

---

## Chạy một app ở chế độ dev

| App | Command | Mở ra |
| --- | --- | --- |
| `api` (NestJS) | `pnpm --filter api start:dev` | `http://localhost:3000/health` → `{ "status": "ok" }` |
| `sk-ops` (Web Admin) | `pnpm --filter sk-ops dev` | Vite dev server → **"Web Admin"** |
| `sk-hub` (Web HTX) | `pnpm --filter sk-hub dev` | Vite dev server → **"Web HTX"** |
| `sk-go` (Expo) | `pnpm --filter sk-go exec expo start` | Expo dev server (bấm `i` / `a` / scan QR) |

---

## Formatting

Lint/format **chỉ dùng oxlint + oxfmt** (không ESLint/Prettier):

```sh
pnpm format        # oxfmt . (writes)
pnpm format:check  # oxfmt --check . (CI / pre-PR)
```

---

## Troubleshooting

| Triệu chứng | Cách xử lý |
| --- | --- |
| `nest: Permission denied` (exit 126) sau khi `pnpm add/remove` incremental | Hoisted linker có thể xoá mất exec bit trên `@nestjs/cli/bin/nest.js`. Chạy clean install: `rm -rf node_modules && pnpm install`. |
| Expo: "Unable to resolve module" / React bị trùng | Đảm bảo `node-linker=hoisted` còn nguyên và `apps/sk-go/metro.config.js` vẫn có; chạy lại `pnpm install`. |
| `pnpm` crash với `Cannot use 'in' operator ... 'integrity'` | `package.json` ở root phải dùng string `packageManager`, **không** phải `devEngines` (một bug của pnpm 11.9.0). Đừng đưa `devEngines` trở lại. |
| Cloudflare Worker test: `ERR_FUTURE_COMPATIBILITY_DATE` | `compatibility_date` trong `wrangler.jsonc` không được vượt quá `workerd` đang bundle. Hạ nó xuống, hoặc bump `workerd`. |
| `pnpm` sai version | `corepack prepare pnpm@11.9.0 --activate`. |

---

Tiếp theo: đọc [CONTRIBUTING.md](../CONTRIBUTING.vi.md) trước khi bắt tay vào thay đổi gì.
