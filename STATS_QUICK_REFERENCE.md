# Stats Engine Quick Reference

## Import
```python
from backend import stats
from backend.database import SessionLocal
```

## Basic Usage

### 1. Get Letter Ranking
```python
db = SessionLocal()
ranking = stats.get_ranking(db)

# Returns list sorted by frequency:
# [
#   {"letter": "A", "p_hat": 0.382, "rank": 1, "count": 38200,
#    "lower_bound": 0.379, "upper_bound": 0.385},
#   ...
# ]

db.close()
```

### 2. Base Frequencies
```python
db = SessionLocal()
frequencies = stats.calculate_base_frequency(db)
# Returns: {"A": 0.382, "B": 0.211, ...}

total = stats.get_total_draws(db)
# Returns: 100000

counts = stats.get_letter_counts(db)
# Returns: {"A": 38200, "B": 21100, ...}

db.close()
```

### 3. Wilson Confidence Interval
```python
# Calculate CI for a proportion
lower, upper = stats.calculate_wilson_interval(p=0.382, n=100000)
# Returns: (0.379, 0.385)

# With custom z-score
lower, upper = stats.calculate_wilson_interval(p=0.382, n=100000, z=2.576)  # 99% CI
```

### 4. Rolling Window (Recent Frequency)
```python
db = SessionLocal()

# Last 5000 draws (default)
recent_freq = stats.calculate_rolling_frequency(db)
# Returns: {"A": 0.385, "B": 0.215, ...}

# Custom window size
recent_freq = stats.calculate_rolling_frequency(db, window_size=1000)

db.close()
```

### 5. Drift Detection
```python
db = SessionLocal()

# Full drift status
drift_status = stats.detect_drift(db, window_size=5000)
# Returns dict with per-letter drift info

# Summary only
summary = stats.get_drift_summary(db, window_size=5000)
# Returns: {
#   "any_drift_detected": False,
#   "drifted_letters": [],
#   "letters_at_risk": [],
#   "window_size": 5000,
#   "total_draws": 100000
# }

# Reset tracking
stats.reset_drift_tracker()

db.close()
```

## Constants

```python
stats.VALID_LETTERS               # ["A", "B", "C", "D", "E", "F", "G"]
stats.Z_SCORE_95                  # 1.96 (for 95% CI)
stats.DEFAULT_WINDOW_SIZE         # 5000
stats.DRIFT_THRESHOLD_CONSECUTIVE # 10 (violations needed)
```

## API Integration Examples

### GET /stats/ranking
```python
from fastapi import Depends
from sqlalchemy.orm import Session
from backend.database import get_db
from backend import stats

@app.get("/stats/ranking")
def get_stats_ranking(db: Session = Depends(get_db)):
    ranking = stats.get_ranking(db)
    total = stats.get_total_draws(db)
    
    return {
        "total_draws": total,
        "ranking": ranking
    }
```

### GET /stats/drift
```python
@app.get("/stats/drift")
def get_drift_status(
    window_size: int = 5000,
    db: Session = Depends(get_db)
):
    return stats.get_drift_summary(db, window_size)
```

### GET /stats/summary
```python
@app.get("/stats/summary")
def get_summary(db: Session = Depends(get_db)):
    return {
        "total_draws": stats.get_total_draws(db),
        "letter_counts": stats.get_letter_counts(db),
        "frequencies": stats.calculate_base_frequency(db)
    }
```

## Testing

```bash
# Run comprehensive test suite
python -m backend.test_stats

# Run usage examples
python -m backend.example_stats_usage
```

## Common Patterns

### Compare Recent vs Historical
```python
db = SessionLocal()

historical = stats.calculate_base_frequency(db)
recent = stats.calculate_rolling_frequency(db, window_size=500)

for letter in stats.VALID_LETTERS:
    hist_pct = historical[letter] * 100
    recent_pct = recent[letter] * 100
    change = recent_pct - hist_pct
    print(f"{letter}: {change:+.1f}%")

db.close()
```

### Check for Any Drift
```python
db = SessionLocal()
summary = stats.get_drift_summary(db)

if summary["any_drift_detected"]:
    print(f"⚠ Drift detected in: {', '.join(summary['drifted_letters'])}")
else:
    print("✓ All letters within normal range")

db.close()
```

### Get Top 3 Letters
```python
db = SessionLocal()
ranking = stats.get_ranking(db)

top_3 = ranking[:3]
for entry in top_3:
    print(f"{entry['rank']}. {entry['letter']} - {entry['p_hat']*100:.1f}%")

db.close()
```

## Notes

- All functions require a database session
- Functions are stateless except drift tracker (can be reset)
- Wilson CIs automatically handle edge cases (p=0, p=1, n=0)
- Drift detection needs 10+ consecutive violations to flag
- Window size is configurable (default: 5000)
- No gap-based or "overdue" logic implemented (intentional)

## Documentation

- Full API reference: `STATS_IMPLEMENTATION.md`
- Test suite: `backend/test_stats.py`
- Usage examples: `backend/example_stats_usage.py`
- Build summary: `STATS_BUILD_SUMMARY.md`
