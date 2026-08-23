# Wilsonic - Quick Start Guide

## System is Ready! ✓

Both backend and frontend servers are currently running.

## Access the System

### Dashboard (Frontend)
**URL:** http://localhost:3000

Open in your browser to see:
- Letter ranking with percentages and confidence intervals
- Manual entry form (7 letter buttons)
- Recent draws history
- Drift detection indicator

### API Documentation
**URL:** http://localhost:8000/docs

Interactive Swagger UI where you can:
- Test all API endpoints
- See request/response schemas
- Try live API calls

### API Health Check
**URL:** http://localhost:8000/health

Quick status check showing:
- System health
- Database connection
- Total draws count

## How to Use

### Submit a Draw
1. Open http://localhost:3000
2. Click one of the 7 letter buttons (A-G)
3. Click "Add Draw"
4. See success message
5. Watch the ranking and history update automatically

### View Statistics
- **Ranking**: See all 7 letters sorted by probability
- **History**: View last 10 draws with timestamps
- **Drift**: Check if recent patterns differ from historical

### Auto-Refresh
The dashboard automatically refreshes every 30 seconds to show the latest data.

## Server Commands

### Stop Servers
If you need to stop the servers:

**Backend:**
- Go to the terminal running uvicorn
- Press `Ctrl+C`

**Frontend:**
- Go to the terminal running npm
- Press `Ctrl+C`

### Restart Servers

**Backend:**
```bash
source venv/bin/activate
uvicorn backend.main:app --reload
```

**Frontend:**
```bash
cd frontend
npm run dev
```

## Testing

### Run Backend Tests
```bash
source venv/bin/activate
python -m backend.test_stats
python -m backend.test_api
```

### Try API Demo
```bash
source venv/bin/activate
python -m backend.demo_api
```

## Sample Workflow

1. **View current ranking**
   - Open http://localhost:3000
   - See letter A is most likely (38.2%)

2. **Submit draws**
   - Click letters A, B, C, etc.
   - Click "Add Draw" after each
   - Watch history table update

3. **Check statistics**
   - Ranking updates with new data
   - History shows recent draws
   - Drift indicator shows status

4. **Explore API**
   - Visit http://localhost:8000/docs
   - Try GET /stats/ranking
   - See JSON response

## File Structure

```
wilsonic/
├── backend/          # Python FastAPI backend
│   ├── api/         # API routes
│   ├── database.py  # Database setup
│   ├── models.py    # Data models
│   ├── stats.py     # Statistics engine
│   └── main.py      # FastAPI app
│
├── frontend/         # React dashboard
│   └── src/
│       ├── components/  # UI components
│       └── App.jsx      # Main app
│
└── *.md             # Documentation files
```

## Documentation

All documentation is in the root folder:

- **README.md** - Project overview
- **PHASE1_COMPLETE.md** - Completion summary
- **SETUP_SUMMARY.md** - Initial setup guide
- **STATS_IMPLEMENTATION.md** - Stats API reference
- **API_IMPLEMENTATION.md** - API reference
- **FRONTEND_IMPLEMENTATION.md** - Frontend reference
- **\*_QUICK_REFERENCE.md** - Quick guides

## Troubleshooting

### Backend not responding
```bash
# Check if running
curl http://localhost:8000/health

# If not, restart
source venv/bin/activate
uvicorn backend.main:app --reload
```

### Frontend not loading
```bash
# Check if running
curl http://localhost:3000

# If not, restart
cd frontend
npm run dev
```

### Database issues
```bash
# Test database
source venv/bin/activate
python -m backend.test_db_setup
```

## Next Steps

### Phase 2 (Optional)
- Build automated scraper
- Schedule draws every 3 minutes
- Keep manual entry as backup

### Phase 3 (Optional)
- Deploy to Railway/Render
- Switch to PostgreSQL
- Add production configurations

## Support

Check the documentation files for detailed information:
- `API_QUICK_REFERENCE.md` - API usage examples
- `STATS_QUICK_REFERENCE.md` - Stats functions
- `frontend/README.md` - Frontend details

---

**Status**: ✓ System running and ready to use  
**Dashboard**: http://localhost:3000  
**API**: http://localhost:8000  
**Built**: Saturday, August 15, 2026
