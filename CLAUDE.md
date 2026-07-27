# CLAUDE.md

Guidance for AI agents (Claude Code and others) that work in this repository.

## What this is

**Sankit** is a GACP-compliance and traceability platform for Vietnamese medicinal herbs. This
repository is a **pnpm + Turborepo monorepo**. It contains 3 apps for 3 actors, plus shared
packages. The repository is currently a **runnable bootstrap skeleton**. It has no business
logic, no data schemas, and no auth wiring. Each of those arrives with its own Linear ticket.
The product intent is in [docs/vision.md](./docs/vision.md).

## Layout

```
apps/
  sk-backend  Hono 4 on Cloudflare Workers · GET /health → 200 · OpenAPI 3.1 (hono-openapi + valibot) · Scalar docs at /docs · Vitest
  sk-ops   Vite+React+TS · "Web Admin" · Tailwind v4 + shadcn · TanStack/Valibot/Zustand · Cloudflare Worker
  sk-coop  Vite+React+TS · "Web HTX" · Tailwind v4 + shadcn · TanStack/Valibot/Zustand · Cloudflare Worker
  sk-go    Expo SDK 57 + TS · one screen · drizzle-orm + expo-sqlite installed (unconfigured)
packages/
  config       @sankit/config — shared tsconfig / oxlint / Tailwind base / Vitest base
  types        @sankit/types — export {}
  form-schema  @sankit/form-schema — export {}
  rule-engine  @sankit/rule-engine — export {}
```

## Commands

| Command                             | Does                                             |
| ----------------------------------- | ------------------------------------------------ |
| `pnpm install`                      | install (node-linker=hoisted, required for Expo) |
| `pnpm build`                        | `turbo run build`                                |
| `pnpm test`                         | `turbo run test` → Vitest per workspace          |
| `pnpm lint`                         | oxlint over the repository                       |
| `pnpm format` / `pnpm format:check` | oxfmt write / check                              |
| `pnpm --filter <app> dev`           | run one app                                      |

## Hard rules (do not violate)

- **Add dependencies with `pnpm add` / `pnpm add -D` only.** Do not write a dependency into
  `package.json` by hand.
- **Use oxlint + oxfmt only** — no ESLint, no Prettier. **Use Vitest** everywhere — no Jest.
- **Keep TypeScript pinned to 6.0.3** (the current stable line). Do not move to the TS7 native
  compiler yet. The repository tooling (wrangler, Vitest, Expo) is not validated on it.
  `baseUrl` is removed to stay clear of the TS 7 deprecations.
- **Do not create a shared `packages/ui`** — each web app owns its own shadcn design system.
- **The web apps are Cloudflare Workers with static-assets bindings** (through
  `@cloudflare/vite-plugin`), **not** Cloudflare Pages. Keep the Worker entry and the
  `wrangler.jsonc` of each app.
- `node-linker=hoisted` is intentional (Expo/Metro). Do not remove it.
- The root `package.json` uses the `packageManager` field, **not** `devEngines` (a pnpm 11.9.0
  bug).
- Bootstrap discipline: do not add business logic, schemas, or auth outside the ticket that owns
  them.

## Workflow

Each change goes through a pull request that is linked to a Linear ticket (`SANKIT-###`). Create
a branch from `main`. Do not commit to `main` directly. See
[CONTRIBUTING.md](./CONTRIBUTING.md). TDD is preferred (red → green → refactor). Before you say
that work is done, make sure that `pnpm build && pnpm lint && pnpm test` are green.

## Gotchas

- A workspace binary exits with code 126 after incremental installs. The cause: the hoisted
  linker strips the exec bit. Do a clean install: `rm -rf node_modules && pnpm install`.
- A Cloudflare Worker test fails with `ERR_FUTURE_COMPATIBILITY_DATE`. Make sure that the
  `compatibility_date` in `wrangler.jsonc` does not go past the bundled `workerd`.
