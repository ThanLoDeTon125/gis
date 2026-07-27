# Contributing

Tài liệu này cho mỗi developer của Sankit biết cách làm việc. Đọc tài liệu này trước khi bạn thay
đổi repository.

> Repository này là **proprietary and confidential** — xem [LICENSE.md](./LICENSE.vi.md). Không
> chia sẻ source, configuration, hay quy trình setup ra ngoài Company.

---

## 0. Setup một lần

1. Cài toolchain → [docs/PREREQUISITES.md](./docs/PREREQUISITES.vi.md)
2. Set up repository → [docs/INSTALLATION.md](./docs/INSTALLATION.vi.md)

Trước khi bắt đầu, hãy chắc chắn `pnpm build`, `pnpm lint`, và `pnpm test` đều xanh.

---

## 1. Mọi thay đổi đều đi qua Pull Request

**Không commit thẳng vào `main`.** Nhánh `main` được bảo vệ và luôn release được. Mọi công việc
vào `main` qua một pull request và một review.

### The loop

1. **Bắt đầu từ một Linear ticket.** Mỗi thay đổi có một Linear issue (ví dụ `SANKIT-123`). Nếu
   không có ticket, không mở pull request.
2. **Tạo nhánh từ `main`.** Đặt ticket ID trong tên nhánh:
   ```sh
   git switch main && git pull
   git switch -c SANKIT-123-short-description
   ```
3. **Commit** theo từng bước nhỏ và logic. Dùng **Conventional Commits** (xem §2).
4. **Mở một pull request** vào `main`:
   - Title: `SANKIT-123: <what changed>` (ticket ID giúp Linear tự động link pull request).
   - Description: nói cái gì thay đổi và tại sao. Nói bạn đã test thế nào. Thêm screenshot cho
     thay đổi UI.
   - Link Linear ticket. Dán URL, hoặc dùng integration Linear ↔ GitHub.
5. **Qua hết các gate** (§3). CI phải xanh. Pull request phải có ít nhất **một review approve**.
6. **Merge**, rồi xoá nhánh.

> 🔴 **CHỈ DÙNG SQUASH MERGE.** Mỗi pull request lên `main` là **một commit squash duy nhất**.
> Không dùng merge commit. Không dùng rebase-and-merge. Không push nhiều commit thô. Quy tắc này
> giữ một commit sạch cho mỗi ticket trong history của `main`. Đặt title commit squash là
> `SANKIT-123: <what changed>`.

> Mẹo: đặt ticket ID trong tên nhánh **và** trong title pull request. Khi đó Linear tự link cả
> hai.

### Các concept Git cần biết

Workflow này dùng một số feature của Git. Nếu một feature còn mới với bạn, đọc trang liên quan bên
dưới trước. Các trang này ngắn và thực dụng — bạn không cần đọc hết man page.

- **Branching** — [Atlassian: Using branches](https://www.atlassian.com/git/tutorials/using-branches)
- **Squash** — [Tower: Squash commits](https://www.git-tower.com/learn/git/faq/git-squash) (mỗi pull request lên `main` bằng cách này — xem §1)
- **Cherry-pick** — [Atlassian: git cherry-pick](https://www.atlassian.com/git/tutorials/cherry-pick) (chuyển một commit giữa các nhánh, ví dụ một hotfix)
- **Worktree** — [DataCamp: Git worktree](https://www.datacamp.com/tutorial/git-worktree-tutorial) (làm việc trên hai hay nhiều nhánh cùng lúc, không cần stash hay switch)

---

## 2. Conventional Commits

```
<type>(<scope>): <subject>
```

Types: `feat`, `fix`, `chore`, `docs`, `refactor`, `test`, `style`, `perf`, `ci`.
Scope là tên app hoặc package (`sk-backend`, `sk-ops`, `sk-coop`, `sk-go`, `config`, `types`, …).

Ví dụ:

- `feat(sk-backend): add tenant guard to health module`
- `fix(sk-ops): correct TanStack Router param typing`
- `chore(config): bump oxlint base rules`

---

## 3. Definition of Done (mọi mục phải pass trước khi bạn request review)

- [ ] `pnpm build` — xanh
- [ ] `pnpm lint` — xanh (**chỉ oxlint + oxfmt**; không ESLint/Prettier)
- [ ] `pnpm format:check` — sạch
- [ ] `pnpm test` — xanh (Vitest; không Jest)
- [ ] Hành vi mới có test (ưu tiên TDD — red → green → refactor)
- [ ] Pull request đã link với Linear ticket của nó
- [ ] Không có secret, không có giá trị `.env`, không có dữ liệu proprietary trong các commit

---

## 4. House rules

- **Chỉ thêm dependency bằng CLI** — `pnpm add` / `pnpm add -D`. Không tự tay ghi dependency vào
  `package.json`.
- **Cài vào đúng workspace:** `pnpm add <pkg> --filter <app>` (hoặc `-w` cho root).
- **Giữ TypeScript ở 6.0.3** — chưa chuyển sang native compiler TS 7. Tooling của repository
  (wrangler, Vitest, Expo) chưa được validate trên tsgo.
- **Không tạo `packages/ui` dùng chung** — mỗi web app tự sở hữu shadcn design system. Đặt logic
  dùng chung trong `@sankit/{types,form-schema,rule-engine}`. Đặt configuration dùng chung trong
  `@sankit/config`.
- **Web app deploy dưới dạng Cloudflare Workers với static assets** (không phải Pages). Giữ
  nguyên Worker entry và `wrangler.jsonc` của mỗi app.
- **Giữ `main` luôn release được.** Nếu một thay đổi có rủi ro, đặt nó sau một flag, hoặc giữ pull
  request nhỏ.
- **Không commit output sinh tự động** (`dist`, `.turbo`, `node_modules`, `dist` của Expo). Các
  đường dẫn này đã có trong `.gitignore`.
- **Kỷ luật bootstrap:** không thêm business logic, schema, hay auth wiring ngoài ticket sở hữu
  chúng.

---

## 5. Nhận trợ giúp

Nếu bạn bị block, comment vào Linear ticket, hoặc gửi tin nhắn kèm ticket ID trong channel của
team. Không phá house rule để lách một blocker.
