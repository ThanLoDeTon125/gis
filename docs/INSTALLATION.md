# Installation

This document tells you how to set up the Sankit monorepo on your computer. Complete
[PREREQUISITES.md](./PREREQUISITES.md) first (Node 24, pnpm 11.9.0, `gh` authenticated).

---

## 1. Clone the repository

```sh
gh repo clone SANKIT-PRODUCT/sankitmono
cd sankitmono
```

## 2. Select Node 24

The repository sets the Node version in `.nvmrc`:

```fish
nvm use          # reads .nvmrc → Node 24
```

## 3. Install the dependencies

```sh
pnpm install
```

> The repository sets `node-linker=hoisted` in `.npmrc` and `pnpm-workspace.yaml`. Expo/Metro
> **requires** this setting to resolve workspace dependencies. Do not remove it.

## 4. Make sure that the workspace is green

```sh
pnpm build      # turbo run build — all workspaces
pnpm lint       # oxlint over the repo
pnpm test       # turbo run test — Vitest per workspace
```

Make sure that each command exits with code `0`. The `pnpm test` command includes the sk-backend
`GET /health` → 200 check. It also includes the render tests and the Cloudflare Worker smoke tests
of the web applications.

---

## Start an application in development mode

| App                  | Command                               | Result                                                |
| -------------------- | ------------------------------------- | ----------------------------------------------------- |
| `sk-backend` (Hono)  | `pnpm --filter sk-backend dev`        | `http://localhost:8787/health` → `{ "status": "ok" }` |
| `sk-ops` (Web Admin) | `pnpm --filter sk-ops dev`            | Vite dev server → **"Web Admin"**                     |
| `sk-coop` (Web HTX)  | `pnpm --filter sk-coop dev`           | Vite dev server → **"Web HTX"**                       |
| `sk-go` (Expo)       | `pnpm --filter sk-go exec expo start` | Expo dev server (press `i` / `a`, or scan the QR)     |

---

## Format the code

Use **oxlint + oxfmt only** for lint and format. Do not use ESLint or Prettier.

```sh
pnpm format        # oxfmt . (writes)
pnpm format:check  # oxfmt --check . (CI / pre-PR)
```

---

## Troubleshooting

| Symptom                                                                         | Fix                                                                                                                                    |
| ------------------------------------------------------------------------------- | -------------------------------------------------------------------------------------------------------------------------------------- |
| A workspace binary shows `Permission denied` (exit 126) after `pnpm add/remove` | The hoisted linker can remove the exec bit from workspace binaries. Do a clean install: `rm -rf node_modules && pnpm install`.         |
| Expo shows "Unable to resolve module" or a duplicate React                      | Make sure that `node-linker=hoisted` is not changed and that `apps/sk-go/metro.config.js` is present. Then do `pnpm install` again.    |
| `pnpm` stops with `Cannot use 'in' operator ... 'integrity'`                    | The root `package.json` must use the `packageManager` string, **not** `devEngines` (a pnpm 11.9.0 bug). Do not add `devEngines` again. |
| A Cloudflare Worker test shows `ERR_FUTURE_COMPATIBILITY_DATE`                  | The `compatibility_date` in `wrangler.jsonc` must not be later than the included `workerd`. Decrease the date, or update `workerd`.    |
| `pnpm` has an incorrect version                                                 | Do `corepack prepare pnpm@11.9.0 --activate`.                                                                                          |

---

Read [CONTRIBUTING.md](../CONTRIBUTING.md) before you make changes.
