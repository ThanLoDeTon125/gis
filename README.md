# Sankit Monorepo

> 🇻🇳 Tiếng Việt: [README.vi.md](./README.vi.md)

Runnable skeleton for **Sankit** — a GACP-compliance / traceability platform for Vietnamese
medicinal herbs. Three apps for three actors plus shared packages. This repo is the empty
scaffold that feature tickets build on: **no business logic, no schemas, no auth wiring yet.**

> 🔒 **Proprietary & confidential.** Access is limited to authorized team members — see
> [LICENSE.md](./LICENSE.md). Do not share source, configuration, or setup.

## Documentation

| Doc | Purpose |
| --- | --- |
| [docs/PREREQUISITES.md](./docs/PREREQUISITES.md) | Install the developer toolchain (Ghostty, Fish, Fisher, nvm.fish, pnpm, OrbStack, LazyGit, …) |
| [docs/INSTALLATION.md](./docs/INSTALLATION.md) | Clone + set up + run the repo |
| [CONTRIBUTING.md](./CONTRIBUTING.md) | Working process — PRs linked to Linear tickets, house rules |
| [docs/vision.md](./docs/vision.md) | Product intent, scope, and locked technical decisions |
| [LICENSE.md](./LICENSE.md) | Proprietary & confidential license |

**New here?** Start with [PREREQUISITES](./docs/PREREQUISITES.md) → [INSTALLATION](./docs/INSTALLATION.md) → [CONTRIBUTING](./CONTRIBUTING.md).

## Quick start

```sh
nvm use          # Node 24 (see .nvmrc)
pnpm install     # node-linker=hoisted — required for Expo
pnpm build && pnpm lint && pnpm test
```

Full setup: [docs/INSTALLATION.md](./docs/INSTALLATION.md).

## Repo-wide commands

| Command | What it does |
| --- | --- |
| `pnpm build` | `turbo run build` across all workspaces |
| `pnpm test` | `turbo run test` → Vitest per workspace |
| `pnpm lint` | `oxlint` over the repo |
| `pnpm format` | `oxfmt .` (writes) |
| `pnpm format:check` | `oxfmt --check .` |

Lint/format is **oxlint + oxfmt only** (no ESLint/Prettier). Tests are **Vitest** everywhere
(no Jest). TypeScript is pinned to **6.0.3** (the current stable line; TS 7 native compiler is not adopted yet).

## Dev per app

| App | Command | Notes |
| --- | --- | --- |
| `api` (NestJS) | `pnpm --filter api start:dev` | `GET /health` → 200 |
| `sk-ops` (Vite + React) | `pnpm --filter sk-ops dev` | route renders **"Web Admin"** |
| `sk-hub` (Vite + React) | `pnpm --filter sk-hub dev` | route renders **"Web HTX"** |
| `sk-go` (Expo) | `pnpm --filter sk-go exec expo start` | one empty screen ("Sankit Go") |

The two web apps deploy as **Cloudflare Workers with a static-assets binding** (via
`@cloudflare/vite-plugin`), **not** Cloudflare Pages — chosen because Cloudflare now steers new
projects to Workers Static Assets and it lets the `vitest-pool-workers` smoke test hit each app's
real Worker entry.

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

- `node-linker=hoisted` weakens pnpm's isolation (can mask phantom-dependency bugs) but is required
  for Expo/Metro to resolve workspace dependencies. Accepted trade-off for the bootstrap.
- `packages/config` (`@sankit/config`) ships the shared tsconfig / oxlint / Tailwind base layer /
  Vitest base consumed by the other workspaces. There is **no shared `packages/ui`** — each web app
  owns its own shadcn design system.
