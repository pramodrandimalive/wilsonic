# Wilsonic

A prediction indicator system for a lottery-style game where one of seven letters (A–G) is drawn every 3 minutes. The system tracks historical draws and surfaces which letter is statistically most likely to appear next based on running frequency.

## Status: ✓ PHASE 1 MVP COMPLETE

All Phase 1 components built, tested, and functional:
- ✓ Database layer (SQLAlchemy + SQLite)
- ✓ Stats engine (frequency analysis, Wilson CIs, drift detection)
- ✓ API endpoints (all 5 from specification)
- ✓ React dashboard (ranked list, manual entry, history, drift indicator)

**Access the system:**
- **Frontend**: http://localhost:3000
- **Backend API**: http://localhost:8000
- **API Docs**: http://localhost:8000/docs

## Overview

**This is an indicator system, not a prediction oracle.** Letters are NOT equally likely in the observed data (A≈38.2%, B≈21.1%, C≈13.4%, D≈12.1%, E≈11.0%, F≈3.6%, G≈0.7%), and the system uses simple frequency analysis validated against 300,000 historical draws.

## Tech Stack

- **Backend:** Python (FastAPI) ✓
- **Database:** SQLite (with SQLAlchemy ORM) ✓
- **Frontend:** React 18 + Vite ✓
- **Hosting:** Railway or Render (Phase 3)

## Project Structure

```
wilsonic/
├── backend/
│   ├── main.py                 → FastAPI app entrypoint
│   ├── database.py             → SQLAlchemy engine/session setup ✓
│   ├── models.py               → Draw table model ✓
│   ├── stats.py                → Statistics logic (Phase 1)
│   ├── api/
│   │   └── routes.py           → API endpoints (Phase 1)
│   └── scraper/                → Automated scraper (Phase 2)
├── frontend/                   → React dashboard (Phase 1)
├── requirements.txt            ✓
└── README.md                   ✓
```

## Quick Start

### 1. Start Backend
```bash
# Activate virtual environment
source venv/bin/activate

# Start FastAPI server
uvicorn backend.main:app --reload
```
Server will be available at: http://localhost:8000

### 2. Start Frontend
```bash
# In a new terminal
cd frontend
npm run dev
```
Dashboard will be available at: http://localhost:3000

### 3. Use the System
- Open http://localhost:3000 in your browser
- View letter ranking and statistics
- Submit draws manually using the letter buttons
- Watch the history table and drift indicator

## Features

### Backend (FastAPI + SQLite)
- **Stats Engine**: Base frequency, Wilson confidence intervals, rolling windows, drift detection
- **API Endpoints**: 5 RESTful endpoints for ranking, draws, drift, and summary
- **Database**: SQLite with SQLAlchemy ORM (easy PostgreSQL migration)
- **No gap-based logic**: Memoryless approach validated against 300k draws

### Frontend (React + Vite)
- **Ranked List**: All 7 letters with percentages and 95% CI ranges
- **Manual Entry**: 7 letter buttons + Add Draw (calls API)
- **History Table**: Last 10 draws with timestamps (most recent first)
- **Drift Indicator**: Visual badge showing drift detection status
- **Auto-refresh**: Updates every 30 seconds

## Setup

### Backend Setup

1. **Install dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

2. **Initialize the database:**
   Database will be created automatically when the app starts.

3. **Run tests:**
   ```bash
   python -m backend.test_db_setup
   python -m backend.test_stats
   python -m backend.test_api
   ```

### Frontend Setup

1. **Install dependencies:**
   ```bash
   cd frontend
   npm install
   ```

2. **Start development server:**
   ```bash
   npm run dev
   ```

3. **Build for production:**
   ```bash
   npm run build
   ```

## Database Schema

### `draws` Table

| Column | Type | Notes |
|---|---|---|
| id | Integer, primary key, autoincrement | |
| letter | String(1) | One of A, B, C, D, E, F, G |
| timestamp | DateTime | When the draw happened (default: now) |
| source | String | `"manual"` or `"scraper"` — tracks entry origin |

## Build Phases

### ✓ Phase 1 (Complete)
1. ✓ Database schema + SQLAlchemy models
2. ✓ Stats engine (`stats.py`) — sections 5.1–5.5
3. ✓ API endpoints — section 6
4. ✓ Manual entry form + dashboard — section 7
5. ✓ Wire frontend to backend
6. ✓ Test end-to-end with manually entered draws

**Status**: All Phase 1 components complete and tested. System is fully functional.

### Phase 2 (Later, not now)
6. Scraper module — pulls draws automatically from target website
7. Scheduler — runs scraper every 3 minutes, writes to `draws` table with `source="scraper"`
8. Keep manual entry as a fallback/backup input method even after scraper ships

### Phase 3 (Later)
9. Deployment to Railway/Render, hosting finalization

## Key Features (Implemented)

- **Frequency-based ranking** — letters ranked by observed probability ✓
- **Wilson confidence intervals** — statistical confidence bounds for each letter ✓
- **Drift detection** — alerts when recent frequency diverges from historical baseline ✓
- **Manual entry** — simple form to record draws ✓
- **History table** — recent draws with timestamps ✓
- **Auto-refresh** — dashboard updates every 30 seconds ✓
- **No "overdue" logic** — the draw process is memoryless (validated via backtesting) ✓

## Development Notes

- Database uses SQLite stored at `backend/wilsonic.db`
- SQLAlchemy ORM makes PostgreSQL migration straightforward when needed
- No authentication in MVP (single user)
- Stats engine logic validated against 300k historical draws

---

For detailed specifications, see `wilsonic_project_brief.md`.
