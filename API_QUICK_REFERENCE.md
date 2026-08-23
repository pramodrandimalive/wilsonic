# API Quick Reference

## Starting the Server

```bash
# Activate virtual environment
source venv/bin/activate

# Start server with auto-reload
uvicorn backend.main:app --reload

# Server will be available at: http://localhost:8000
```

## All Endpoints

### 1. POST /draws - Submit a Draw
```bash
# Basic usage (timestamp defaults to now)
curl -X POST http://localhost:8000/draws \
  -H "Content-Type: application/json" \
  -d '{"letter": "A"}'

# With custom timestamp
curl -X POST http://localhost:8000/draws \
  -H "Content-Type: application/json" \
  -d '{"letter": "B", "timestamp": "2026-08-15T15:30:00Z"}'
```

### 2. GET /draws - List Recent Draws
```bash
# Default (page 1, 50 items)
curl http://localhost:8000/draws

# Custom pagination
curl "http://localhost:8000/draws?page=2&page_size=10"
```

### 3. GET /stats/ranking - Letter Ranking
```bash
curl http://localhost:8000/stats/ranking

# Returns all 7 letters with:
# - p_hat (frequency)
# - rank (1-7)
# - count (raw occurrences)
# - lower_bound, upper_bound (95% CI)
```

### 4. GET /stats/drift - Drift Detection
```bash
# Default window (5000 draws)
curl http://localhost:8000/stats/drift

# Custom window size
curl "http://localhost:8000/stats/drift?window_size=1000"
```

### 5. GET /stats/summary - Summary Statistics
```bash
curl http://localhost:8000/stats/summary

# Returns:
# - total_draws
# - letter_counts (raw counts)
# - frequencies (percentages)
# - last_draw info
```

### Bonus: Health Check
```bash
curl http://localhost:8000/health
```

## Using Python requests

```python
import requests

BASE_URL = "http://localhost:8000"

# Submit a draw
response = requests.post(f"{BASE_URL}/draws", json={"letter": "A"})
draw = response.json()
print(f"Created draw #{draw['id']}")

# Get ranking
response = requests.get(f"{BASE_URL}/stats/ranking")
data = response.json()
print(f"Top letter: {data['ranking'][0]['letter']} ({data['ranking'][0]['p_hat']*100:.1f}%)")

# Check for drift
response = requests.get(f"{BASE_URL}/stats/drift")
data = response.json()
if data['any_drift_detected']:
    print(f"⚠ Drift detected in: {', '.join(data['drifted_letters'])}")
else:
    print("✓ All letters within normal range")
```

## Using JavaScript fetch

```javascript
const BASE_URL = 'http://localhost:8000';

// Submit a draw
const response = await fetch(`${BASE_URL}/draws`, {
  method: 'POST',
  headers: { 'Content-Type': 'application/json' },
  body: JSON.stringify({ letter: 'A' })
});
const draw = await response.json();
console.log(`Created draw #${draw.id}`);

// Get ranking
const rankingRes = await fetch(`${BASE_URL}/stats/ranking`);
const ranking = await rankingRes.json();
console.log('Top 3 letters:', ranking.ranking.slice(0, 3));

// Get summary
const summaryRes = await fetch(`${BASE_URL}/stats/summary`);
const summary = await summaryRes.json();
console.log(`Total draws: ${summary.total_draws}`);
```

## Interactive Documentation

### Swagger UI (Try Endpoints)
http://localhost:8000/docs

### ReDoc (Read Documentation)
http://localhost:8000/redoc

## Response Examples

### POST /draws (201 Created)
```json
{
  "id": 10001,
  "letter": "A",
  "timestamp": "2026-08-15T16:00:47.624131",
  "source": "manual"
}
```

### GET /draws (200 OK)
```json
{
  "draws": [
    {"id": 10006, "letter": "A", "timestamp": "2026-08-15T16:00:48.078021", "source": "manual"}
  ],
  "total": 10006,
  "page": 1,
  "page_size": 50,
  "total_pages": 201
}
```

### GET /stats/ranking (200 OK)
```json
{
  "total_draws": 10006,
  "ranking": [
    {
      "letter": "A",
      "p_hat": 0.382171,
      "rank": 1,
      "count": 3824,
      "lower_bound": 0.3727,
      "upper_bound": 0.3917
    }
  ]
}
```

### GET /stats/drift (200 OK)
```json
{
  "any_drift_detected": false,
  "drifted_letters": [],
  "letters_at_risk": [],
  "window_size": 5000,
  "total_draws": 10006,
  "drift_status": {
    "A": {
      "drift_detected": false,
      "p_hat_recent": 0.385,
      "p_hat_historical": 0.382,
      "lower_bound": 0.3727,
      "upper_bound": 0.3917,
      "consecutive_violations": 0,
      "outside_interval": false
    }
  }
}
```

### GET /stats/summary (200 OK)
```json
{
  "total_draws": 10006,
  "letter_counts": {"A": 3824, "B": 2111, "C": 1341, "D": 1210, "E": 1100, "F": 360, "G": 60},
  "frequencies": {"A": 0.382171, "B": 0.210973, ...},
  "last_draw": {"id": 10006, "letter": "A", "timestamp": "2026-08-15T16:00:48.078021", "source": "manual"},
  "last_updated": "2026-08-15T16:00:48.287170Z"
}
```

## Error Responses

### 422 Validation Error (Invalid Letter)
```json
{
  "detail": [
    {
      "type": "value_error",
      "loc": ["body", "letter"],
      "msg": "Value error, Letter must be one of A, B, C, D, E, F, G",
      "input": "Z"
    }
  ]
}
```

### 404 Not Found
```json
{
  "detail": "Not Found"
}
```

### 500 Internal Server Error
```json
{
  "detail": "Failed to create draw: [error message]"
}
```

## Testing

```bash
# Run full test suite
python -m backend.test_api

# Individual tests
curl http://localhost:8000/health  # Should return 200
curl -X POST http://localhost:8000/draws -d '{"letter":"A"}' -H "Content-Type: application/json"  # Should return 201
```

## Common Tasks

### Add Multiple Draws
```bash
for letter in A A B C D E F G; do
  curl -X POST http://localhost:8000/draws \
    -H "Content-Type: application/json" \
    -d "{\"letter\":\"$letter\"}"
  sleep 0.1
done
```

### Get Top 3 Letters
```bash
curl -s http://localhost:8000/stats/ranking | \
  python3 -c "import sys, json; data=json.load(sys.stdin); \
  [print(f\"{e['rank']}. {e['letter']} - {e['p_hat']*100:.1f}%\") for e in data['ranking'][:3]]"
```

### Check Recent Activity
```bash
curl -s "http://localhost:8000/draws?page=1&page_size=5" | \
  python3 -c "import sys, json; data=json.load(sys.stdin); \
  print(f\"Last {len(data['draws'])} draws:\"); \
  [print(f\"  {d['letter']} at {d['timestamp']}\") for d in data['draws']]"
```

## Notes

- All timestamps are UTC
- Letter validation is case-insensitive (lowercase converted to uppercase)
- Pagination is 1-indexed (page 1 is first page)
- Window size for drift must be 100-50000
- CORS enabled for localhost:3000 and localhost:5173

## Documentation

- Full API docs: `API_IMPLEMENTATION.md`
- Stats engine: `STATS_IMPLEMENTATION.md`
- Quick reference: `STATS_QUICK_REFERENCE.md`
