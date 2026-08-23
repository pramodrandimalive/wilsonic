# Rolling Frequency Trend Chart - Implementation Summary

## Overview

Added an interactive Rolling Frequency Trend chart to visualize how letter frequencies have evolved over the entire dataset history. The chart is **hidden by default** with a toggle switch to show/hide it, avoiding unnecessary data fetching when not in use.

---

## Backend Implementation

### New Endpoint: `GET /stats/rolling-trend`

**Location:** `backend/api/routes.py`

**Query Parameters:**
- `window_size` (int, default: 5000): Rolling window size for each calculation
- `interval` (int, default: 500): Number of draws between each data point

**Response:**
```json
{
  "data_points": [
    {
      "position": 5000,
      "draw_id": 12345,
      "timestamp": "2026-08-15T10:30:00Z",
      "freq_A": 38.2,
      "freq_B": 21.1,
      "freq_C": 13.4,
      "freq_D": 12.1,
      "freq_E": 11.0,
      "freq_F": 3.6,
      "freq_G": 0.7
    },
    ...
  ],
  "baseline_frequencies": {
    "A": 38.2,
    "B": 21.1,
    ...
  },
  "total_draws": 299890,
  "window_size": 5000,
  "interval": 500
}
```

**How it works:**
1. Starts at position `window_size` (first point where we have enough data)
2. At each `interval`, gets the most recent `window_size` draws
3. Calculates frequency (%) for each letter in that window
4. Returns all data points + baseline frequencies for reference lines

---

## Frontend Implementation

### Component: `RollingFrequencyChart.jsx`

**Location:** `frontend/src/components/RollingFrequencyChart.jsx`

**Key Features:**

#### 1. **Interactive Legend Controls**
- Click any letter to **isolate** it (hides all others)
- Click isolated letter again to **show all**
- "Show All" / "Hide All" button for quick toggle
- Each letter has its own color-coded button

#### 2. **Baseline Reference Lines**
- Toggle checkbox to show/hide baseline (full-history p_hat)
- Dashed lines show historical average for each letter
- Only visible for currently shown letters
- Helps compare recent trend vs historical baseline

#### 3. **Color Coding** (matches ranking cards)
```javascript
A: #4CAF50  // Green
B: #2196F3  // Blue
C: #FF9800  // Orange
D: #9C27B0  // Purple
E: #F44336  // Red
F: #00BCD4  // Cyan
G: #FFC107  // Amber
```

#### 4. **Responsive Tooltip**
- Shows draw position
- Lists frequency for all visible letters
- Color-coded for easy identification

#### 5. **Disclaimer**
Blue banner at bottom:
> "Shows recent frequency vs historical baseline over time. This is not a predictive pattern — draws are statistically independent, so chart shapes don't forecast future draws."

---

### Dashboard Integration

**Location:** `frontend/src/pages/Dashboard.jsx`

**Toggle Switch:**
- Located between Letter Trend Cards and main content
- Default state: **OFF** (chart hidden)
- Modern iOS-style toggle switch
- Label: "Show Rolling Frequency Trend Chart"

**Data Fetching:**
- Only fetches trend data when toggle is **ON**
- Re-fetches when window size changes
- Re-fetches after manual draw submission
- Chart is **completely unmounted** when OFF (no wasted renders)

**State Management:**
- `showTrendChart`: boolean (toggle state)
- `trendData`: trend data object
- `trendLoading`: loading state for trend data
- State persists during session (resets on page reload)

---

## Usage Guide

### Basic Usage
1. Open dashboard at `http://localhost:3001/`
2. Toggle "Show Rolling Frequency Trend Chart" to **ON**
3. Wait for data to load (~1-2 seconds)
4. Chart appears with all 7 letters visible

### Isolate a Single Letter
1. Click any letter button in the controls (e.g., "A")
2. Only letter A's line is shown
3. Click "A" again to show all letters

### Show Baselines
1. Check "Show Baselines" checkbox
2. Dashed reference lines appear for each visible letter
3. Compares recent trend against historical average

### Change Window Size
1. Adjust "Analysis Window" selector at top
2. Chart automatically re-fetches with new window size
3. More responsive with smaller windows (100-1000)
4. More stable with larger windows (10000-100000)

### Hide Chart
1. Toggle "Show Rolling Frequency Trend Chart" to **OFF**
2. Chart unmounts immediately
3. Dashboard remains fast without trend data overhead

---

## Technical Details

### Performance Optimizations

1. **Conditional Rendering**
   - Chart only mounts when `showTrendChart === true`
   - No data fetching when chart is hidden
   - Recharts bundle only loaded when needed

2. **Data Sampling**
   - `interval` parameter controls data point density
   - Default 500 draws = ~600 points for 300K dataset
   - Adjust for performance vs granularity tradeoff

3. **Rolling Window Calculation**
   - Uses SQLAlchemy offset/limit for efficient queries
   - Calculates frequencies on the fly
   - No caching (always fresh data)

### Chart Configuration

**Recharts Components Used:**
- `LineChart`: Main container
- `Line`: One per letter (7 total)
- `XAxis`: Draw position
- `YAxis`: Frequency %
- `CartesianGrid`: Background grid
- `Tooltip`: Hover info
- `Legend`: Letter toggles (clickable)
- `ReferenceLine`: Baseline dashed lines
- `ResponsiveContainer`: Auto-sizing

**Chart Settings:**
- Height: 400px
- Lines: 2px width (3px when isolated)
- Dots: Hidden (show on hover only)
- Animation: Smooth transitions
- Grid: 3px dash pattern

---

## Styling

### RollingFrequencyChart.css

**Key Styles:**
- White card with shadow
- Blue-themed controls
- Letter toggle buttons match line colors
- Tooltip: white with blue border
- Disclaimer: light blue banner
- Dark mode support included
- Mobile responsive (stacks controls)

**Toggle Switch (Dashboard.css):**
- iOS-style toggle (52x28px)
- Green when ON (#4CAF50)
- Gray when OFF (#ccc)
- White slider ball with shadow
- Smooth 0.3s transitions

---

## API Examples

### Get Default Trend Data
```bash
curl 'http://localhost:8000/stats/rolling-trend'
```

### Custom Window and Interval
```bash
curl 'http://localhost:8000/stats/rolling-trend?window_size=10000&interval=1000'
```

### Fine-grained (smaller interval)
```bash
curl 'http://localhost:8000/stats/rolling-trend?window_size=5000&interval=100'
```

### Coarse-grained (larger interval, faster)
```bash
curl 'http://localhost:8000/stats/rolling-trend?window_size=5000&interval=5000'
```

---

## Dependencies

### New Dependency: recharts
```bash
npm install recharts
```

**Version:** Latest (auto-installed)
**Bundle Size:** ~583 KB minified (note in build output)
**Why Recharts?**
- React-native charts library
- Declarative API
- Responsive by default
- Good performance for 500-1000 data points
- Supports reference lines and interactive legends

---

## File Changes Summary

### Backend
- **Modified:** `backend/api/routes.py`
  - Added `GET /stats/rolling-trend` endpoint

### Frontend
- **New:** `frontend/src/components/RollingFrequencyChart.jsx`
- **New:** `frontend/src/components/RollingFrequencyChart.css`
- **Modified:** `frontend/src/pages/Dashboard.jsx`
  - Added trend chart state
  - Added toggle switch
  - Added conditional rendering
  - Added trend data fetching
- **Modified:** `frontend/src/pages/Dashboard.css`
  - Added toggle switch styles
  - Added trend loading styles
- **Modified:** `frontend/package.json`
  - Added recharts dependency

---

## Behavior Summary

### When Toggle is OFF (Default)
✅ No API calls to `/stats/rolling-trend`  
✅ No chart rendering  
✅ Dashboard loads fast  
✅ Minimal memory usage  

### When Toggle is ON
✅ Fetches trend data once  
✅ Renders chart with all 7 letters  
✅ Interactive controls available  
✅ Re-fetches on window size change  
✅ Re-fetches after manual draw entry  

---

## Example User Flow

1. **User opens dashboard**
   - Chart is hidden
   - Toggle is OFF
   - No trend data fetched

2. **User toggles chart ON**
   - "Loading trend data..." message appears
   - API call to `/stats/rolling-trend`
   - Chart renders with all 7 letters

3. **User clicks "B" button**
   - Only letter B line is visible
   - Blue line stands out (3px width)
   - Other letters hidden

4. **User checks "Show Baselines"**
   - Dashed reference line appears for B
   - Shows historical average: 21.1%
   - Easy to see if recent trend is above/below baseline

5. **User clicks "B" again**
   - All 7 letters visible again
   - Normal 2px line widths

6. **User changes window size to 10000**
   - Chart re-fetches with larger window
   - Trend lines become smoother (less variance)

7. **User toggles chart OFF**
   - Chart unmounts
   - Dashboard returns to normal

---

## Notes

### Statistical Context
- **Not predictive:** Chart shows historical patterns, not future forecasts
- **Independent draws:** Each draw is random and independent
- **Variance is normal:** Fluctuations don't indicate "hot" or "cold" streaks
- **Baseline shows expected:** Dashed lines are long-term averages

### Performance Notes
- 300K draws with interval=500 → ~600 data points
- Recharts handles 500-1000 points smoothly
- Larger intervals (1000-5000) for faster rendering
- Smaller intervals (100-500) for more detail

### Future Enhancements (Not Implemented)
- [ ] Zoom/pan functionality
- [ ] Export chart as PNG
- [ ] Time-based x-axis (timestamps instead of positions)
- [ ] Adjustable interval from UI
- [ ] Multiple window sizes on same chart
- [ ] Anomaly highlighting (drift-detected periods)

---

## Testing Checklist

✅ Backend endpoint returns valid data  
✅ Frontend builds successfully  
✅ Toggle switch works (ON/OFF)  
✅ Chart renders with all 7 letters  
✅ Letter isolation works (click individual letters)  
✅ Show All / Hide All button works  
✅ Baseline toggle shows/hides dashed lines  
✅ Tooltip shows correct data on hover  
✅ Window size change re-fetches data  
✅ Chart unmounts when toggle OFF  
✅ No data fetching when toggle OFF  
✅ Disclaimer banner visible  
✅ Mobile responsive  
✅ Dark mode support  

---

## Summary

Successfully implemented a **toggleable Rolling Frequency Trend chart** that:
- Visualizes letter frequency evolution over time
- **Hidden by default** to keep dashboard fast
- Interactive legend (isolate letters, show/hide baselines)
- Color-coded to match the ranking system
- Includes disclaimer about statistical independence
- Fully integrated with existing window size selector
- Responsive and mobile-friendly
- Dark mode compatible

**All requirements met!** 🎉
