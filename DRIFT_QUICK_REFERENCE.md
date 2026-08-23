# Enhanced Drift Detection - Quick Reference

## Usage

### Frontend (User)
1. Open the Wilsonic dashboard
2. Find "Analysis Window" dropdown below the drift indicator
3. Select window size:
   - **100-500 draws**: Very sensitive, reacts fast to changes
   - **1,000-5,000 draws**: Balanced (5000 is default)
   - **10,000-50,000 draws**: More stable, filters noise
   - **100,000 draws**: Most stable (requires 300k+ total draws)
4. Dashboard updates automatically when window changes

### API (Developer)
```bash
# Use default window (5000)
curl http://localhost:8000/stats/drift

# Use custom window
curl http://localhost:8000/stats/drift?window_size=1000

# Test various windows
curl http://localhost:8000/stats/drift?window_size=100
curl http://localhost:8000/stats/drift?window_size=50000
```

### Response Format
```json
{
  "any_drift_detected": false,
  "drifted_letters": [],
  "letters_at_risk": ["E"],
  "window_size": 1000,
  "total_draws": 299882,
  "drift_status": {
    "A": {
      "drift_detected": false,
      "p_hat_recent": 0.384,
      "p_hat_historical": 0.382,
      "z_score": 0.069,
      "consecutive_violations": 0,
      "outside_interval": false
    },
    "E": {
      "z_score": 2.033,
      "outside_interval": true
    }
  }
}
```

## Interpreting Z-Scores

- **|z| < 1.96**: Normal variation, no concern
- **|z| = 1.96-2.58**: Marginally significant (monitor)
- **|z| = 2.58-3.29**: Significant deviation (investigate)
- **|z| > 3.29**: Highly significant (action needed)

## Window Size Guide

| Window | Use Case | Sensitivity | False Positives |
|--------|----------|-------------|-----------------|
| 100 | Quick alerts | Very High | High |
| 500 | Recent trends | High | Medium-High |
| 1,000 | Short-term monitoring | High | Medium |
| 5,000 | **Default (recommended)** | Medium | Low |
| 10,000 | Medium-term trends | Medium-Low | Very Low |
| 50,000 | Long-term stability | Low | Minimal |
| 100,000 | Historical analysis | Very Low | Negligible |

## Drift Detection Logic

1. **Calculate z-score** for each letter comparing recent vs historical frequency
2. **Check threshold**: If |z| > 1.96, mark as "outside interval"
3. **Track consecutive violations**: Count how many times in a row
4. **Flag drift**: Only after 10+ consecutive violations

This two-stage approach prevents false alarms from natural statistical noise.

## Examples

### Example 1: Small Window (Sensitive)
```
Window: 1000 draws
Letter E: z=2.033, outside_interval=true
Status: Monitoring (not yet flagged, need 10+ consecutive)
```

### Example 2: Default Window (Balanced)
```
Window: 5000 draws
Letter A: z=-2.214, outside_interval=true
Letter C: z=2.697, outside_interval=true
Status: Both showing potential drift
```

### Example 3: Large Window (Stable)
```
Window: 50000 draws
All z-scores < 1.5
Status: All clear, stable distribution
```

### Example 4: Insufficient Data
```
Window: 100000 draws
Total draws: 299882 (need 300000)
Status: "Drift detection requires at least 300,000 draws"
```

## Testing

Run comprehensive tests:
```bash
cd /Users/pramodrandima/Documents/Projects/wilsonic
source venv/bin/activate
python -m backend.test_enhanced_drift
```

Expected output:
- ✓ All z-test calculations correct
- ✓ All window sizes working
- ✓ Edge cases handled
- ✓ Dynamic thresholds working

## Quick Verification

```bash
# Test small window
curl -s 'http://localhost:8000/stats/drift?window_size=100' | python3 -m json.tool

# Test default window
curl -s 'http://localhost:8000/stats/drift' | python3 -m json.tool

# Test large window
curl -s 'http://localhost:8000/stats/drift?window_size=50000' | python3 -m json.tool
```

---
**Documentation**: Sunday, August 16, 2026  
**Status**: Production Ready ✅
