# Contributing

How every Sankit developer works. Read this before touching the codebase.

> This repository is **proprietary and confidential** — see [LICENSE.md](./LICENSE.md). Do not
> share source, configuration, or setup outside the Company.

---

## 0. One-time setup

1. Install the toolchain → [docs/PREREQUISITES.md](./docs/PREREQUISITES.md)
2. Set up the repo → [docs/INSTALLATION.md](./docs/INSTALLATION.md)

Confirm `pnpm build`, `pnpm lint`, `pnpm test` are all green before you start.

---

## 1. Every change goes through a Pull Request

**No direct commits to `main`.** `main` is protected and always releasable. All work lands via PR
and review.

### The loop

1. **Start from a Linear ticket.** Every change has a Linear issue (e.g. `SANKIT-123`). No ticket,
   no PR.
2. **Branch off `main`**, named with the ticket ID:
   ```sh
   git switch main && git pull
   git switch -c SANKIT-123-short-description
   ```
3. **Commit** in small, logical steps using **Conventional Commits** (see §2).
4. **Open a PR** back into `main`:
   - Title: `SANKIT-123: <what changed>` (the ticket ID lets Linear auto-link the PR).
   - Description: what + why, how you tested, screenshots for UI.
   - Link the Linear ticket (paste the URL / use the Linear ↔ GitHub integration).
5. **Pass all gates** (§3) — CI green, at least **one approving review**.
6. **Merge**, then delete the branch.

> 🔴 **SQUASH MERGE ONLY.** Every PR lands on `main` as a **single squashed commit** — never a
> merge commit, never rebase-and-merge, never a raw multi-commit push. This keeps `main`'s history
> one-clean-commit-per-ticket. Use the squash commit title `SANKIT-123: <what changed>`.

> Tip: put the ticket ID in the branch name **and** the PR title so Linear links both
> automatically.

### Git concepts worth knowing

This workflow leans on a few Git features. If any are unfamiliar, read these first (skip the
full man pages — these are the short, practical versions):

- **Branching** — [Atlassian: Using branches](https://www.atlassian.com/git/tutorials/using-branches)
- **Squash** — [Tower: Squash commits](https://www.git-tower.com/learn/git/faq/git-squash) (this is how every PR lands — see §1)
- **Cherry-pick** — [Atlassian: git cherry-pick](https://www.atlassian.com/git/tutorials/cherry-pick) (move a single commit between branches, e.g. a hotfix)
- **Worktree** — [DataCamp: Git worktree](https://www.datacamp.com/tutorial/git-worktree-tutorial) (work on multiple branches at once without stashing/switching)

---

## 2. Conventional Commits

```
<type>(<scope>): <subject>
```

Types: `feat`, `fix`, `chore`, `docs`, `refactor`, `test`, `style`, `perf`, `ci`.
Scope = app/package (`api`, `sk-ops`, `sk-hub`, `sk-go`, `config`, `types`, …).

Examples:
- `feat(api): add tenant guard to health module`
- `fix(sk-ops): correct TanStack Router param typing`
- `chore(config): bump oxlint base rules`

---

## 3. Definition of Done (must pass before requesting review)

- [ ] `pnpm build` — green
- [ ] `pnpm lint` — green (**oxlint + oxfmt only**; no ESLint/Prettier)
- [ ] `pnpm format:check` — clean
- [ ] `pnpm test` — green (Vitest; no Jest)
- [ ] New behavior has tests (TDD preferred — red → green → refactor)
- [ ] PR linked to its Linear ticket
- [ ] No secrets, no `.env` values, no proprietary data committed

---

## 4. House rules

- **Dependencies are added via the CLI only** — `pnpm add` / `pnpm add -D`. Never hand-write a
  dependency into `package.json`.
- **Install into the right workspace:** `pnpm add <pkg> --filter <app>` (or `-w` for the root).
- **TypeScript stays on 6.0.3** — do not bump to the TS 7 native compiler yet: `nest build` needs
  the programmatic compiler API that tsgo doesn't ship until TS 7.1 (the rest of the repo is
  TS7-clean; api is the blocker).
- **No shared `packages/ui`** — each web app owns its shadcn design system. Put truly shared logic
  in `@sankit/{types,form-schema,rule-engine}` or shared config in `@sankit/config`.
- **Web apps deploy as Cloudflare Workers with static assets** (not Pages). Keep each app's real
  Worker entry + `wrangler.jsonc` intact.
- **Keep `main` releasable.** If a change is risky, gate it behind a flag or keep the PR small.
- **Don't commit generated output** (`dist`, `.turbo`, `node_modules`, Expo `dist`) — already in
  `.gitignore`.
- **Bootstrap discipline:** no business logic / schemas / auth wiring outside the ticket that owns
  it.

---

## 5. Getting help

Blocked? Comment on the Linear ticket or flag it in the team channel with the ticket ID. Don't
work around a blocker by breaking a house rule.
