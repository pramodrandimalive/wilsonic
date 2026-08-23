# Letter Trend Cards - Component Layout Preview

## Visual Layout

Here's how the per-letter trend cards appear in the dashboard:

```
┌─────────────────────────────────────────────────────────────────────┐
│ Wilsonic Dashboard                                                  │
│ 299,882 historical draws                                            │
├─────────────────────────────────────────────────────────────────────┤
│                                                                      │
│ ┌──────────────────────────────────────────────────────────────┐   │
│ │ ✓ All Clear                                                   │   │
│ │ Recent patterns match historical baseline                    │   │
│ └──────────────────────────────────────────────────────────────┘   │
│                                                                      │
│ ┌──────────────────────────────────────────────────────────────┐   │
│ │ Analysis Window: [5k draws ▾]                                │   │
│ │ Smaller windows react faster but show more natural           │   │
│ │ statistical fluctuation. Larger windows are more stable.     │   │
│ └──────────────────────────────────────────────────────────────┘   │
│                                                                      │
│ ┌──────────────────────────────────────────────────────────────┐   │
│ │ Per-Letter Trends                                             │   │
│ │                                                               │   │
│ │ ┌─────┐ ┌─────┐ ┌─────┐ ┌─────┐ ┌─────┐ ┌─────┐ ┌─────┐    │   │
│ │ │ A ▼ │ │ B ─ │ │ C ▲ │ │ D ─ │ │ E ─ │ │ F ─ │ │ G ─ │    │   │
│ │ │━━━━━│ │━━━━━│ │━━━━━│ │━━━━━│ │━━━━━│ │━━━━━│ │━━━━━│    │   │
│ │ │Rcnt:│ │Rcnt:│ │Rcnt:│ │Rcnt:│ │Rcnt:│ │Rcnt:│ │Rcnt:│    │   │
│ │ │36.0%│ │21.1%│ │14.8%│ │12.1%│ │11.0%│ │3.6% │ │0.7% │    │   │
│ │ │     │ │     │ │     │ │     │ │     │ │     │ │     │    │   │
│ │ │Base:│ │Base:│ │Base:│ │Base:│ │Base:│ │Base:│ │Base:│    │   │
│ │ │38.0-│ │21.0-│ │13.2-│ │11.9-│ │10.8-│ │3.4- │ │0.5- │    │   │
│ │ │38.4%│ │21.3%│ │13.6%│ │12.3%│ │11.2%│ │3.8% │ │0.9% │    │   │
│ │ │     │ │     │ │     │ │     │ │     │ │     │ │     │    │   │
│ │ │z=-2.│ │z=-0.│ │z=2.7│ │z=0.9│ │z=0.1│ │z=-0.│ │z=-0.│    │   │
│ │ │21   │ │28   │ │0    │ │2    │ │2    │ │32   │ │09   │    │   │
│ │ └─────┘ └─────┘ └─────┘ └─────┘ └─────┘ └─────┘ └─────┘    │   │
│ └──────────────────────────────────────────────────────────────┘   │
│                                                                      │
│ [Manual Entry Form]  [Ranked List]                                  │
│ [History Table]                                                      │
│                                                                      │
└─────────────────────────────────────────────────────────────────────┘
```

## Card Details

### Individual Card Structure

Each letter card displays:

```
┌─────────────────┐
│ A          ▼    │  ← Letter and trend arrow
├─────────────────┤
│ Recent: 36.0%   │  ← Recent frequency (bold)
│ Baseline:       │  ← Historical CI range
│ 38.0%–38.4%     │
│                 │
│ 2 consecutive   │  ← Only if violations > 0
│ violations      │
│                 │
│ z = -2.21       │  ← Z-score (monospace font)
└─────────────────┘
```

### Color Coding

**▲ Up Trend (Above Upper Bound)**
- Border: Orange (#ff9800)
- Background: Warm gradient (white → light orange)
- Arrow: Dark orange (#ff6f00)
- Letter: Dark orange (#e65100)
- Example: Letter C at 14.8% when baseline is 13.2%–13.6%

**▼ Down Trend (Below Lower Bound)**
- Border: Red (#f44336)
- Background: Cool gradient (white → light red)
- Arrow: Dark red (#d32f2f)
- Letter: Dark red (#c62828)
- Example: Letter A at 36.0% when baseline is 38.0%–38.4%

**─ Flat Trend (Within CI)**
- Border: Light gray (#e0e0e0)
- Background: White
- Arrow: Medium gray (#9e9e9e)
- Letter: Normal text color
- Example: Letters B, D, E, F, G within their baselines

## Responsive Behavior

### Desktop (>768px)
- Grid: Auto-fit columns, min 140px per card
- 7 cards fit in 2 rows typically (4 + 3 or 3 + 2 + 2)
- Spacing: 0.75rem gap between cards

### Mobile (<768px)
- Grid: Auto-fit columns, min 120px per card
- Tighter spacing: 0.5rem gap
- Smaller fonts for compact display
- 2-3 cards per row typically

## Interactive Features

1. **Hover Effect**
   - Card lifts slightly (2px up)
   - Drop shadow appears
   - Smooth transition

2. **Real-Time Updates**
   - Updates when window size selector changes
   - Updates every 30 seconds with auto-refresh
   - No page reload needed

3. **Tooltip on Z-Score**
   - Shows "Z-score from two-proportion test" on hover

## Data Flow

```
API Response (/stats/drift?window_size=5000)
    ↓
drift_status: {
  "A": {
    "p_hat_recent": 0.360,
    "p_hat_historical": 0.382,
    "lower_bound": 0.380,
    "upper_bound": 0.384,
    "z_score": -2.21,
    "consecutive_violations": 2,
    "outside_interval": true
  },
  ...
}
    ↓
LetterTrendCards Component
    ↓
7 Individual Cards (one per letter)
```

## Example Scenarios

### Scenario 1: Window=5000, No Drift Detected
```
A ▼  Recent: 36.0% (Baseline: 38.0%–38.4%)  [2 violations]  z=-2.21
B ─  Recent: 21.1% (Baseline: 21.0%–21.3%)  z=-0.28
C ▲  Recent: 14.8% (Baseline: 13.2%–13.6%)  z=2.70
D ─  Recent: 12.1% (Baseline: 11.9%–12.3%)  z=0.92
E ─  Recent: 11.0% (Baseline: 10.8%–11.2%)  z=0.12
F ─  Recent: 3.6%  (Baseline: 3.4%–3.8%)    z=-0.32
G ─  Recent: 0.7%  (Baseline: 0.5%–0.9%)    z=-0.09
```

### Scenario 2: Window=1000, High Sensitivity
```
A ▲  Recent: 41.2% (Baseline: 38.0%–38.4%)  z=2.02
B ─  Recent: 21.0% (Baseline: 21.0%–21.3%)  z=-0.77
C ─  Recent: 13.1% (Baseline: 13.2%–13.6%)  z=-1.28
D ─  Recent: 12.0% (Baseline: 11.9%–12.3%)  z=-0.94
E ▲  Recent: 11.8% (Baseline: 10.8%–11.2%)  [1 violation]  z=2.03
F ─  Recent: 3.7%  (Baseline: 3.4%–3.8%)    z=0.21
G ─  Recent: 0.6%  (Baseline: 0.5%–0.9%)    z=-0.82
```

### Scenario 3: Window=50000, Stable
```
All letters show ─ (flat) with small z-scores (|z| < 1.2)
Very stable, no deviations detected
```

## Integration with Existing Features

1. **Drift Indicator Banner** (above cards)
   - Shows overall "All Clear" or "Drift Detected" status
   - Based on 10+ consecutive violations threshold
   - Summarizes drifted letters

2. **Window Size Selector** (above cards)
   - Changes window size (100 to 100k)
   - Causes cards to update with new recent percentages
   - More sensitive windows → more ▲/▼ arrows

3. **Ranked List** (below, right panel)
   - Shows overall historical ranking
   - Cards show real-time deviation from those baselines

## Advantages

1. **Granular Visibility**: See each letter's status individually
2. **Real-Time Feedback**: Immediate response to window size changes
3. **Visual Clarity**: Color coding and arrows are intuitive
4. **Statistical Context**: Shows CI range, z-score, violation count
5. **Actionable**: Can identify which letters need attention before 10+ violations
6. **Educational**: Helps understand how window size affects sensitivity

## Next Steps

This is the **component layout preview**. The styling is functional but can be adjusted:
- Card dimensions
- Spacing/gaps
- Color intensity
- Font sizes
- Border styles
- Shadow effects

Would you like me to adjust any visual aspects before finalizing?
