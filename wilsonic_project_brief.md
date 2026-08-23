# Wilsonic — Project Brief

## 1. What this project is

A prediction *indicator* system for a lottery-style game: one of seven letters (A–G) is drawn every 3 minutes. The system tracks historical draws and surfaces which letter is statistically most likely to appear next, based on running frequency — not a guarantee, an indicator.

**Core finding from data analysis (300,000 historical draws already analyzed):**
- Letters are NOT equally likely. Stable observed frequencies: A≈38.2%, B≈21.1%, C≈13.4%, D≈12.1%, E≈11.0%, F≈3.6%, G≈0.7%.
- The draw process is memoryless (confirmed via hazard-rate analysis and backtesting). "Letter X hasn't appeared in a while so it's due" is **false** and must NOT be implemented — backtested and it performs worse than the flat frequency model.
- Best-performing strategy in backtesting: simple running frequency ranking (~38% accuracy vs ~14% for random guessing). No rolling-window or gap-based variant beat it.

## 2. Tech stack

- **Backend:** Python (FastAPI)
- **Database:** SQLite to start (simple, file-based, no server setup). Structure it so migration to PostgreSQL later is easy (use SQLAlchemy ORM).
- **Frontend:** React (dashboard)
- **Repo structure:** Monorepo (single repo, frontend/backend folders)
- **Hosting (later phase):** Railway or Render — not needed for local MVP build

## 3. Repo structure

```
wilsonic/
├── backend/
│   ├── main.py                 → FastAPI app entrypoint
│   ├── database.py             → SQLAlchemy engine/session setup
│   ├── models.py                → Draw table model
│   ├── stats.py                  → all statistics logic (see section 5)
│   ├── api/
│   │   └── routes.py            → API endpoints (see section 6)
│   └── scraper/                  → placeholder folder, empty for now (Phase 2)
├── frontend/
│   └── (React app — dashboard)
├── requirements.txt
└── README.md
```

## 4. Database schema

**Table: `draws`**

| Column | Type | Notes |
|---|---|---|
| id | Integer, primary key, autoincrement | |
| letter | String(1) | One of A, B, C, D, E, F, G |
| timestamp | DateTime | When the draw happened (default: now) |
| source | String | `"manual"` or `"scraper"` (Phase 2) — track entry origin |

## 5. Stats engine logic (`stats.py`)

This is the core logic, already validated against 300k historical records. Implement exactly this — do not add gap/"time since last occurrence" logic.

### 5.1 Base frequency estimator
```
p_hat(L) = count(L) / total_draws
```
Computed for all 7 letters from full history.

### 5.2 Ranking
Sort all 7 letters by `p_hat(L)` descending. Output as a list of `{letter, p_hat, rank}`.

### 5.3 Wilson score confidence interval
For each letter, compute the 95% Wilson confidence interval around `p_hat(L)`:

```
z = 1.96
n = total_draws
p = p_hat(L)

denominator = 1 + z²/n
center = (p + z²/(2n)) / denominator
margin = z * sqrt((p*(1-p)/n) + z²/(4n²)) / denominator

lower_bound = center - margin
upper_bound = center + margin
```

Return `{lower_bound, upper_bound}` alongside each letter's ranking entry.

### 5.4 Rolling window (recent frequency)
```
p_hat_recent(L) = count(L in last N draws) / N
```
Default `N = 5000`. Make this configurable (query param or config value).

### 5.5 Drift detection
For each letter, compare `p_hat_recent(L)` to the full-history confidence interval `[lower_bound, upper_bound]` from 5.3.

- If `p_hat_recent(L)` falls outside that interval for **10+ consecutive checks** (not just once — avoid false alarms from noise), flag `drift_detected: true` for that letter.
- Otherwise `drift_detected: false`.
- This runs in the background / on each stats refresh, not as a separate manual action.

### 5.6 Explicitly excluded logic
Do not implement: gap-since-last-occurrence, "overdue" scoring, or any hazard-rate-based "due" prediction. These were tested and disproven — including them would be a regression, not a feature.

## 6. API endpoints (`api/routes.py`)

| Endpoint | Method | Purpose |
|---|---|---|
| `/draws` | POST | Manual entry: submit a new draw `{letter, timestamp?}` |
| `/draws` | GET | List recent draws (paginated, for history table) |
| `/stats/ranking` | GET | Current ranked letter list with `p_hat` + confidence intervals |
| `/stats/drift` | GET | Drift status per letter |
| `/stats/summary` | GET | Total draws, per-letter counts, last updated time |

## 7. Frontend (dashboard) requirements

- **Ranked list view** — all 7 letters, sorted by probability, showing `p_hat` as a percentage and the confidence interval as a range (e.g. "A — 38.2% (37.5%–38.9%)")
- **Manual entry form** — a simple letter picker (7 buttons, A–G) + "Add Draw" button. On submit, calls `POST /draws` and refreshes the ranking.
- **History table** — recent draws with timestamp and letter, most recent first
- **Drift indicator** — a visible badge/alert if any letter currently has `drift_detected: true`
- No login/auth needed for MVP (single user)

## 8. Build phases

**Phase 1 (this brief, build now):**
1. Database schema + SQLAlchemy models
2. Stats engine (`stats.py`) — sections 5.1–5.5
3. API endpoints — section 6
4. Manual entry form + dashboard — section 7
5. Wire frontend to backend, test end-to-end with manually entered draws

**Phase 2 (later, not now):**
6. Scraper module — pulls draws automatically from a target website (site TBD)
7. Scheduler — runs scraper every 3 minutes, writes to `draws` table with `source="scraper"`
8. Keep manual entry as a fallback/backup input method even after scraper ships

**Phase 3 (later):**
9. Deployment to Railway/Render, hosting finalization

## 9. Explicit non-goals

- No guarantee-of-win claims anywhere in the UI or docs — this is an indicator, not a prediction oracle
- No gap/"due" logic (see 5.6)
- No auth/multi-user support in MVP
- No PostgreSQL migration yet — SQLite is sufficient for MVP scale
