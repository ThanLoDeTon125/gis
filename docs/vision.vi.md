# Sankit Monorepo — Bootstrap Vision

> Nguồn chân lý (source of truth) cho task-loop. Rút ra từ `BOOTSTRAP.md` + hiểu biết chung từ
> grilling-session. **Chỉ đọc (read-only)** trong suốt loop. CHỈ trong phạm vi bootstrap.

## Intent

Dựng lên một **runnable skeleton** cho Sankit monorepo (GitHub org `SANKIT-PRODUCT`).
Sankit là nền tảng GACP-compliance / truy xuất nguồn gốc cho dược liệu Việt Nam —
3 app cho 3 nhóm người dùng (Sankit Admin, Farm Manager/HTX, Field User). Task này dựng cái
scaffold rỗng để các feature sau này sống trong đó. **Chưa có business logic, chưa có data schema,
chưa cấu hình auth** — đó là các ticket riêng.

## Ranh giới phạm vi cứng (non-goals)

- KHÔNG business/feature code, KHÔNG domain model, KHÔNG GACP rule, KHÔNG auth wiring.
- KHÔNG thư viện thừa nào ngoài những cái đã liệt kê rõ.
- Các dep được pre-install-nhưng-chưa-configure là cố ý (Drizzle, Better Auth, CASL trong api;
  Drizzle + expo-sqlite trong sk-go). Chỉ install; không configure.

## Locked stack (không được đổi)

- **Monorepo:** pnpm + Turborepo + `pnpm-workspace.yaml`. TypeScript strict toàn repo.
- **Lint/format:** `oxlint` + `oxfmt` (KHÔNG phải ESLint/Prettier). oxfmt còn pre-1.0 — nếu nó
  vỡ trên một file nào đó thì báo lại; KHÔNG âm thầm quay về Prettier.
- **Tests:** Vitest trên toàn repo (bỏ Jest mặc định của Nest).
- **Package manager:** pnpm 11.9 (field `packageManager`). Node 24 (`.nvmrc`).
- **Mọi dep đều install qua CLI `pnpm add`** — không bao giờ tự tay ghi block dependency.

### apps/api — NestJS
TypeScript. `GET /health` → 200. Chỉ empty module. Pre-install (KHÔNG configure):
`drizzle-orm` + `node-postgres` (pg), Better Auth, CASL. Vitest thay cho Jest.

### apps/sk-ops & apps/sk-hub — Vite + React + TS
Tailwind + shadcn/ui (khởi tạo **theo từng app** — mỗi app tự sở hữu design system, KHÔNG có
`packages/ui` dùng chung). TanStack Query + TanStack Router + TanStack Form, Valibot, Zustand.
- sk-ops → một route render ra **"Web Admin"** (ứng với Sankit Admin).
- sk-hub → một route render ra **"Web HTX"** (ứng với Farm Manager).

### apps/sk-go — Expo (React Native) + TS
Install Drizzle + expo-sqlite (chưa dùng lúc này). Một màn hình rỗng.

### packages/
- `types`, `form-schema`, `rule-engine` — rỗng (placeholder `export {}`), cross-importable.
- `config` — tsconfig base dùng chung, oxlint config, Tailwind preset **base** dùng chung
  (mỗi web app layer theme riêng lên trên), Vitest config dùng chung.

Scope package nội bộ: `@sankit/*` (ví dụ `@sankit/config`). App giữ tên trơn.

## Locked decisions (từ grilling)

1. **Root scaffold** — mọi thứ ở root của repo, KHÔNG có thư mục `sankit/` lồng bên trong.
2. **Local git only** — `git init`, commit tách theo từng app/package, **không remote / không push**.
3. **Không có shared UI package** — mỗi web app tự sở hữu shadcn design system.
4. **Workers Static Assets, KHÔNG phải Cloudflare Pages** — một deviation có chủ đích, được ghi lại rõ,
   khác với chữ "Pages" trong BOOTSTRAP. Mỗi web app dùng `@cloudflare/vite-plugin` và deploy dưới dạng
   một Worker với `[assets]` binding (placeholder secret trong `wrangler.jsonc`). Smoke test
   `@cloudflare/vitest-pool-workers` nhắm vào Worker entry thật của từng app — không cần Worker phụ dùng
   một lần rồi bỏ. Ghi lại deviation này trong README + một ADR.
5. `oxlint` + `oxfmt`; Vitest ở mọi nơi; dep chỉ qua CLI `pnpm add`.

## Deferred / placeholder (ghi chú lại, chưa quyết)

- Engine offline-sync cho mobile (PowerSync / ElectricSQL / tự làm) — rủi ro mở lớn nhất, chưa chốt.
  Nằm ngoài phạm vi bootstrap. sk-go giữ nguyên Expo trần + Drizzle/sqlite chưa dùng.
- Storage (R2), bộ generate PDF dossier, schema/auth thật — tất cả là ticket sau này.

## Done nghĩa là

- `pnpm install` + `pnpm build` + `pnpm lint` + `pnpm test` pass trên toàn repo.
- api `GET /health` trả về 200.
- sk-ops + sk-hub mở ra một trang trắng ("Web Admin" / "Web HTX").
- sk-go Expo chạy được.
- Smoke test Cloudflare Workers pass.
- README root ngắn gọn (cách chạy dev cho từng app + directory structure) + ADR cho deviation
  Pages→Workers.
- Commit tách theo từng app/package (local).
