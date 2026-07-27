# Sankit — Shared Design Contract

*Single source of truth for everything the three apps share. Three designers work separately and cannot coordinate — so when your app doc and this doc disagree, **this doc wins**. Read this + your one app doc. Any new shared word, seal, state, or token is added **here first**.*

---

## 1. The product in one page

**What Sankit is.** A platform that helps farming cooperatives *prove* to outside auditors that they followed a certification standard (like GACP). Proof is captured in the field, at the moment of work, with a photo and an auto-stamped who / when / where — so records are trustworthy, instead of paperwork reconstructed from memory before an audit.

**The core insight (shapes all three apps).** A record only counts if it is captured *on the spot, by the doer, with proof*. That single idea drives everything: the field app is gamified so capture is cheap and rewarding; the seal proves a record is real; the dashboards exist to keep the right proof flowing and turn it into an audit dossier.

**The three apps — one product.**
- **sk-ops** — Sankit staff run the platform (configure standards & rules, onboard coops, monitor the fleet). Desktop, data-dense.
- **sk-hub** — a coop manager runs their coop (registry, staff, tasks, readiness, reports). Web + tablet.
- **sk-go** — coop field workers capture observations. Mobile, offline, gamified.

**Golden rule:** the three apps must feel like one product. Shared words, the Verified seal, states, and design tokens must match **exactly** across all three. Don't invent local variants.

---

## 2. Vocabulary & label map (authoritative — anti-drift)

One concept, one internal name, and a fixed user-facing label per app. **Never invent a new user-facing noun in an app doc.** If a screen needs a new word, it is added to this table first.

| Internal concept | sk-ops label | sk-hub label | sk-go label | Plain meaning |
|---|---|---|---|---|
| Standard | Programme / Standard | Programme | *(hidden)* | A certification scheme (GACP, GlobalGAP, buyer rules) |
| Requirement | Requirement | Goal | *(hidden)* | One thing a Standard demands be proven |
| Observation (assigned) | Task | Task | **Task** | A job to capture |
| Observation (completed) | Record | Record | **Log** | A finished, saved capture |
| Provenance | Provenance | Verified | **Verified ✓** | The proof attached (photo + who/when/where) |
| Schedule (recurring) | Routine | Routine | **Routine** | A Task that repeats |
| Condition / interval gate | Gate | Gate | **Locked until…** | An action blocked until a condition is met |
| Rule violation / gap | Flag | Issue | *(blocked screen)* | A problem to fix before audit |
| Reference data | Reference data | *(read-only)* | *(invisible)* | Lookup tables rules use (lists, limits) |
| Report | Audit pack | Audit pack | — | Evidence assembled for the auditor |
| Registry site | Site / Plot | Plot | **Plot** (map tile) | A piece of the farm |
| Crop / batch | Crop / Batch | Crop / Batch | *(context)* | What's grown, and a specific lot |
| Operator | Operator | Staff | *(the signed-in user)* | A field worker (the provenance "who") |
| Engagement | *(analytics)* | Engagement | **Streak / Points** | Keep-up rewards, earned only for Verified logs |
| Attestation | Document | Documents | — | Signed paperwork that can't be field-captured |

Field workers (**sk-go**) never see internal terms — only Task / Log / Plot / Routine / Verified / Locked.

---

## 3. Provenance & the "Verified ✓" seal

- **What it is:** who (signed-in user) + when (device time) + where (GPS) + photo, captured at the moment of the act. Attached silently and automatically.
- **When shown:** on **every completed record**, in all three apps.
- **Seal visual:** a check mark + the word "Verified", in the **Success/Verified** color role (§6). Small, consistent placement (corner of a record/photo thumbnail).
- **Weak/unverified record:** if a required signal is missing (e.g. no GPS), show a **Caution**-colored "Unverified" / "Needs GPS" state — never the Verified seal. All three apps use this same distinction.
- **Earning rule (gamification):** points/streaks accrue **only for Verified records**. Never reward raw volume; no "most logs" leaderboards. This is deliberate anti-faking and applies everywhere.
- **Immutability:** records cannot be edited after capture. Corrections are new records. All apps present logs as read-only history.

---

## 4. Gate / Lock / Issue model (shared states)

- **Gate = a Rule firing at the moment of an action.** Two severities, visually distinct everywhere:
  - **Hard gate → blocks.** Uses the **Danger** color; a clear "stop". Cannot proceed. (e.g. product not on approved list.)
  - **Soft flag → warns.** Uses the **Caution** color. Proceed-with-note (the note is logged for manager review).
- **"Locked until…" format (shared copy pattern):** always state **reason + unlock date** — "Harvest locked — 4 days left in the waiting period (opens 24 Jun)." Same wording pattern in sk-go (worker sees it) and sk-hub (manager sees it).
- **Issue lifecycle (hub & ops):** `open → in progress → resolved`, where resolution = task assigned / evidence added / justified override. Same states and labels in both dashboards.
- **Authoring → display seam:** the message text for a gate/rule is authored **once in sk-ops** and appears **verbatim** to the worker in sk-go and the manager in sk-hub. One string, three surfaces — designers must leave room for operator-authored copy, not hardcode it.

---

## 5. Shared entities (canonical names + key fields)

All three apps use these exact names and IDs. Dashboards create/manage them; the field app references them.

- **Plot / Site** — `id`, `name`, `boundary/GPS`, `coop`, `season`. *ID must stay stable across seasons — rule correctness depends on it.*
- **Crop / Batch** — `id`, `species`, `plot`, `planting date`.
- **Operator** — `id`, `name`, `role`, `coop`. *This is the provenance "who".*
- **Programme (Standard)** — `id`, `name`, `version`, `renewal date`.
- **Requirement (Goal)** — `id`, `programme`, `description`, `evidence bar`.
- **Observation (Task / Log / Record)** — `id`, `type` (schema), `payload`, `provenance`, `links` (plot / crop / operator / timestamp), `status`.
- **Reference data** — `table`, `version`, `effective date`.

---

## 6. Shared visual language (semantic slots — designers own the values)

*This section defines only the **shared meanings and slots** three siloed designers must agree on. The actual values — hex, type sizes, spacing, component styling — are the **designer's job**. Requirement: whatever values are chosen must be **used consistently across all three apps** and legible in sunlight and for low-literacy users.*

**Semantic color roles** (name the meaning, not the value). Each must exist, be visually distinct, and mean the same thing in every app. Other sections refer to these by role name — never a specific value; the designer maps role → value.
- **Success / Verified**
- **Primary / action**
- **Positive / schedule**
- **Caution / at-risk / stale**
- **Danger / hard-gate / error**
- **Neutrals** (ink, body, muted, line, surface, background)

**Type & spacing:** one shared type scale and one spacing/radius system across all apps (designer sets the values). Vietnamese diacritics must render cleanly at every size.

**Shared components** (must exist and read identically across apps; designer styles them): Card · Status pill (uses the color roles) · Provenance seal · Progress ring · Readiness meter · Streak counter · Badge · Photo-thumbnail-with-seal · "Locked until…" banner · Issue/Flag row.

**Gamification visual language** (shared *moments*; designer designs them): progress rings/meters, streak indicator, milestone markers, brief celebration moments. Intended tone: encouraging and clean — professional-playful, not childish. Intensity varies by app (heavy in sk-go, moderate in sk-hub, light in sk-ops); the visual family stays consistent.

**Iconography:** legible at small size and in sunlight; paired with short words (critical for low-literacy sk-go).

**Localization:** Vietnamese-first across all apps; icon-supported; keep copy short.

---

## 7. Global states (all apps)

Define once, match everywhere: **loading · empty · error · offline · at-risk · stale-reference-data.** Offline is central to sk-go; at-risk and stale are first-class in the dashboards. Map each state to the **color roles in §6** so the three apps read identically.

---

## 8. Cross-app seams (explicit handoffs)

These are the joints where one app's output becomes another's input. Get the shared piece wrong and the product breaks at the seam.

- **Standard / Requirement / Rule / Reference data** authored in **sk-ops** → **sk-hub** shows readiness & issues against them; **sk-go** shows the resulting tasks & gates.
- **Gate/rule message string:** authored in **sk-ops** → shown verbatim in **sk-go** (worker) and **sk-hub** (manager).
- **Reference data version:** published in **sk-ops** → **sk-go** warns when its copy is stale → **sk-ops** sees device staleness.
- **Observation captured in sk-go** → appears in **sk-hub** records feed and **sk-ops** adoption analytics.
- **Readiness in sk-hub** = coverage of **sk-ops**-defined Requirements.
- **Provenance seal** is identical wherever it appears: earned in sk-go, reviewed in sk-hub, integrity-monitored in sk-ops.

---

## 9. How to use this doc

1. Read **this** + your single app doc. Nothing else needed.
2. On any conflict, **this doc wins**.
3. Need a new shared word, state, seal behavior, or token? It goes **here first**, then into the app docs — never invented locally.
4. Anything ambiguous or missing → flag to the doc owner rather than guessing (you can't ask the other designers).
