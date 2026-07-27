# Contributing

This document tells each Sankit developer how to work. Read this document before you change the
repository.

> This repository is **proprietary and confidential** — see [LICENSE.md](./LICENSE.md). Do not
> share the source, the configuration, or the setup procedures outside the Company.

---

## 0. One-time setup

1. Install the toolchain → [docs/PREREQUISITES.md](./docs/PREREQUISITES.md)
2. Set up the repository → [docs/INSTALLATION.md](./docs/INSTALLATION.md)

Before you start, make sure that `pnpm build`, `pnpm lint`, and `pnpm test` are green.

---

## 1. Every change goes through a Pull Request

**Do not commit directly to `main`.** The `main` branch is protected and always releasable. All
work goes to `main` through a pull request and a review.

### The loop

1. **Start from a Linear ticket.** Each change has a Linear issue (for example `SANKIT-123`). If
   there is no ticket, do not open a pull request.
2. **Create a branch from `main`.** Put the ticket ID in the branch name:
   ```sh
   git switch main && git pull
   git switch -c SANKIT-123-short-description
   ```
3. **Commit** in small logical steps. Use **Conventional Commits** (see §2).
4. **Open a pull request** into `main`:
   - Title: `SANKIT-123: <what changed>` (the ticket ID lets Linear link the pull request
     automatically).
   - Description: tell what changed and why. Tell how you tested. Add screenshots for UI changes.
   - Link the Linear ticket. Paste the URL, or use the Linear ↔ GitHub integration.
5. **Pass all the gates** (§3). CI must be green. The pull request must have at least **one
   approving review**.
6. **Merge**, then delete the branch.

> 🔴 **SQUASH MERGE ONLY.** Each pull request lands on `main` as **one squashed commit**. Do not
> use a merge commit. Do not use rebase-and-merge. Do not push multiple raw commits. This rule
> keeps one clean commit for each ticket in the history of `main`. Use the squash commit title
> `SANKIT-123: <what changed>`.

> Tip: put the ticket ID in the branch name **and** in the pull request title. Then Linear links
> both automatically.

### Git concepts to know

This workflow uses some Git features. If a feature is new to you, read the related page below
first. These pages are short and practical — you do not have to read the full man pages.

- **Branching** — [Atlassian: Using branches](https://www.atlassian.com/git/tutorials/using-branches)
- **Squash** — [Tower: Squash commits](https://www.git-tower.com/learn/git/faq/git-squash) (each pull request lands with this method — see §1)
- **Cherry-pick** — [Atlassian: git cherry-pick](https://www.atlassian.com/git/tutorials/cherry-pick) (move one commit between branches, for example a hotfix)
- **Worktree** — [DataCamp: Git worktree](https://www.datacamp.com/tutorial/git-worktree-tutorial) (work on two or more branches at the same time, with no stash or switch)

---

## 2. Conventional Commits

```
<type>(<scope>): <subject>
```

Types: `feat`, `fix`, `chore`, `docs`, `refactor`, `test`, `style`, `perf`, `ci`.
The scope is the app or package name (`sk-backend`, `sk-ops`, `sk-coop`, `sk-go`, `config`,
`types`, …).

Examples:

- `feat(sk-backend): add tenant guard to health module`
- `fix(sk-ops): correct TanStack Router param typing`
- `chore(config): bump oxlint base rules`

---

## 3. Definition of Done (all items must pass before you request a review)

- [ ] `pnpm build` — green
- [ ] `pnpm lint` — green (**oxlint + oxfmt only**; no ESLint/Prettier)
- [ ] `pnpm format:check` — clean
- [ ] `pnpm test` — green (Vitest; no Jest)
- [ ] New behavior has tests (TDD preferred — red → green → refactor)
- [ ] The pull request is linked to its Linear ticket
- [ ] No secrets, no `.env` values, and no proprietary data in the commits

---

## 4. House rules

- **Add dependencies with the CLI only** — `pnpm add` / `pnpm add -D`. Do not write a dependency
  into `package.json` manually.
- **Install into the correct workspace:** `pnpm add <pkg> --filter <app>` (or `-w` for the root).
- **Keep TypeScript on 6.0.3** — do not move to the TS 7 native compiler yet. The repository
  tooling (wrangler, Vitest, Expo) is not validated against tsgo.
- **Do not create a shared `packages/ui`** — each web app owns its shadcn design system. Put
  shared logic in `@sankit/{types,form-schema,rule-engine}`. Put shared configuration in
  `@sankit/config`.
- **Web apps deploy as Cloudflare Workers with static assets** (not Pages). Keep the Worker entry
  and the `wrangler.jsonc` of each app intact.
- **Keep `main` releasable.** If a change has risk, put it behind a flag, or keep the pull request
  small.
- **Do not commit generated output** (`dist`, `.turbo`, `node_modules`, Expo `dist`). These paths
  are already in `.gitignore`.
- **Bootstrap discipline:** do not add business logic, schemas, or auth wiring outside the ticket
  that owns them.

---

## 5. Get help

If you are blocked, comment on the Linear ticket, or send a message with the ticket ID in the
team channel. Do not break a house rule to work around a blocker.
