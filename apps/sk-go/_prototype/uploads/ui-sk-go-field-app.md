# sk-go — Field Staff App (UI Design Brief)

*The web app coop field staff use to perform observation tasks. Mobile-first, offline-first, low-literacy-friendly, gamification-led.*

> **Read this with `sk-shared-contract.md`.** That shared doc is authoritative for vocabulary, the Verified ✓ seal, gate/lock/issue states, shared entities, and design tokens. This doc covers only what's specific to sk-go.

---

## 0. Context (read first)

**What Sankit is.** Sankit is a platform that helps farming cooperatives *prove* they followed a certification standard (like GACP) — proof an outside auditor demands months later. The trick: capture that proof *at the moment of work*, with a photo, instead of letting people reconstruct paperwork from memory afterward (which auditors don't trust).

**The one thing that shapes this app.** A record only counts if it's captured on the spot, by the person doing the work, with a photo and an auto-stamped who / when / where. Field workers today avoid this because it's a boring chore with no payback — so **sk-go's entire job is to make capturing feel fast, rewarding, and obvious** (hence the gamification). If capture has friction, workers skip it and the product fails. Also plan for the field reality: **no signal** (offline), **low literacy**, and **cheap phones** — so taps over typing, icons over words.

**The three apps (you're building the third).**
- *sk-ops* — Sankit's own staff run the platform.
- *sk-hub* — a coop manager runs their coop.
- **sk-go (this doc)** — coop field workers capture observations in the field.

**Words you'll use:** Task · Log · Verified ✓ · Routine · Locked until… · Plot · Streak/Points. Full plain-words meanings and the cross-app mapping are in **`sk-shared-contract.md` §2** (authoritative — don't reinvent labels).

---

## 1. Who & where

- **Users:** coop field workers. Often low literacy, shared/cheap Android phones, working in fields with poor or no signal.
- **Device:** phone, portrait, one-hand use, outdoors (bright sun → high contrast needed). Web app (PWA-style), installable.
- **Core job:** capture observations *at the moment of work* — with photo proof — so records are trustworthy. Everything else is secondary.
- **Design north star:** the act of capturing must feel **fast, rewarding, and obvious** — cheaper than not doing it. If capture has friction, workers revert to reconstruction and the whole system fails.

---

## 2. Conventions

**Shared — defined in `sk-shared-contract.md`, don't redefine here:** the vocabulary/label map (§2), the Verified ✓ seal (§3), gate/lock/issue states (§4), design tokens & gamification visual language (§6), and global states — loading / empty / error / offline (§7).

**sk-go-specific emphasis:**
- **Gamification is heaviest in this app.** Progress rings, streaks, plot-status colors, celebratory completion — small, frequent wins. (Rewards earned only for Verified logs — the shared anti-faking rule.)
- **Always show the next action.** Home answers "what do I do now?" with one primary button.
- **Locks inform, not punish** — a gate says why, when it opens, and who to ask.
- **Low-literacy-safe:** icons + short words + color, minimal typing, pick-lists and photo over text; Vietnamese-first.
- **Field-app patterns:** persistent offline/sync indicator; one-hand reach (primary actions in the bottom third); big tap targets; high contrast for sunlight; **live-camera-only** capture (protects provenance); silent who/when/where stamping with a small "captured here, now" confirmation.

---

## 3. Views

### 3.1 Sign-in / Identity
- **Purpose:** establish *who* (the provenance "who"). 
- **Shows:** worker picker or PIN; optional face photo for high-trust logs; coop name.
- **Actions:** sign in; stay signed in on this device.
- **States:** offline sign-in must work (cached identities); wrong PIN; device not provisioned.
- **Notes:** shared devices are common — make switching users fast but explicit (identity drives provenance integrity).

### 3.2 Home / Today (the quest board)
- **Purpose:** answer "what now?" instantly.
- **Shows:** today's Tasks (count + next up), streak counter, daily progress ring, sync status, plot alerts.
- **Actions:** **Start next task** (primary CTA); open task list; open plot map.
- **States:** all done (celebration + streak), overdue tasks (gentle nudge), nothing assigned.
- **Game:** streak flame, progress ring fills as tasks complete, "all clear" reward.

### 3.3 Task list / My Tasks
- **Purpose:** the queue of what to capture.
- **Shows:** task cards grouped by Plot or by Due; each card: icon, short title, plot, due, reward, status (available / locked / done).
- **Actions:** filter (plot, due, type); tap a task → capture flow.
- **States:** locked tasks show "Locked until <date> — <reason>"; overdue highlighted; empty.
- **Game:** routines badged as recurring; completed tasks show Verified ✓ and points earned.

### 3.4 Capture flow (task detail) — THE core view
- **Purpose:** capture one Observation, fast, with proof.
- **Shows / steps:**
  1. Context: what + which plot (pre-filled from the task).
  2. Payload fields: **pick-lists, steppers, toggles — minimal free typing.** (e.g. product from an approved pick-list, dose via stepper, area preset.)
  3. **Photo capture (mandatory):** in-app camera, live capture only (no gallery upload) to protect provenance; allow multiple.
  4. Auto-stamp confirmation: "captured on Plot A3 · today · here" (who/when/where shown, not editable).
  5. Confirm & log.
- **Actions:** next/back per step; retake photo; save (works offline → queued).
- **States:** offline (queued, clearly shown); gate triggered (→ 3.5); missing required field; GPS unavailable (flag, allow with warning).
- **Game:** step progress; on confirm → success moment (3.7).
- **Notes:** keep steps minimal; every extra tap is adoption risk. Fields defined by the task's schema (metric type) — layout must be schema-driven/templated.

### 3.5 Gate / Warning screen
- **Purpose:** stop or warn when a rule fails, clearly.
- **Shows:** what's wrong in plain language (e.g. "This product isn't on the approved list" / "Harvest locked — 4 days left in the waiting period"), why it matters, what to do, who to contact.
- **Actions:** for hard gates → cannot proceed (back / pick alternative); for soft flags → proceed-with-note (logged for manager review).
- **States:** hard block vs soft warning must look different (red stop vs amber caution).
- **Notes:** never a dead end — always offer a next step. Uses on-device rules + reference data (works offline).

### 3.6 Plot map / Board
- **Purpose:** spatial view of the coop's plots as tiles.
- **Shows:** plots as colored tiles/pins by status (tasks due / healthy / flagged / locked); current GPS position.
- **Actions:** tap plot → its tasks + recent logs; start a task for this plot.
- **States:** GPS off; map tiles offline (cache); plot boundaries fuzzy (allow manual plot select as fallback — plot identity matters for rules).
- **Game:** the "board" — tidy/green plots feel good; flagged plots pull attention.

### 3.7 Success / Confirmation
- **Purpose:** reward the verified capture, reinforce the habit.
- **Shows:** "Logged & Verified ✓", points/streak change, what's next.
- **Actions:** next task; done.
- **Game:** brief celebratory animation, streak increment, occasional badge unlocks.

### 3.8 My Progress / Profile
- **Purpose:** personal engagement.
- **Shows:** current streak, tasks this week/season, badges, personal completion rate.
- **Actions:** view badge details.
- **Notes:** keep comparison personal (self vs past), not ranked against peers, to avoid fake-for-rank behavior.

### 3.9 Sync / Offline queue
- **Purpose:** trust that queued work is safe and will upload.
- **Shows:** pending captures (with thumbnails), last sync time, storage used, conflicts.
- **Actions:** manual sync; retry failed; view queued item.
- **States:** syncing, failed, stale reference data warning ("your approved lists are 12 days old — sync soon").
- **Notes:** this view is a trust anchor for offline work — make it reassuring and honest.

### 3.10 Notifications / Reminders
- **Purpose:** surface due routines, overdue tasks, resolved gates ("harvest now unlocked on A3").
- **Shows:** time-ordered nudges.
- **Actions:** tap → relevant task/plot.
- **Game:** streak-protection nudges ("log today to keep your streak").

### 3.11 My History / Records (read-only)
- **Purpose:** let a worker see what they've logged.
- **Shows:** past logs with Verified ✓, photo thumbnail, plot, date.
- **Actions:** view a log; filter by plot/date.
- **Notes:** read-only — logs are immutable once captured (integrity).

---

## 4. Cross-cutting requirements
- **Offline-first:** capture, gate rules, reference data, plot list, identities all work with zero signal; queue + sync later.
- **Provenance integrity:** live-camera only, silent GPS/time/user stamps, immutable logs.
- **Localization:** Vietnamese first; icon-supported; low-literacy copy.
- **Accessibility:** large targets, high contrast for sunlight, minimal typing.
- **Performance:** must run on low-end Android.

---

## 5. Open design questions (flagging, not solving)
- How to handle **shared devices** without weakening the "who" (fast switch vs integrity).
- **GPS-off / fuzzy plots:** fallback plot selection vs provenance strength.
- How visible to make **points/streaks** without tipping into fake-for-reward — err toward personal, verified-only rewards.
