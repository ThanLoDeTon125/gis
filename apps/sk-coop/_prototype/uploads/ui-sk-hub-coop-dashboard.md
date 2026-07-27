# sk-hub — Coop Manager Dashboard (UI Design Brief)

*The dashboard a cooperative uses to manage its own scope: its plots, its staff, its tasks, its evidence, and its progress toward certification. Web-first (desktop + tablet).*

> **Read this with `sk-shared-contract.md`.** That shared doc is authoritative for vocabulary, the Verified ✓ seal, gate/lock/issue states, shared entities, and design tokens. This doc covers only what's specific to sk-hub.

---

## 0. Context (read first)

**What Sankit is.** Sankit helps farming cooperatives *prove* to an outside auditor that they followed a certification standard (like GACP). Proof is captured in the field, at the moment of work, with photos — so it's trustworthy, instead of paperwork reconstructed from memory just before an audit.

**The one thing that shapes this app.** A coop passes or fails an audit months from now based on whether the right proof got captured *along the way*. This dashboard is the manager's cockpit for staying **audit-ready**: seeing what proof is still missing, fixing problems *before* the auditor arrives, keeping field staff active, and producing the evidence pack on demand. Design it **forward-looking** — always answer "are we on track, and what's missing?" — not as a rear-view record.

**The three apps (you're building the second).**
- *sk-ops* — Sankit's own staff run the platform.
- **sk-hub (this doc)** — a coop manager runs their coop's scope.
- *sk-go* — coop field workers capture proof in the field.

**Words you'll use:** Programme · Goal · Record · Verified ✓ · Task/Routine · Issue · Gate · Documents · Audit pack · Plot/Crop. Full plain-words meanings and the cross-app mapping are in **`sk-shared-contract.md` §2** (authoritative — don't reinvent labels).

---

## 1. Who & where

- **Users:** coop manager(s) and admin staff. Moderate literacy/tech comfort. Office or on-site, tablet or laptop.
- **Core job:** make sure the coop is **audit-ready** — the right observations are being captured, gaps and issues are resolved *before* the audit, staff stay active, and the evidence dossier can be produced on demand.
- **Design north star:** always answer **"are we on track, and what's missing?"** — forward-looking, not just a record of the past.

---

## 2. Conventions

**Shared — defined in `sk-shared-contract.md`, don't redefine here:** the vocabulary/label map (§2), the Verified ✓ seal (§3), gate/lock/issue states (§4), shared entities (§5), design tokens (§6), and global states (§7).

**sk-hub-specific emphasis (moderate gamification — this is a management tool):**
- **Season-campaign framing:** progress toward certification shown as a filling **Readiness meter** per Programme, with milestones.
- **Quest-log for issues:** gaps and flags as a prioritized "to resolve" list, with clear wins when cleared.
- **Team engagement, healthily:** surface staff activity/streaks to spot who's active or stuck — support framing, not surveillance or ranking.
- **Forward-looking, always:** every Programme view leads with what's *still missing* per Goal, with deadlines from Routines.
- **Dashboard patterns:** readiness/status first; **at-risk** and **overdue** are first-class statuses; every summary number drills down to the underlying records; spot-check tools on records (integrity).

---

## 3. Views

### 3.1 Login / Coop context
- **Purpose:** identify manager; select coop/scope if more than one.
- **Shows:** coop name, active Programmes, current season.
- **Actions:** sign in; switch coop.

### 3.2 Overview (Campaign HQ)
- **Purpose:** the "on track?" answer at a glance.
- **Shows:** Readiness meter per Programme; season progress; top Issues (gaps, flags, overdue); team activity snapshot; upcoming deadlines (from Routines); stale-reference-data warnings.
- **Actions:** jump to Issues, Readiness board, Reports.
- **Game:** readiness meters, milestone markers, "cleared this week" wins.
- **States:** healthy / at-risk / behind; pre-audit countdown when a date is set.

### 3.3 Readiness board (Requirements coverage) — KEY VIEW
- **Purpose:** forward-looking "what's still missing" per Programme.
- **Shows:** each Goal with status (complete / partial / missing / at-risk), evidence count, and the specific outstanding items (e.g. "water lab test not yet done for Plot A3").
- **Actions:** create/assign a Task to close a gap; open the evidence behind a Goal; filter by plot/crop.
- **Game:** Goals as a checklist that fills; at-risk Goals flagged with deadline.
- **Notes:** this is the heart of sk-hub — it turns a Programme into a live task list, not a report skin.

### 3.4 Registry management (Plots, Crops, Batches)
- **Purpose:** maintain the entities everything else references.
- **Shows:** plot map + list; crops/batches per plot; season assignments.
- **Actions:** add/edit/retire plots; draw/adjust boundaries; assign crops; manage batches.
- **Notes:** **plot identity quality directly affects rule correctness** — make boundaries and stable IDs easy to get right; warn on re-numbering across seasons.

### 3.5 Team / Operators
- **Purpose:** manage field staff and their work.
- **Shows:** staff list, roles, assigned plots/routes, activity/streak, workload, completion rate.
- **Actions:** add/deactivate staff (identity for provenance); assign plots/tasks; reset access.
- **Game:** engagement indicators to spot inactive staff early — support framing.

### 3.6 Tasks & Routines (scheduling)
- **Purpose:** decide what gets captured and when.
- **Shows:** one-off Tasks and recurring Routines; assignee; cadence; completion rates.
- **Actions:** create Task; set Routine (daily/weekly/seasonal); bulk-assign; reassign.
- **Notes:** Routines are the adoption engine — make cadences easy to set and monitor.

### 3.7 Records feed (Observations)
- **Purpose:** review what's being captured; spot-check integrity.
- **Shows:** stream of records with photo thumbnails, Verified ✓, plot/crop/worker/type/date.
- **Actions:** filter/search; open a record; flag suspicious; mark reviewed (spot-audit).
- **Notes:** integrity backstop — surface anomalies (duplicate photos, GPS mismatch) for manager review.

### 3.8 Issues to resolve
- **Purpose:** the coop's "fix-it" queue before audit.
- **Shows:** rule flags (audit-mode), coverage gaps, unresolved soft-gate notes, stale data — prioritized by risk/deadline.
- **Actions:** resolve (assign task, add note/evidence, override with justification); track status.
- **Game:** quest-log feel; visible progress as issues clear.

### 3.9 Documents / Attestations
- **Purpose:** home for the signed-paperwork slice that has no capture flow.
- **Shows:** required documents per Programme (contracts, training records, species/soil certs), upload status, expiry/renewal dates.
- **Actions:** upload; link to a Goal; set renewal reminders.
- **Notes:** deliberately called out — this slice is easy to forget and often fails audits.

### 3.10 Audit pack / Reports
- **Purpose:** produce the auditor-facing dossier on demand.
- **Shows:** per Programme, the assembled evidence mapped to Goals; pre-audit checklist; missing-evidence report.
- **Actions:** generate/export dossier (per Programme format); export gap report; share.
- **Game:** "audit-ready" completion state.

### 3.11 Programmes & renewal
- **Purpose:** manage which Standards the coop pursues and their clocks.
- **Shows:** active Programmes, certification status, renewal dates.
- **Actions:** request adding a Programme (routes to sk-ops); view renewal timeline.

### 3.12 Notifications & activity log
- **Purpose:** keep the manager ahead of deadlines and changes.
- **Shows:** overdue tasks, upcoming routines, resolved gates, reference-data updates, staff activity.

---

## 4. Cross-cutting requirements
- **Forward-looking bias:** every Programme view emphasizes what's outstanding and by when.
- **Drill-down everywhere:** summaries → records → provenance.
- **Localization:** Vietnamese first.
- **Roles:** manager vs read-only staff.
- **Tablet-friendly** for on-site use.

---

## 5. Open design questions
- How much **integrity/anomaly surfacing** belongs to the manager vs sk-ops (avoid overwhelming).
- Balancing **team engagement visibility** so it supports rather than surveils.
- How to make **plot identity** hard to get wrong without heavy GIS tooling.
