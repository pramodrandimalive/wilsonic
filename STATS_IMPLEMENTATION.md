# Stats Engine Implementation - Complete Documentation

## Overview

The `backend/stats.py` module implements all statistical analysis for Wilsonic, exactly following Section 5 of the project brief. The logic has been validated against 300,000 historical draws.

## Implementation Status: ✓ COMPLETE

All five sections implemented and tested:
- ✓ 5.1 Base Frequency Estimator
- ✓ 5.2 Ranking
- ✓ 5.3 Wilson Score Confidence Interval
- ✓ 5.4 Rolling Window (Recent Frequency)
- ✓ 5.5 Drift Detection
- ✓ 5.6 Excluded Logic (verified NOT implemented)

## Functions Overview

### Section 5.1: Base Frequency Estimator

```python
calculate_base_frequency(db: Session) -> Dict[str, float]
```
Calculates `p_hat(L) = count(L) / total_draws` for all 7 letters from full history.

**Returns:** `{"A": 0.382, "B": 0.211, ...}`

**Helper functions:**
- `get_total_draws(db)` - Total count of draws
- `get_letter_counts(db)` - Raw counts per letter

### Section 5.2: Ranking

```python
get_ranking(db: Session) -> List[Dict]
```
Returns all letters ranked by frequency (descending) with confidence intervals.

**Returns:**
```python
[
    {
        "letter": "A",
        "p_hat": 0.382,
        "rank": 1,
        "count": 38200,
        "lower_bound": 0.379,
        "upper_bound": 0.385
    },
    ...
]
```

### Section 5.3: Wilson Score Confidence Interval

```python
calculate_wilson_interval(p: float, n: int, z: float = 1.96) -> Tuple[float, float]
```
Computes 95% Wilson confidence interval using the exact formula from the brief:

```
z = 1.96
denominator = 1 + z²/n
center = (p + z²/(2n)) / denominator
margin = z * sqrt((p*(1-p)/n) + z²/(4n²)) / denominator
lower_bound = center - margin
upper_bound = center + margin
```

**Returns:** `(lower_bound, upper_bound)`

### Section 5.4: Rolling Window

```python
calculate_rolling_frequency(db: Session, window_size: int = 5000) -> Dict[str, float]
```
Calculates `p_hat_recent(L) = count(L in last N draws) / N`

**Parameters:**
- `window_size`: Number of recent draws to analyze (default: 5000, configurable)

**Returns:** `{"A": 0.385, "B": 0.215, ...}`

**Helper functions:**
- `get_rolling_window_size(db, requested_size)` - Actual window size (capped at total draws)

### Section 5.5: Drift Detection

```python
detect_drift(db: Session, window_size: int = 5000, reset_tracker: bool = False) -> Dict[str, Dict]
```
Detects if recent frequency has drifted outside historical confidence interval.

**Key Logic:**
- Compares `p_hat_recent(L)` to Wilson CI `[lower_bound, upper_bound]`
- Flags drift ONLY after **10+ consecutive violations** (not just once)
- Tracks consecutive violations in memory
- Resets counter when frequency returns to normal range

**Returns:**
```python
{
    "A": {
        "drift_detected": False,
        "p_hat_recent": 0.385,
        "p_hat_historical": 0.382,
        "lower_bound": 0.379,
        "upper_bound": 0.385,
        "consecutive_violations": 0,
        "outside_interval": False
    },
    ...
}
```

**Helper functions:**
- `get_drift_summary(db, window_size)` - High-level summary of drift status
- `reset_drift_tracker()` - Reset violation counters

### Section 5.6: Excluded Logic

**The following are INTENTIONALLY NOT IMPLEMENTED:**
- Gap-since-last-occurrence tracking
- "Overdue" letter scoring
- Hazard-rate-based "due" predictions
- Time-weighted predictions

These approaches were tested and disproven - they perform worse than simple frequency ranking.

## Constants

```python
VALID_LETTERS = ["A", "B", "C", "D", "E", "F", "G"]
Z_SCORE_95 = 1.96                    # 95% confidence interval
DEFAULT_WINDOW_SIZE = 5000           # Rolling window default
DRIFT_THRESHOLD_CONSECUTIVE = 10     # Violations needed to flag drift
```

## Testing

### Comprehensive Test Suite

Run: `python -m backend.test_stats`

Tests all five sections with assertions:
- ✓ Base frequency with empty DB and known distributions
- ✓ Wilson intervals with various sample sizes and edge cases
- ✓ Ranking order and structure validation
- ✓ Rolling window capturing recent patterns vs historical
- ✓ Drift detection with consecutive violation threshold
- ✓ Verification that excluded logic is NOT present

**All tests passing:** ✓

### Usage Examples

Run: `python -m backend.example_stats_usage`

Demonstrates:
1. Basic frequency statistics
2. Letter ranking with confidence intervals
3. Rolling window comparison (recent vs historical)
4. Drift detection
5. Complete workflow for API endpoint

## Performance Notes

- All database queries are optimized with SQLAlchemy ORM
- Drift tracking uses in-memory dictionary (fast, simple for MVP)
- Functions are stateless except for drift tracker (can be reset)
- Window size configurable for different analysis needs

## Integration with API

Functions are ready for integration in `backend/api/routes.py`:

| Endpoint | Function(s) |
|---|---|
| `GET /stats/ranking` | `get_ranking(db)` |
| `GET /stats/drift` | `detect_drift(db)` or `get_drift_summary(db)` |
| `GET /stats/summary` | `get_total_draws(db)`, `get_letter_counts(db)` |

## Mathematical Accuracy

Wilson confidence interval implementation matches the exact formula from the project brief:
- Z-score: 1.96 (95% two-tailed)
- Handles edge cases: p=0, p=1, n=0
- Results validated against statistical references
- Wider intervals for small samples (correct behavior)

## Drift Detection Algorithm

```
For each letter L:
    1. Get p_hat_recent(L) from last N draws
    2. Get Wilson CI [lower, upper] from full history
    3. If p_hat_recent is outside [lower, upper]:
         consecutive_violations++
       Else:
         consecutive_violations = 0
    4. If consecutive_violations >= 10:
         drift_detected = True
```

This prevents false alarms from normal statistical noise.

## Code Quality

- ✓ All functions independently testable
- ✓ Type hints for parameters and returns
- ✓ Comprehensive docstrings with examples
- ✓ Clear variable names matching brief notation
- ✓ No magic numbers (all constants defined)
- ✓ Proper error handling (empty DB, edge cases)
- ✓ Comments explaining formulas and thresholds

## Next Steps (Phase 1)

The stats engine is complete and ready for:
1. API endpoint integration (`backend/api/routes.py`)
2. FastAPI app setup (`backend/main.py`)
3. Frontend dashboard integration

## Files Created

| File | Purpose | Status |
|---|---|---|
| `backend/stats.py` | Core stats engine | ✓ Complete |
| `backend/test_stats.py` | Comprehensive test suite | ✓ Complete |
| `backend/example_stats_usage.py` | Usage examples | ✓ Complete |
| `STATS_IMPLEMENTATION.md` | This documentation | ✓ Complete |

---

**Implementation Date:** 2026-08-15  
**Validated Against:** 300k historical draws (per project brief)  
**Status:** Ready for API integration
