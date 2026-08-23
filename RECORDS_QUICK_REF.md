# Records Management Feature - Quick Reference

## Backend API

### PUT /draws/{id}
Update a draw's letter and/or timestamp.

```bash
curl -X PUT 'http://localhost:8000/draws/{id}' \
  -H 'Content-Type: application/json' \
  -d '{"letter": "B", "timestamp": "2026-08-15T16:00:00Z"}'
```

### DELETE /draws/{id}
Delete a draw by ID.

```bash
curl -X DELETE 'http://localhost:8000/draws/{id}'
```

### GET /draws (Enhanced)
List draws with filters.

**Query Parameters:**
- `page` (int): Page number (default: 1)
- `page_size` (int): Items per page (default: 50, max: 500)
- `letter` (string): Filter by A-G
- `source` (string): Filter by manual/historical_import/scraper
- `sort` (string): "newest" (default) or "oldest"

```bash
curl 'http://localhost:8000/draws?page=1&page_size=25&letter=A&source=manual&sort=newest'
```

---

## Frontend

### Navigation
- Dashboard → Click "Manage Records" button
- Records Page → Click "← Back to Dashboard" link

### URL Routes
- `/` - Dashboard
- `/records` - Records Management

### Features
1. **Filters**: Letter, Source, Sort Order, Page Size
2. **Inline Editing**: Click "Edit" → Change values → "Save" or "Cancel"
3. **Delete**: Click "Delete" → Confirm dialog
4. **Pagination**: Previous/Next buttons, page indicator

---

## Key Files

### Backend
- `backend/api/routes.py` - API endpoints
  - `DrawUpdate` model
  - `update_draw()` function
  - `delete_draw()` function
  - Enhanced `list_draws()` function

### Frontend
- `frontend/src/App.jsx` - Router wrapper
- `frontend/src/pages/Dashboard.jsx` - Main dashboard
- `frontend/src/pages/RecordsManagement.jsx` - Records page
- `frontend/src/pages/RecordsManagement.css` - Records styling

---

## Warning

⚠️ **Editing or deleting records permanently affects all statistics:**
- Letter frequencies
- Rankings
- Drift detection
- Confidence intervals

Always backup data before bulk changes.

---

## Testing

```bash
# Backend server
cd /path/to/wilsonic
source venv/bin/activate
uvicorn backend.main:app --reload

# Frontend server
cd /path/to/wilsonic/frontend
npm run dev

# Open browser
http://localhost:3000/         # Dashboard
http://localhost:3000/records  # Records Management
```

---

## Quick Stats Check

After editing/deleting records, verify statistics:

```bash
# Check ranking
curl http://localhost:8000/stats/ranking | jq '.ranking[] | {letter, p_hat, count}'

# Check drift
curl 'http://localhost:8000/stats/drift?window_size=5000' | jq '{any_drift_detected, drifted_letters}'

# Check total draws
curl http://localhost:8000/stats/summary | jq '{total_draws, letter_counts}'
```
