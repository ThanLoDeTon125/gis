# Sankit Monorepo

> 🇻🇳 Tiếng Việt: [README.vi.md](./README.vi.md)

This repository is the runnable skeleton for **Sankit** — a GACP-compliance and traceability
platform for Vietnamese medicinal herbs. It contains three apps for three actors, plus shared
packages. The repository is an empty scaffold, and feature tickets build on it: **it has no
business logic, no schemas, and no auth wiring yet.**

> 🔒 **Proprietary & confidential.** Access is limited to authorized team members. See
> [LICENSE.md](./LICENSE.md). Do not share the source, the configuration, or the setup procedures.

## Documentation

| Doc                                              | Purpose                                                                                       |
| ------------------------------------------------ | --------------------------------------------------------------------------------------------- |
| [docs/PREREQUISITES.md](./docs/PREREQUISITES.md) | Install the developer toolchain (Ghostty, Fish, Fisher, nvm.fish, pnpm, OrbStack, LazyGit, …) |
| [docs/INSTALLATION.md](./docs/INSTALLATION.md)   | Clone, set up, and run the repository                                                         |
| [CONTRIBUTING.md](./CONTRIBUTING.md)             | Work process — PRs linked to Linear tickets, house rules                                      |
| [docs/vision.md](./docs/vision.md)               | Product intent, scope, and locked technical decisions                                         |
| [LICENSE.md](./LICENSE.md)                       | Proprietary & confidential license                                                            |

**If you are new, start here:** [PREREQUISITES](./docs/PREREQUISITES.md) → [INSTALLATION](./docs/INSTALLATION.md) → [CONTRIBUTING](./CONTRIBUTING.md).

## Quick start

```sh
nvm use          # Node 24 (see .nvmrc)
pnpm install     # node-linker=hoisted — required for Expo
pnpm build && pnpm lint && pnpm test
```

For the full setup procedure, see [docs/INSTALLATION.md](./docs/INSTALLATION.md).

## Repository commands

| Command             | What it does                            |
| ------------------- | --------------------------------------- |
| `pnpm build`        | `turbo run build` across all workspaces |
| `pnpm test`         | `turbo run test` → Vitest per workspace |
| `pnpm lint`         | `oxlint` over the repository            |
| `pnpm format`       | `oxfmt .` (writes)                      |
| `pnpm format:check` | `oxfmt --check .`                       |

Use **oxlint and oxfmt only** for lint and format. Do not use ESLint or Prettier. Use **Vitest**
for all tests. Do not use Jest. TypeScript is pinned to **6.0.3**, the current stable line. The
repository does not use the TS 7 native compiler yet.

## Dev per app

| App                      | Command                               | Notes                          |
| ------------------------ | ------------------------------------- | ------------------------------ |
| `sk-backend` (Hono)      | `pnpm --filter sk-backend dev`        | `GET /health` → 200            |
| `sk-ops` (Vite + React)  | `pnpm --filter sk-ops dev`            | route renders **"Web Admin"**  |
| `sk-coop` (Vite + React) | `pnpm --filter sk-coop dev`           | route renders **"Web HTX"**    |
| `sk-go` (Expo)           | `pnpm --filter sk-go exec expo start` | one empty screen ("Sankit Go") |

The two web apps deploy as **Cloudflare Workers with a static-assets binding** (through
`@cloudflare/vite-plugin`). They do **not** deploy as Cloudflare Pages. This choice has two
reasons. Cloudflare now sends new projects to Workers Static Assets. Also, the
`vitest-pool-workers` smoke test can reach the real Worker entry of each app.

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

- The `node-linker=hoisted` setting makes the isolation of pnpm weaker, and this can hide
  phantom-dependency bugs. But Expo and Metro need this setting to resolve workspace dependencies.
  This trade-off is accepted for the bootstrap phase.
- `packages/config` (`@sankit/config`) supplies the shared bases for tsconfig, oxlint, the
  Tailwind base layer, and Vitest. The other workspaces use these bases. The repository has **no
  shared `packages/ui`** — each web app owns its own shadcn design system.
