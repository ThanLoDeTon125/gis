# Sankit Monorepo — Bootstrap Vision

> This document is the source of truth for the task-loop. It comes from `BOOTSTRAP.md` and the
> shared understanding from the grilling session. It is **read-only** during the loop. It covers
> the bootstrap scope ONLY.

## Intent

Stand up a **runnable skeleton** for the Sankit monorepo (GitHub org `SANKIT-PRODUCT`). Sankit
is a GACP-compliance and traceability platform for Vietnamese medicinal herbs. It has 3 apps for
3 actors (Sankit Admin, Farm Manager/HTX, Field User). This task builds the empty scaffold that
will later hold those features. **It adds no business logic, no data schemas, and no auth
configuration** — those are separate tickets.

## Hard scope boundary (non-goals)

- NO business or feature code, NO domain models, NO GACP rules, NO auth wiring.
- NO unused libraries beyond the libraries in the explicit list.
- Dependencies that are pre-installed but not configured are intentional (Drizzle + expo-sqlite
  in sk-go). Install them only. Do not configure them.

## Locked stack (do not swap)

- **Monorepo:** pnpm + Turborepo + `pnpm-workspace.yaml`. TypeScript strict across the
  repository.
- **Lint/format:** `oxlint` + `oxfmt` (NOT ESLint/Prettier). oxfmt is pre-1.0. If it breaks on a
  file, flag that file. Do NOT fall back to Prettier silently.
- **Tests:** Vitest across the whole repository (no Jest).
- **Package manager:** pnpm 11.9 (`packageManager` field). Node 24 (`.nvmrc`).
- **Install all dependencies with the `pnpm add` CLI only** — do not write dependency blocks by
  hand.

### apps/sk-backend — Hono on Cloudflare Workers

TypeScript. `GET /health` → 200. The app serves an OpenAPI 3.1 specification at `/openapi.json`
(hono-openapi + Valibot) and the Scalar reference UI at `/docs`. No business routes yet.

### apps/sk-ops & apps/sk-coop — Vite + React + TS

Tailwind + shadcn/ui (initialized **per app** — each app owns its design system, NO shared
`packages/ui`). TanStack Query + TanStack Router + TanStack Form, Valibot, Zustand.

- sk-ops → one route that renders **"Web Admin"** (maps to Sankit Admin).
- sk-coop → one route that renders **"Web HTX"** (maps to Farm Manager).

### apps/sk-go — Expo (React Native) + TS

Install Drizzle + expo-sqlite (not used for now). One empty screen.

### packages/

- `types`, `form-schema`, `rule-engine` — empty (`export {}` placeholder). They can import each
  other.
- `config` — the shared tsconfig base, the oxlint configuration, the shared **base** Tailwind
  preset (each web app layers its own theme on top), and the shared Vitest configuration.

The internal package scope is `@sankit/*` (for example `@sankit/config`). Apps keep plain names.

## Locked decisions (from grilling)

1. **Root scaffold** — everything is at the repository root. There is NO nested `sankit/`
   directory.
2. **Local git only** — `git init`, split commits per app/package, **no remote and no push**.
3. **No shared UI package** — each web app owns its shadcn design system.
4. **Workers Static Assets, NOT Cloudflare Pages** — a deliberate, documented deviation from the
   "Pages" wording in BOOTSTRAP. Each web app uses `@cloudflare/vite-plugin` and deploys as a
   Worker with an `[assets]` binding (placeholder secrets in `wrangler.jsonc`). The
   `@cloudflare/vitest-pool-workers` smoke test targets the real Worker entry of each app — no
   throwaway extra Worker. Record the deviation in the README and in an ADR.
5. `oxlint` + `oxfmt`; Vitest everywhere; dependencies through the `pnpm add` CLI only.

## Deferred / placeholder (note, do not decide)

- The mobile offline-sync engine (PowerSync / ElectricSQL / DIY) is the largest open risk. It is
  not decided, and it is out of the bootstrap scope. sk-go stays bare Expo + unused
  Drizzle/sqlite.
- Storage (R2), the PDF dossier generator, and the real schemas/auth are all later tickets.

## Done means

- `pnpm install` + `pnpm build` + `pnpm lint` + `pnpm test` pass across the repository.
- sk-backend `GET /health` returns 200.
- sk-ops + sk-coop open to a blank page ("Web Admin" / "Web HTX").
- sk-go Expo runs.
- The Cloudflare Workers smoke test passes.
- A short root README (how to run dev for each app + the directory structure) + an ADR for the
  Pages→Workers deviation.
- Split commits per app/package (local).
