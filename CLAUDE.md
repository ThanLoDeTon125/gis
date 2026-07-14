# CLAUDE.md

Guidance for AI agents (Claude Code et al.) working in this repository.

## What this is

**Sankit** — a GACP-compliance / traceability platform for Vietnamese medicinal herbs. This repo
is a **pnpm + Turborepo monorepo**: 3 apps for 3 actors + shared packages. It is currently a
**runnable bootstrap skeleton** — no business logic, schemas, or auth wiring yet; those arrive per
Linear ticket. Product intent lives in [docs/vision.md](./docs/vision.md).

## Layout

```
apps/
  api      NestJS 11 · GET /health → 200 · empty db/auth/abilities modules · Vitest+swc
  sk-ops   Vite+React+TS · "Web Admin" · Tailwind v4 + shadcn · TanStack/Valibot/Zustand · Cloudflare Worker
  sk-hub   mirror of sk-ops · "Web HTX"
  sk-go    Expo SDK 57 + TS · one screen · drizzle-orm + expo-sqlite installed (unconfigured)
packages/
  config       @sankit/config — shared tsconfig / oxlint / Tailwind base / Vitest base
  types        @sankit/types — export {}
  form-schema  @sankit/form-schema — export {}
  rule-engine  @sankit/rule-engine — export {}
```

## Commands

| Command | Does |
| --- | --- |
| `pnpm install` | install (node-linker=hoisted, required for Expo) |
| `pnpm build` | `turbo run build` |
| `pnpm test` | `turbo run test` → Vitest per workspace |
| `pnpm lint` | oxlint over the repo |
| `pnpm format` / `pnpm format:check` | oxfmt write / check |
| `pnpm --filter <app> dev` (or `start:dev` for api) | run one app |

## Hard rules (do not violate)

- **Dependencies via `pnpm add` / `pnpm add -D` only.** Never hand-write a dependency into
  `package.json`.
- **oxlint + oxfmt only** — no ESLint, no Prettier. **Vitest** everywhere — no Jest.
- **TypeScript pinned to 6.0.3** (current stable line) — do not move to the TS7 native compiler yet
  (Nest decorator metadata + tooling not validated on it). `baseUrl` is dropped and api uses
  `nodenext` module/resolution to stay clear of TS 7 deprecations.
- **No shared `packages/ui`** — each web app owns its shadcn design system.
- **Web apps are Cloudflare Workers with static-assets bindings** (via `@cloudflare/vite-plugin`),
  **not** Cloudflare Pages. Keep each app's Worker entry + `wrangler.jsonc`.
- `node-linker=hoisted` is intentional (Expo/Metro). Don't remove it.
- Root `package.json` uses the `packageManager` field, **not** `devEngines` (pnpm 11.9.0 bug).
- Bootstrap discipline: no business logic / schemas / auth outside the owning ticket.

## Workflow

All changes go through a PR linked to a Linear ticket (`SANKIT-###`). Branch off `main`, never
commit to `main` directly. See [CONTRIBUTING.md](./CONTRIBUTING.md). Prefer TDD (red → green →
refactor). Before claiming done: `pnpm build && pnpm lint && pnpm test` green.

## Gotchas

- `nest` exit 126 after incremental installs → clean `rm -rf node_modules && pnpm install`.
- Cloudflare Worker test `ERR_FUTURE_COMPATIBILITY_DATE` → `wrangler.jsonc compatibility_date`
  must not exceed the bundled `workerd`.
