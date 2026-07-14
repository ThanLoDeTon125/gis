# Sankit Monorepo

> 🇬🇧 English: [README.md](./README.md)

Bộ khung chạy được (runnable skeleton) cho **Sankit** — nền tảng GACP-compliance / truy xuất nguồn gốc
cho dược liệu Việt Nam. Ba app cho ba nhóm người dùng, cộng thêm các shared package. Repo này là cái
scaffold rỗng để các feature ticket sau này xây lên: **chưa có business logic, chưa có schema, chưa
wiring auth.**

> 🔒 **Proprietary & confidential.** Chỉ những thành viên được cấp quyền trong team mới được truy cập —
> xem [LICENSE.md](./LICENSE.vi.md). Không chia sẻ source, config hay quy trình setup ra ngoài.

## Documentation

| Doc | Mục đích |
| --- | --- |
| [docs/PREREQUISITES.md](./docs/PREREQUISITES.vi.md) | Cài bộ toolchain cho dev (Ghostty, Fish, Fisher, nvm.fish, pnpm, OrbStack, LazyGit, …) |
| [docs/INSTALLATION.md](./docs/INSTALLATION.vi.md) | Clone + setup + chạy repo |
| [CONTRIBUTING.md](./CONTRIBUTING.vi.md) | Quy trình làm việc — PR gắn với Linear ticket, các house rule |
| [docs/vision.md](./docs/vision.vi.md) | Định hướng sản phẩm, phạm vi, và các quyết định kỹ thuật đã chốt |
| [LICENSE.md](./LICENSE.vi.md) | License proprietary & confidential |

**Mới vào?** Bắt đầu từ [PREREQUISITES](./docs/PREREQUISITES.vi.md) → [INSTALLATION](./docs/INSTALLATION.vi.md) → [CONTRIBUTING](./CONTRIBUTING.vi.md).

## Quick start

```sh
nvm use          # Node 24 (see .nvmrc)
pnpm install     # node-linker=hoisted — required for Expo
pnpm build && pnpm lint && pnpm test
```

Setup đầy đủ: [docs/INSTALLATION.md](./docs/INSTALLATION.vi.md).

## Repo-wide commands

| Command | Làm gì |
| --- | --- |
| `pnpm build` | `turbo run build` trên tất cả workspace |
| `pnpm test` | `turbo run test` → Vitest cho từng workspace |
| `pnpm lint` | `oxlint` trên toàn repo |
| `pnpm format` | `oxfmt .` (ghi đè) |
| `pnpm format:check` | `oxfmt --check .` |

Lint/format **chỉ dùng oxlint + oxfmt** (không ESLint/Prettier). Test **dùng Vitest** ở mọi nơi
(không Jest). TypeScript được ghim ở **6.0.3** (nhánh stable hiện tại; chưa dùng native compiler TS 7).

## Dev per app

| App | Command | Ghi chú |
| --- | --- | --- |
| `api` (NestJS) | `pnpm --filter api start:dev` | `GET /health` → 200 |
| `sk-ops` (Vite + React) | `pnpm --filter sk-ops dev` | route render ra **"Web Admin"** |
| `sk-hub` (Vite + React) | `pnpm --filter sk-hub dev` | route render ra **"Web HTX"** |
| `sk-go` (Expo) | `pnpm --filter sk-go exec expo start` | một màn hình rỗng ("Sankit Go") |

Hai web app deploy dưới dạng **Cloudflare Workers với static-assets binding** (qua
`@cloudflare/vite-plugin`), **không** phải Cloudflare Pages — chọn vậy vì Cloudflare giờ hướng các
project mới sang Workers Static Assets, và cách này cho phép smoke test `vitest-pool-workers` chạy
thẳng vào Worker entry thật của từng app.

## Directory structure

```
sankitmono
├── package.json                 # root; scripts build/lint/test/dev/format
├── pnpm-workspace.yaml          # packages: apps/*, packages/* + nodeLinker: hoisted
├── .npmrc                       # node-linker=hoisted
├── turbo.json                   # tasks: build/test/lint/dev
├── tsconfig.json                # extends @sankit/config/tsconfig.base.json
├── .oxlintrc.json               # extends @sankit/config oxlint base
├── .nvmrc                       # 24
├── CLAUDE.md · AGENTS.md        # AI-agent guidance (AGENTS.md → CLAUDE.md symlink)
├── docs/                        # vision + setup guides
├── apps/
│   ├── api/       # NestJS 11; /health; empty db/auth/abilities modules; Vitest+swc
│   ├── sk-ops/    # Vite+React+TS; Tailwind v4 + shadcn; TanStack/Valibot/Zustand; "Web Admin"; Worker + wrangler + pool-workers test
│   ├── sk-hub/    # mirror of sk-ops; "Web HTX"
│   └── sk-go/     # Expo SDK 57 + TS; one empty screen; unconfigured drizzle-orm + expo-sqlite
└── packages/
    ├── config/       # @sankit/config: tsconfig / oxlint / tailwind / vitest bases
    ├── types/        # @sankit/types: export {}
    ├── form-schema/  # @sankit/form-schema: export {}
    └── rule-engine/  # @sankit/rule-engine: export {}
```

## Notes

- `node-linker=hoisted` làm yếu đi tính isolation của pnpm (có thể che giấu các phantom-dependency bug)
  nhưng lại cần thiết để Expo/Metro resolve được workspace dependency. Đây là trade-off đã chấp nhận cho
  giai đoạn bootstrap.
- `packages/config` (`@sankit/config`) cung cấp lớp base dùng chung gồm tsconfig / oxlint / Tailwind base
  layer / Vitest cho các workspace khác. **Không có `packages/ui` dùng chung** — mỗi web app tự sở hữu
  shadcn design system của riêng nó.
