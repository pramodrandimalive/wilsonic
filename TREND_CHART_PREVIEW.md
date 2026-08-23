# Rolling Frequency Trend Chart - Component Preview

## Dashboard with Toggle (Default: OFF)

```
┌─────────────────────────────────────────────────────────────┐
│  Wilsonic Dashboard                      [Manage Records]   │
│  Lottery Prediction Indicator System                        │
└─────────────────────────────────────────────────────────────┘

┌──────────────────────┐  ┌──────────────────────────────────┐
│ 🔔 Monitoring        │  │ Analysis Window                  │
│ No drift detected    │  │ [5000 ▼]                        │
└──────────────────────┘  └──────────────────────────────────┘

┌─────────────────────────────────────────────────────────────┐
│  [A] 38.2%  [B] 21.1%  [C] 13.4%  [D] 12.1%                │
│  [E] 11.0%  [F] 3.6%   [G] 0.7%   (Letter Trend Cards)     │
└─────────────────────────────────────────────────────────────┘

┌─────────────────────────────────────────────────────────────┐
│  ⚪──────  Show Rolling Frequency Trend Chart               │
│  ^OFF                                                        │
└─────────────────────────────────────────────────────────────┘
                        👆 TOGGLE HERE

... (rest of dashboard: manual entry, ranking, history) ...
```

---

## Dashboard with Toggle (ON) - Chart Visible

```
┌─────────────────────────────────────────────────────────────┐
│  Wilsonic Dashboard                      [Manage Records]   │
└─────────────────────────────────────────────────────────────┘

┌──────────────────────┐  ┌──────────────────────────────────┐
│ Monitoring           │  │ Analysis Window: [5000 ▼]        │
└──────────────────────┘  └──────────────────────────────────┘

... (Letter Trend Cards) ...

┌─────────────────────────────────────────────────────────────┐
│  ──────⚪  Show Rolling Frequency Trend Chart               │
│  ^ON                                                         │
└─────────────────────────────────────────────────────────────┘

┌─────────────────────────────────────────────────────────────┐
│  Rolling Frequency Trend                                    │
│  Window: 5000 draws • Interval: 500 draws • Total: 299,890 │
├─────────────────────────────────────────────────────────────┤
│  [Show All]  ☐ Show Baselines                              │
│  [A] [B] [C] [D] [E] [F] [G]  ← Click to isolate          │
├─────────────────────────────────────────────────────────────┤
│   40% ┤                 ╱─────A (green)                    │
│       │                ╱                                    │
│   30% ┤          ─────B (blue)                             │
│       │                                                     │
│   20% ┤      ╱─────C (orange)                              │
│       │     ╱                                               │
│   10% ┤────D,E,F,G (purple, red, cyan, amber)              │
│       │                                                     │
│    0% └──────────────────────────────────────────────────  │
│       5K      100K      200K      300K  (Draw Position)    │
├─────────────────────────────────────────────────────────────┤
│  ℹ️ Shows recent frequency vs historical baseline over      │
│     time. This is not a predictive pattern — draws are      │
│     statistically independent, so chart shapes don't        │
│     forecast future draws.                                  │
└─────────────────────────────────────────────────────────────┘

... (rest of dashboard) ...
```

---

## Chart with Baselines Enabled

```
┌─────────────────────────────────────────────────────────────┐
│  Rolling Frequency Trend                                    │
├─────────────────────────────────────────────────────────────┤
│  [Show All]  ☑ Show Baselines  ← CHECKED                   │
│  [A] [B] [C] [D] [E] [F] [G]                               │
├─────────────────────────────────────────────────────────────┤
│   40% ┤        ╱─────A (green)                             │
│       │ - - - A baseline (38.2%) - - - - - - (green dash) │
│   30% ┤                                                     │
│       │                                                     │
│   20% ┤  ─────B (blue)                                     │
│       │ - - - B baseline (21.1%) - - - - (blue dash)      │
│   10% ┤                                                     │
│       │ - - C,D,E,F,G baselines - - (colored dashes)      │
│    0% └─────────────────────────────────────────────────   │
│       5K      100K      200K      300K                     │
└─────────────────────────────────────────────────────────────┘

Each letter has its own baseline (dashed horizontal line)
showing full-history average. Easy to see when recent
trend is above/below expected.
```

---

## Chart with Letter B Isolated

```
┌─────────────────────────────────────────────────────────────┐
│  Rolling Frequency Trend                                    │
├─────────────────────────────────────────────────────────────┤
│  [Show All]  ☑ Show Baselines                              │
│  [ ] [ B ] [ ] [ ] [ ] [ ] [ ]  ← Only B selected         │
│     ^^^^                                                    │
│   ISOLATED (highlighted with shadow)                        │
├─────────────────────────────────────────────────────────────┤
│   25% ┤                                                     │
│       │     ╱──────────────────B (blue, 3px wide)         │
│   20% ┤    ╱                                                │
│       │ - - - B baseline (21.1%) - - - - - (blue dash)    │
│   15% ┤                                                     │
│       │                                                     │
│   10% └─────────────────────────────────────────────────   │
│       5K      100K      200K      300K                     │
│                                                             │
│  Only letter B visible. Line is thicker (3px).             │
│  Click B again to show all letters.                        │
└─────────────────────────────────────────────────────────────┘
```

---

## Interactive Controls Explained

### Letter Toggle Buttons
```
[A] [B] [C] [D] [E] [F] [G]
 ↑   ↑   ↑   ↑   ↑   ↑   ↑
 │   │   │   │   │   │   └─ Amber button
 │   │   │   │   │   └───── Cyan button
 │   │   │   │   └───────── Red button
 │   │   │   └───────────── Purple button
 │   │   └───────────────── Orange button
 │   └───────────────────── Blue button
 └───────────────────────── Green button

Click any button:
- First click: ISOLATES that letter (hides others)
- Second click: Shows all letters again

Button states:
- Active: Filled with color, white text
- Inactive: White background, colored border
- Isolated: Filled + shadow ring
```

### Show/Hide Controls
```
┌────────────────────────────────────────────┐
│ [Show All] ☐ Show Baselines               │
│     ↑          ↑                           │
│     │          └─ Checkbox: Toggle dashed  │
│     │             baseline reference lines │
│     │                                      │
│     └─ Button: Toggle all letters ON/OFF  │
│        (Smart: "Hide All" when all shown) │
└────────────────────────────────────────────┘
```

### Legend (clickable)
```
─── A  ─── B  ─── C  ─── D  ─── E  ─── F  ─── G
 ↑      ↑      ↑      ↑      ↑      ↑      ↑
 Click any legend item to isolate that letter
 (same behavior as letter toggle buttons)
```

### Tooltip (on hover)
```
┌──────────────────┐
│  Draw #125000    │  ← Position in sequence
├──────────────────┤
│  A: 38.45%       │  ← Color-coded frequencies
│  B: 21.32%       │     for all visible letters
│  C: 13.12%       │
│  ...             │
└──────────────────┘
```

---

## Color Scheme Reference

| Letter | Color   | Hex Code | Usage                     |
|--------|---------|----------|---------------------------|
| A      | Green   | #4CAF50  | Line, button, baseline    |
| B      | Blue    | #2196F3  | Line, button, baseline    |
| C      | Orange  | #FF9800  | Line, button, baseline    |
| D      | Purple  | #9C27B0  | Line, button, baseline    |
| E      | Red     | #F44336  | Line, button, baseline    |
| F      | Cyan    | #00BCD4  | Line, button, baseline    |
| G      | Amber   | #FFC107  | Line, button, baseline    |

**Consistency:** These colors match the letter badges throughout the app (ranking cards, drift indicators, etc.)

---

## Responsive Behavior

### Desktop (> 768px)
```
Controls: Side-by-side layout
  [Show All] [☐ Baselines]    [A] [B] [C] [D] [E] [F] [G]
  └─ Left side                  └─ Right side

Chart: Full 400px height
```

### Mobile (≤ 768px)
```
Controls: Stacked layout
  [Show All] [☐ Baselines]
  
  [A] [B] [C]
  [D] [E] [F] [G]
  └─ Buttons wrap to multiple rows

Chart: Responsive width, 400px height
```

---

## Data Flow

```
User toggles chart ON
       ↓
Dashboard.jsx sets showTrendChart = true
       ↓
useEffect triggers fetchTrendData()
       ↓
API call: GET /stats/rolling-trend?window_size=5000&interval=500
       ↓
Backend calculates frequencies at each interval
       ↓
Returns data_points array + baseline_frequencies
       ↓
Dashboard passes trendData to RollingFrequencyChart
       ↓
Chart renders with Recharts
       ↓
User interacts (click letters, toggle baselines)
       ↓
Chart re-renders with updated visibility/baselines
       ↓
(No new API calls for interactions)
```

---

## Toggle Switch Visual States

### OFF (Default)
```
┌────────────────────────────────────────────┐
│  ⚪──────  Show Rolling Frequency Trend    │
│  ^Gray     Chart                           │
└────────────────────────────────────────────┘
```

### ON
```
┌────────────────────────────────────────────┐
│  ──────⚪  Show Rolling Frequency Trend    │
│  ^Green    Chart                           │
└────────────────────────────────────────────┘
```

### Transition
```
OFF: ⚪──────  (slider left, gray background)
         ↓ (0.3s smooth transition)
ON:  ──────⚪  (slider right, green background)
```

---

## Complete Feature Set

✅ **Toggle switch** (hidden by default)
✅ **Line chart** with 7 color-coded letter lines
✅ **Rolling window** calculation at intervals
✅ **Baseline reference lines** (dashed, toggleable)
✅ **Letter isolation** (click to show one letter)
✅ **Show All / Hide All** button
✅ **Interactive tooltip** (hover over chart)
✅ **Clickable legend** (same as letter buttons)
✅ **Disclaimer banner** (statistical independence warning)
✅ **Window size integration** (uses global selector)
✅ **Auto-refresh** on draw submission
✅ **Loading state** (shows "Loading trend data...")
✅ **Responsive design** (desktop + mobile)
✅ **Dark mode** support

---

## Preview the Component

To see it in action:

1. Start backend: `uvicorn backend.main:app --reload`
2. Start frontend: `npm run dev` (in frontend/)
3. Open: `http://localhost:3001/`
4. Toggle: "Show Rolling Frequency Trend Chart" → ON
5. Wait: ~1-2 seconds for data to load
6. Interact: Click letters, toggle baselines, explore!

The chart will show **how letter frequencies have changed over the 299,890 historical draws**, making it easy to spot long-term trends and compare recent behavior against historical baselines.

**Remember:** This is a visualization tool, not a prediction system. The disclaimer makes this clear to users.
