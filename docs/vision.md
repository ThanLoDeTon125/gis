# Sankit Monorepo — Bootstrap Vision

> Source of truth for the task-loop. Derived from `BOOTSTRAP.md` + the grilling-session
> shared understanding. **Read-only** during the loop. Bootstrap scope ONLY.

## Intent

Stand up a **runnable skeleton** for the Sankit monorepo (GitHub org `SANKIT-PRODUCT`).
Sankit is a GACP-compliance / traceability platform for Vietnamese medicinal herbs —
3 apps for 3 actors (Sankit Admin, Farm Manager/HTX, Field User). This task builds the
empty scaffold those features will later live in. **No business logic, no data schemas,
no auth configuration** — those are separate tickets.

## Hard scope boundary (non-goals)

- NO business/feature code, NO domain models, NO GACP rules, NO auth wiring.
- NO unused libraries beyond those explicitly listed.
- Pre-installed-but-unconfigured deps are intentional (Drizzle, Better Auth, CASL in api;
  Drizzle + expo-sqlite in sk-go). Install only; do not configure.

## Locked stack (do not swap)

- **Monorepo:** pnpm + Turborepo + `pnpm-workspace.yaml`. TypeScript strict repo-wide.
- **Lint/format:** `oxlint` + `oxfmt` (NOT ESLint/Prettier). oxfmt is pre-1.0 — if it
  breaks on a file, flag it; do NOT silently fall back to Prettier.
- **Tests:** Vitest across the whole repo (swap out Nest's default Jest).
- **Package manager:** pnpm 11.9 (`packageManager` field). Node 24 (`.nvmrc`).
- **All deps installed via `pnpm add` CLI only** — never hand-write dependency blocks.

### apps/api — NestJS
TypeScript. `GET /health` → 200. Empty modules only. Pre-install (do NOT configure):
`drizzle-orm` + `node-postgres` (pg), Better Auth, CASL. Vitest instead of Jest.

### apps/sk-ops & apps/sk-hub — Vite + React + TS
Tailwind + shadcn/ui (initialized **per app** — each app owns its design system, NO shared
`packages/ui`). TanStack Query + TanStack Router + TanStack Form, Valibot, Zustand.
- sk-ops → one route rendering **"Web Admin"** (maps to Sankit Admin).
- sk-hub → one route rendering **"Web HTX"** (maps to Farm Manager).

### apps/sk-go — Expo (React Native) + TS
Install Drizzle + expo-sqlite (unused for now). One empty screen.

### packages/
- `types`, `form-schema`, `rule-engine` — empty (`export {}` placeholder), cross-importable.
- `config` — shared tsconfig base, oxlint config, shared **base** Tailwind preset
  (each web app layers its own theme on top), shared Vitest config.

Internal package scope: `@sankit/*` (e.g. `@sankit/config`). Apps keep plain names.

## Locked decisions (from grilling)

1. **Root scaffold** — everything at repo root, NO nested `sankit/` dir.
2. **Local git only** — `git init`, split commits per app/package, **no remote / no push**.
3. **No shared UI package** — each web app owns its shadcn design system.
4. **Workers Static Assets, NOT Cloudflare Pages** — deliberate documented deviation from
   BOOTSTRAP's "Pages" wording. Each web app uses `@cloudflare/vite-plugin` and deploys as
   a Worker with an `[assets]` binding (placeholder secrets in `wrangler.jsonc`). The
   `@cloudflare/vitest-pool-workers` smoke test targets each app's real Worker entry — no
   throwaway extra Worker. Record deviation in README + an ADR.
5. `oxlint` + `oxfmt`; Vitest everywhere; deps via `pnpm add` CLI only.

## Deferred / placeholder (note, do not decide)

- Mobile offline-sync engine (PowerSync / ElectricSQL / DIY) — biggest open risk, undecided.
  Out of bootstrap scope. sk-go stays bare Expo + unused Drizzle/sqlite.
- Storage (R2), PDF dossier generator, real schemas/auth — all later tickets.

## Done means

- `pnpm install` + `pnpm build` + `pnpm lint` + `pnpm test` pass across the repo.
- api `GET /health` returns 200.
- sk-ops + sk-hub open to a blank page ("Web Admin" / "Web HTX").
- sk-go Expo runs.
- Cloudflare Workers smoke test passes.
- Short root README (how to run dev per app + directory structure) + ADR for the
  Pages→Workers deviation.
- Split commits per app/package (local).
