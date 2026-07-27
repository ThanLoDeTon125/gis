# Sankit Monorepo

> 🇬🇧 English: [README.md](./README.md)

Repository này là bộ khung chạy được (runnable skeleton) cho **Sankit** — nền tảng GACP-compliance
và truy xuất nguồn gốc cho dược liệu Việt Nam. Nó chứa ba app cho ba nhóm người dùng, cộng thêm các
shared package. Repository là một scaffold rỗng, và các feature ticket sẽ xây trên nó: **chưa có
business logic, chưa có schema, và chưa wiring auth.**

> 🔒 **Proprietary & confidential.** Quyền truy cập giới hạn cho các thành viên được cấp quyền.
> Xem [LICENSE.md](./LICENSE.vi.md). Không chia sẻ source, config, hay quy trình setup.

## Documentation

| Doc                                                 | Mục đích                                                                               |
| --------------------------------------------------- | -------------------------------------------------------------------------------------- |
| [docs/PREREQUISITES.md](./docs/PREREQUISITES.vi.md) | Cài bộ toolchain cho dev (Ghostty, Fish, Fisher, nvm.fish, pnpm, OrbStack, LazyGit, …) |
| [docs/INSTALLATION.md](./docs/INSTALLATION.vi.md)   | Clone, setup, và chạy repository                                                       |
| [CONTRIBUTING.md](./CONTRIBUTING.vi.md)             | Quy trình làm việc — PR gắn với Linear ticket, các house rule                          |
| [docs/vision.md](./docs/vision.vi.md)               | Định hướng sản phẩm, phạm vi, và các quyết định kỹ thuật đã chốt                       |
| [LICENSE.md](./LICENSE.vi.md)                       | License proprietary & confidential                                                     |

**Nếu bạn mới vào, bắt đầu từ đây:** [PREREQUISITES](./docs/PREREQUISITES.vi.md) → [INSTALLATION](./docs/INSTALLATION.vi.md) → [CONTRIBUTING](./CONTRIBUTING.vi.md).

## Quick start

```sh
nvm use          # Node 24 (see .nvmrc)
pnpm install     # node-linker=hoisted — required for Expo
pnpm build && pnpm lint && pnpm test
```

Để xem quy trình setup đầy đủ, đọc [docs/INSTALLATION.md](./docs/INSTALLATION.vi.md).

## Repository commands

| Command             | Làm gì                                       |
| ------------------- | -------------------------------------------- |
| `pnpm build`        | `turbo run build` trên tất cả workspace      |
| `pnpm test`         | `turbo run test` → Vitest cho từng workspace |
| `pnpm lint`         | `oxlint` trên toàn repository                |
| `pnpm format`       | `oxfmt .` (ghi đè)                           |
| `pnpm format:check` | `oxfmt --check .`                            |

Chỉ dùng **oxlint và oxfmt** cho lint và format. Không dùng ESLint hay Prettier. Dùng **Vitest**
cho mọi test. Không dùng Jest. TypeScript được ghim ở **6.0.3**, nhánh stable hiện tại.
Repository chưa dùng native compiler của TS 7.

## Dev per app

| App                      | Command                               | Ghi chú                         |
| ------------------------ | ------------------------------------- | ------------------------------- |
| `sk-backend` (Hono)      | `pnpm --filter sk-backend dev`        | `GET /health` → 200             |
| `sk-ops` (Vite + React)  | `pnpm --filter sk-ops dev`            | route render ra **"Web Admin"** |
| `sk-coop` (Vite + React) | `pnpm --filter sk-coop dev`           | route render ra **"Web HTX"**   |
| `sk-go` (Expo)           | `pnpm --filter sk-go exec expo start` | một màn hình rỗng ("Sankit Go") |

Hai web app deploy dưới dạng **Cloudflare Workers với static-assets binding** (qua
`@cloudflare/vite-plugin`). Chúng **không** deploy dưới dạng Cloudflare Pages. Lựa chọn này có hai
lý do. Cloudflare hiện hướng các project mới sang Workers Static Assets. Ngoài ra, smoke test
`vitest-pool-workers` có thể chạy vào Worker entry thật của từng app.

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
│   ├── sk-backend/ # Hono on Cloudflare Workers; /health; OpenAPI 3.1 + Scalar docs
│   ├── sk-ops/    # Vite+React+TS; Tailwind v4 + shadcn; TanStack/Valibot/Zustand; "Web Admin"; Worker + wrangler + pool-workers test
│   ├── sk-coop/    # "Web HTX" — cooperative (HTX) portal
│   └── sk-go/     # Expo SDK 57 + TS; one empty screen; unconfigured drizzle-orm + expo-sqlite
└── packages/
    ├── config/       # @sankit/config: tsconfig / oxlint / tailwind / vitest bases
    ├── types/        # @sankit/types: export {}
    ├── form-schema/  # @sankit/form-schema: export {}
    └── rule-engine/  # @sankit/rule-engine: export {}
```

## Notes

- Setting `node-linker=hoisted` làm isolation của pnpm yếu đi, và điều này có thể che giấu các
  phantom-dependency bug. Nhưng Expo và Metro cần setting này để resolve workspace dependency.
  Trade-off này được chấp nhận cho giai đoạn bootstrap.
- `packages/config` (`@sankit/config`) cung cấp các base dùng chung cho tsconfig, oxlint, lớp
  Tailwind base, và Vitest. Các workspace khác dùng các base này. Repository **không có
  `packages/ui` dùng chung** — mỗi web app tự sở hữu shadcn design system của riêng nó.
