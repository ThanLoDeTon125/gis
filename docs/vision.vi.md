# Sankit Monorepo — Bootstrap Vision

> Tài liệu này là nguồn chân lý (source of truth) cho task-loop. Nó đến từ `BOOTSTRAP.md` và hiểu
> biết chung từ grilling session. Nó **chỉ đọc (read-only)** trong suốt loop. Nó CHỈ bao phủ phạm
> vi bootstrap.

## Intent

Dựng một **runnable skeleton** cho Sankit monorepo (GitHub org `SANKIT-PRODUCT`). Sankit là nền
tảng GACP-compliance và truy xuất nguồn gốc cho dược liệu Việt Nam. Nó có 3 app cho 3 nhóm người
dùng (Sankit Admin, Farm Manager/HTX, Field User). Task này dựng scaffold rỗng để sau này chứa
các feature đó. **Task này không thêm business logic, không thêm data schema, và không cấu hình
auth** — đó là các ticket riêng.

## Ranh giới phạm vi cứng (non-goals)

- KHÔNG business hay feature code, KHÔNG domain model, KHÔNG GACP rule, KHÔNG auth wiring.
- KHÔNG thư viện thừa ngoài danh sách đã liệt kê rõ.
- Các dependency pre-install nhưng chưa configure là cố ý (Drizzle + expo-sqlite trong sk-go).
  Chỉ install chúng. Không configure chúng.

## Locked stack (không được đổi)

- **Monorepo:** pnpm + Turborepo + `pnpm-workspace.yaml`. TypeScript strict trên toàn repository.
- **Lint/format:** `oxlint` + `oxfmt` (KHÔNG phải ESLint/Prettier). oxfmt còn pre-1.0. Nếu nó vỡ
  trên một file, hãy báo lại file đó. KHÔNG âm thầm quay về Prettier.
- **Tests:** Vitest trên toàn repository (không Jest).
- **Package manager:** pnpm 11.9 (field `packageManager`). Node 24 (`.nvmrc`).
- **Chỉ install dependency bằng CLI `pnpm add`** — không tự tay ghi block dependency.

### apps/sk-backend — Hono trên Cloudflare Workers

TypeScript. `GET /health` → 200. App phục vụ OpenAPI 3.1 specification tại `/openapi.json`
(hono-openapi + Valibot) và Scalar reference UI tại `/docs`. Chưa có business route.

### apps/sk-ops & apps/sk-coop — Vite + React + TS

Tailwind + shadcn/ui (khởi tạo **theo từng app** — mỗi app tự sở hữu design system, KHÔNG có
`packages/ui` dùng chung). TanStack Query + TanStack Router + TanStack Form, Valibot, Zustand.

- sk-ops → một route render ra **"Web Admin"** (ứng với Sankit Admin).
- sk-coop → một route render ra **"Web HTX"** (ứng với Farm Manager).

### apps/sk-go — Expo (React Native) + TS

Install Drizzle + expo-sqlite (chưa dùng lúc này). Một màn hình rỗng.

### packages/

- `types`, `form-schema`, `rule-engine` — rỗng (placeholder `export {}`). Chúng có thể import
  lẫn nhau.
- `config` — tsconfig base dùng chung, oxlint configuration, Tailwind preset **base** dùng chung
  (mỗi web app layer theme riêng lên trên), và Vitest configuration dùng chung.

Scope package nội bộ là `@sankit/*` (ví dụ `@sankit/config`). App giữ tên trơn.

## Locked decisions (từ grilling)

1. **Root scaffold** — mọi thứ ở root của repository. KHÔNG có thư mục `sankit/` lồng bên trong.
2. **Local git only** — `git init`, commit tách theo từng app/package, **không remote và không
   push**.
3. **Không có shared UI package** — mỗi web app tự sở hữu shadcn design system.
4. **Workers Static Assets, KHÔNG phải Cloudflare Pages** — một deviation có chủ đích và được ghi
   lại, khác với chữ "Pages" trong BOOTSTRAP. Mỗi web app dùng `@cloudflare/vite-plugin` và deploy
   dưới dạng một Worker với `[assets]` binding (placeholder secret trong `wrangler.jsonc`). Smoke
   test `@cloudflare/vitest-pool-workers` nhắm vào Worker entry thật của từng app — không có
   Worker phụ dùng một lần. Ghi lại deviation này trong README và trong một ADR.
5. `oxlint` + `oxfmt`; Vitest ở mọi nơi; dependency chỉ qua CLI `pnpm add`.

## Deferred / placeholder (ghi chú lại, chưa quyết)

- Engine offline-sync cho mobile (PowerSync / ElectricSQL / tự làm) là rủi ro mở lớn nhất. Nó
  chưa được chốt, và nó nằm ngoài phạm vi bootstrap. sk-go giữ nguyên Expo trần + Drizzle/sqlite
  chưa dùng.
- Storage (R2), bộ generate PDF dossier, và schema/auth thật đều là ticket sau này.

## Done nghĩa là

- `pnpm install` + `pnpm build` + `pnpm lint` + `pnpm test` pass trên toàn repository.
- sk-backend `GET /health` trả về 200.
- sk-ops + sk-coop mở ra một trang trắng ("Web Admin" / "Web HTX").
- sk-go Expo chạy được.
- Smoke test Cloudflare Workers pass.
- Một README root ngắn (cách chạy dev cho từng app + directory structure) + một ADR cho deviation
  Pages→Workers.
- Commit tách theo từng app/package (local).
