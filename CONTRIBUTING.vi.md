# Contributing

Cách mọi developer của Sankit làm việc. Đọc cái này trước khi động vào codebase.

> Repo này là **proprietary and confidential** — xem [LICENSE.md](./LICENSE.vi.md). Không chia sẻ
> source, config hay quy trình setup ra ngoài Company.

---

## 0. Setup một lần

1. Cài toolchain → [docs/PREREQUISITES.md](./docs/PREREQUISITES.vi.md)
2. Set up repo → [docs/INSTALLATION.md](./docs/INSTALLATION.vi.md)

Xác nhận `pnpm build`, `pnpm lint`, `pnpm test` đều xanh trước khi bắt đầu.

---

## 1. Mọi thay đổi đều đi qua Pull Request

**Không commit thẳng vào `main`.** `main` được bảo vệ và luôn ở trạng thái release được. Mọi công việc
đều vào qua PR và review.

### The loop

1. **Bắt đầu từ một Linear ticket.** Mỗi thay đổi đều gắn với một Linear issue (ví dụ `SANKIT-123`).
   Không ticket, không PR.
2. **Nhánh ra từ `main`**, đặt tên theo ticket ID:
   ```sh
   git switch main && git pull
   git switch -c SANKIT-123-short-description
   ```
3. **Commit** theo từng bước nhỏ, logic, dùng **Conventional Commits** (xem §2).
4. **Mở PR** trở lại vào `main`:
   - Title: `SANKIT-123: <what changed>` (ticket ID giúp Linear tự động link PR).
   - Description: cái gì + tại sao, đã test thế nào, kèm screenshot nếu là UI.
   - Link Linear ticket (dán URL / dùng integration Linear ↔ GitHub).
5. **Qua hết các gate** (§3) — CI xanh, và ít nhất **một review approve**.
6. **Merge**, rồi xoá nhánh.

> 🔴 **CHỈ DÙNG SQUASH MERGE.** Mỗi PR khi lên `main` là **một commit squash duy nhất** — không
> merge commit, không rebase-and-merge, không push thẳng nhiều commit. Nhờ vậy history của `main`
> giữ đúng một commit sạch cho mỗi ticket. Đặt title commit squash là `SANKIT-123: <what changed>`.

> Mẹo: để ticket ID **cả** trong tên nhánh **lẫn** title PR để Linear tự link cả hai.

### Các concept Git nên biết

Workflow này dựa vào vài feature của Git. Cái nào chưa quen thì đọc mấy bài dưới trước (khỏi cần
cày hết man page — đây là bản ngắn, thực dụng):

- **Branching** — [Atlassian: Using branches](https://www.atlassian.com/git/tutorials/using-branches)
- **Squash** — [Tower: Squash commits](https://www.git-tower.com/learn/git/faq/git-squash) (đây là cách mọi PR lên `main` — xem §1)
- **Cherry-pick** — [Atlassian: git cherry-pick](https://www.atlassian.com/git/tutorials/cherry-pick) (bê một commit lẻ giữa các branch, ví dụ hotfix)
- **Worktree** — [DataCamp: Git worktree](https://www.datacamp.com/tutorial/git-worktree-tutorial) (làm nhiều branch cùng lúc, khỏi stash/switch qua lại)

---

## 2. Conventional Commits

```
<type>(<scope>): <subject>
```

Types: `feat`, `fix`, `chore`, `docs`, `refactor`, `test`, `style`, `perf`, `ci`.
Scope = app/package (`api`, `sk-ops`, `sk-hub`, `sk-go`, `config`, `types`, …).

Ví dụ:
- `feat(api): add tenant guard to health module`
- `fix(sk-ops): correct TanStack Router param typing`
- `chore(config): bump oxlint base rules`

---

## 3. Definition of Done (phải pass trước khi request review)

- [ ] `pnpm build` — xanh
- [ ] `pnpm lint` — xanh (**chỉ oxlint + oxfmt**; không ESLint/Prettier)
- [ ] `pnpm format:check` — sạch
- [ ] `pnpm test` — xanh (Vitest; không Jest)
- [ ] Hành vi mới phải có test (ưu tiên TDD — red → green → refactor)
- [ ] PR đã link với Linear ticket của nó
- [ ] Không commit secret, không giá trị `.env`, không dữ liệu proprietary

---

## 4. House rules

- **Chỉ thêm dependency qua CLI** — `pnpm add` / `pnpm add -D`. Không bao giờ tự tay ghi dependency vào
  `package.json`.
- **Cài vào đúng workspace:** `pnpm add <pkg> --filter <app>` (hoặc `-w` cho root).
- **TypeScript giữ ở 6.0.3** — chưa bump lên native compiler TS 7: `nest build` cần programmatic
  compiler API mà tsgo chưa ship tới TS 7.1 (phần còn lại của repo TS7-clean; api là chỗ vướng).
- **Không có `packages/ui` dùng chung** — mỗi web app tự sở hữu shadcn design system. Logic thực sự dùng
  chung thì để trong `@sankit/{types,form-schema,rule-engine}`, còn config dùng chung thì để trong
  `@sankit/config`.
- **Web app deploy dưới dạng Cloudflare Workers với static assets** (không phải Pages). Giữ nguyên Worker
  entry thật + `wrangler.jsonc` của từng app.
- **Giữ `main` luôn release được.** Nếu một thay đổi có rủi ro, hãy gate nó sau một flag hoặc chia PR nhỏ ra.
- **Không commit output sinh ra tự động** (`dist`, `.turbo`, `node_modules`, `dist` của Expo) — đã có
  trong `.gitignore`.
- **Kỷ luật bootstrap:** không viết business logic / schema / auth wiring nằm ngoài ticket sở hữu nó.

---

## 5. Cần trợ giúp

Bị block? Comment vào Linear ticket hoặc báo trong channel của team kèm ticket ID. Đừng lách một blocker
bằng cách phá vỡ house rule.
