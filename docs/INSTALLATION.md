# Installation

Set up the Sankit monorepo locally. Assumes you finished [PREREQUISITES.md](./PREREQUISITES.md)
(Node 24, pnpm 11.9.0, `gh` authenticated).

---

## 1. Clone

```sh
gh repo clone SANKIT-PRODUCT/sankitmono
cd sankitmono
```

## 2. Select Node 24

The repo pins Node via `.nvmrc`:

```fish
nvm use          # reads .nvmrc → Node 24
```

## 3. Install dependencies

```sh
pnpm install
```

> `node-linker=hoisted` is set repo-wide (`.npmrc` + `pnpm-workspace.yaml`) — **required** for
> Expo/Metro to resolve workspace deps. Do not remove it.

## 4. Verify the workspace is green

```sh
pnpm build      # turbo run build — all workspaces
pnpm lint       # oxlint over the repo
pnpm test       # turbo run test — Vitest per workspace
```

All three should exit `0`. `pnpm test` includes the api `GET /health` → 200 check and the
web apps' render + Cloudflare Worker smoke tests.

---

## Run an app in dev

| App | Command | Opens |
| --- | --- | --- |
| `api` (NestJS) | `pnpm --filter api start:dev` | `http://localhost:3000/health` → `{ "status": "ok" }` |
| `sk-ops` (Web Admin) | `pnpm --filter sk-ops dev` | Vite dev server → **"Web Admin"** |
| `sk-hub` (Web HTX) | `pnpm --filter sk-hub dev` | Vite dev server → **"Web HTX"** |
| `sk-go` (Expo) | `pnpm --filter sk-go exec expo start` | Expo dev server (press `i` / `a` / scan QR) |

---

## Formatting

Lint/format is **oxlint + oxfmt only** (no ESLint/Prettier):

```sh
pnpm format        # oxfmt . (writes)
pnpm format:check  # oxfmt --check . (CI / pre-PR)
```

---

## Troubleshooting

| Symptom | Fix |
| --- | --- |
| `nest: Permission denied` (exit 126) after incremental `pnpm add/remove` | The hoisted linker can strip the exec bit on `@nestjs/cli/bin/nest.js`. Run a clean install: `rm -rf node_modules && pnpm install`. |
| Expo: "Unable to resolve module" / duplicate React | Ensure `node-linker=hoisted` is intact and `apps/sk-go/metro.config.js` is present; re-run `pnpm install`. |
| `pnpm` command crashes with `Cannot use 'in' operator ... 'integrity'` | The root `package.json` must use the `packageManager` string, **not** `devEngines` (a pnpm 11.9.0 bug). Don't reintroduce `devEngines`. |
| Cloudflare Worker test: `ERR_FUTURE_COMPATIBILITY_DATE` | `wrangler.jsonc` `compatibility_date` must not be in the future relative to the bundled `workerd`. Lower it or bump `workerd`. |
| `pnpm` version mismatch | `corepack prepare pnpm@11.9.0 --activate`. |

---

Next: read [CONTRIBUTING.md](../CONTRIBUTING.md) before making changes.
