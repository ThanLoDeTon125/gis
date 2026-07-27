# sk-ops — Sankit Operations Dashboard (UI Design Brief)

*The internal dashboard Sankit staff use to run the platform: declare standards, manage reference data, onboard and monitor coops, and safeguard integrity and adoption across the whole fleet. Web, desktop-first, data-dense.*

> **Read this with `sk-shared-contract.md`.** That shared doc is authoritative for vocabulary, the Verified ✓ seal, gate/lock/issue states, shared entities, and design tokens. This doc covers only what's specific to sk-ops. (sk-ops uses the full internal vocabulary — see the map in §2 of the shared doc.)

---

## 0. Context (read first)

**What Sankit is.** Sankit is a platform that helps farming cooperatives *prove* to outside auditors that they followed certification standards (like GACP). The core idea: capture proof in the field at the moment of work — with photos and an auto-stamped who / when / where — so records are trustworthy, instead of reconstructed paperwork nobody believes.

**The one thing that shapes this app.** sk-ops is Sankit's internal control room. Sankit's own staff use it to (1) set up the standards and rules the whole system enforces, (2) onboard cooperatives, and (3) watch the health of *every* coop — is proof actually being captured, is anyone faking it, will the auditor accept it. It's a **professional, data-dense, multi-tenant admin tool**: clarity and oversight over delight.

**The three apps (you're building the operator side).**
- **sk-ops (this doc)** — Sankit's own staff run the platform.
- *sk-hub* — a coop manager runs their coop.
- *sk-go* — coop field workers capture proof in the field.

**Words you'll use (full internal vocabulary):** Coop · Fleet · Standard/Programme · Requirement · Rule (gate/audit) · Reference data · Observation · Provenance · Registry · Report/Audit pack. Full definitions and the cross-app label map are in **`sk-shared-contract.md` §2** (authoritative). sk-ops is where these are configured, so it uses the exact internal names.

---

## 1. Who & where

- **Users:** Sankit operators/admins — technical, professional. Desktop, multi-monitor, long sessions.
- **Core job:** configure the system (Standards, Rules, Reference data), onboard coops, and **monitor the health of the whole fleet** — compliance, adoption, and integrity.
- **Design north star:** **control + oversight.** Clarity and density over delight; make risk visible early across many coops.

---

## 2. Conventions

**Shared — defined in `sk-shared-contract.md`, don't redefine here:** the vocabulary/label map (§2), the Verified ✓ seal (§3), gate/lock/issue states (§4), shared entities (§5), design tokens (§6), and global states (§7). sk-ops uses the **full internal vocabulary** (Standard, Requirement, Rule, Observation, Provenance, Registry, Reference data, Timing, Report) and is where those labels are *authored* for the other apps.

**sk-ops-specific emphasis (light gamification — professional tool):**
- Minimal game feel. Borrow only **health scores, coverage meters, and status signals** to make fleet state scannable. No streaks/points for operators (any streak data here is *analytics about field users*).
- **Fleet-first:** default to portfolio views, drill down to one coop.
- **Risk surfacing:** at-risk coops, integrity anomalies, and stale data bubble to the top.
- **Versioning is first-class:** Standards and Reference data carry versions + effective dates; always show which version is live and where deployed.
- **Density done well:** tables, filters, saved views, bulk actions; **at-risk** and **stale** are first-class states.

---

## 3. Views

### 3.1 Login / Admin & roles
- **Purpose:** authenticated access with role scoping (super-admin, standard-author, support, read-only).
- **Actions:** sign in; manage operator users & roles.

### 3.2 Fleet overview
- **Purpose:** health of all coops at a glance.
- **Shows:** each coop's readiness, activity, adoption, and risk flags; sortable/filterable table + summary tiles; fleet-wide KPIs.
- **Actions:** filter by Programme/region/risk; open a coop.
- **Game:** health scores/meters, status colors.
- **States:** coops at-risk, inactive, or with integrity flags pinned to top.

### 3.3 Coop detail (drill-down)
- **Purpose:** everything about one coop.
- **Shows:** their Programmes & readiness, registry size, staff activity, open issues, device/sync health, integrity flags, support history.
- **Actions:** assist/impersonate (audited), adjust their Programmes, contact, open support ticket.

### 3.4 Standard authoring
- **Purpose:** declare & configure a Standard mostly as data.
- **Shows:** a Standard's Requirements, evidence bars per Requirement, schedules, report/dossier shape, renewal clock; version history.
- **Actions:** create/edit Standard; add Requirements; define evidence bars (photo / record / signed document / lab cert); publish a version.
- **Notes:** this view embodies the "add a standard by declaring it" thesis — make the data-driven parts fully editable; clearly mark where a **code tail** is needed (novel rule shape or evidence type) and route that to engineering.

### 3.5 Rule authoring
- **Purpose:** define machine checks and bind them to Requirements + Reference data.
- **Shows:** rule list; per rule — shape (single-event / multi-event), firing mode (gate / audit), inputs (which observation types, which axes, which reference table), the condition, and the message shown to field staff.
- **Actions:** create/edit rule; test against sample observations; enable/disable; set gate message copy (this copy appears in sk-go 3.5).
- **Notes:** distinguish what's configurable-data vs what needs engineering. Provide a rule-tester with sample data.

### 3.6 Reference data management
- **Purpose:** manage the lookup tables rules depend on.
- **Shows:** approved lists, thresholds, QCVN-style limits, active-ingredient equivalences; **versions with effective dates**; where each version is deployed; diff between versions.
- **Actions:** edit; publish a new version with an effective date; view diff; see rollout status to devices.
- **Notes:** **effective-dating is critical** — audits judge against the version valid on the action date, and offline devices may run older versions. Make staleness and rollout status highly visible (ties to sk-go 3.9 warnings).

### 3.7 Onboarding / Coop provisioning
- **Purpose:** stand up a new coop.
- **Shows:** wizard — coop details, assigned Programmes, seed registry (plots/crops), invite manager(s).
- **Actions:** create coop; assign Programmes; bulk-import registry; send invites.

### 3.8 Adoption & engagement analytics
- **Purpose:** answer "is capture actually happening?" across the fleet.
- **Shows:** capture rates, active field users, task/routine completion, streak health, trends by coop/region/time.
- **Actions:** segment; drill to coop/worker; export.
- **Notes:** this view monitors the adoption guarantee (a known project risk) — design it to expose decline early.

### 3.9 Integrity / Anti-cheat monitoring
- **Purpose:** detect and act on faked or weak provenance.
- **Shows:** anomaly flags — duplicate/staged photos, GPS-vs-plot mismatch, device-clock skew, capture bursts, gallery-vs-live inconsistencies; per-coop integrity score; spot-audit scheduler.
- **Actions:** review a flag; schedule a physical spot-audit; mark false positive; escalate.
- **Notes:** provenance is a deterrent, not proof — this view is where the deterrent is enforced. High-priority.

### 3.10 Device & sync fleet health
- **Purpose:** keep offline devices current and syncing.
- **Shows:** devices by coop; last sync; **stale reference-data warnings**; queued-upload backlogs; app versions.
- **Actions:** nudge sync; flag devices with dangerously stale data; push updates.

### 3.11 Audit-acceptance registry
- **Purpose:** track, per Programme/region, whether certifiers accept digital provenance-stamped evidence.
- **Shows:** acceptance status by scheme + certifier + region; notes; last verified date.
- **Actions:** record/update acceptance; flag Programmes where digital is not yet accepted.
- **Notes:** this encodes the single gating assumption of the whole platform — keep it explicit and current.

### 3.12 Support, tickets & system settings
- **Purpose:** run support and configure the platform.
- **Shows:** tickets, system config, feature flags, audit log of operator actions.

---

## 4. Cross-cutting requirements
- **Multi-tenant:** strict coop data isolation; clear tenant context at all times.
- **Versioning & auditability:** every Standard/Rule/Reference change is versioned, effective-dated, and logged.
- **Density done well:** tables, filters, saved views, bulk actions.
- **Role-based access** across authoring vs support vs read-only.

---

## 5. Open design questions
- Where the **data/config boundary vs code tail** is drawn in Standard/Rule authoring — how to show "this needs engineering."
- How much **integrity tooling** is automated vs operator-driven.
- Balancing **fleet density** with fast drill-down to a single coop or worker.
