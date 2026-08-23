# Enhanced Rolling Frequency Trend Chart - Zoom & Baseline Improvements

## Overview

The Rolling Frequency Trend chart has been enhanced with **zoom/pan capabilities** and **improved baseline visualization** with deviation shading.

---

## ✨ New Features

### 1. **Zoom & Pan with Brush Component**

**What it does:**
- Interactive brush slider at the bottom of the chart
- Drag the handles or the brush window to select a range
- Chart automatically zooms to the selected range
- "Reset Zoom" button appears to return to full view

**How to use:**
1. Enable the trend chart
2. Look at the bottom of the chart (blue brush slider)
3. **Drag the handles** to adjust the visible range
4. **Drag the brush window** itself to pan left/right
5. Click **"Reset Zoom"** button to see full dataset again

**Example:**
```
Full view: Draws 5,000 → 299,890 (all data)
         ↓ (drag brush to select range)
Zoomed:   Draws 100,000 → 150,000 (focused view)
         ↓ (click Reset Zoom)
Full view: Back to 5,000 → 299,890
```

---

### 2. **Improved Baseline Visualization**

#### **Muted Baseline Colors**
Baseline reference lines now use **light, muted colors** instead of the same solid colors as the trend lines:

| Letter | Trend Line | Baseline (Muted) |
|--------|-----------|------------------|
| A | #4CAF50 (Green) | #A5D6A7 (Light Green) |
| B | #2196F3 (Blue) | #90CAF9 (Light Blue) |
| C | #FF9800 (Orange) | #FFCC80 (Light Orange) |
| D | #9C27B0 (Purple) | #CE93D8 (Light Purple) |
| E | #F44336 (Red) | #EF9A9A (Light Red) |
| F | #00BCD4 (Cyan) | #80DEEA (Light Cyan) |
| G | #FFC107 (Amber) | #FFE082 (Light Amber) |

**Additional styling:**
- Dashed pattern: `8px dash, 4px gap` (was `5px dash, 5px gap`)
- Stroke width: `2px` (slightly thicker)
- Opacity: `0.7` (semi-transparent)
- Label shows exact baseline value (e.g., "A baseline (38.2%)")

**Visual result:** Baselines clearly read as "background reference" rather than active data lines.

---

### 3. **Deviation Shading**

**What it shows:**
- **Green tint** when trend line is **above** baseline (positive deviation)
- **Red tint** when trend line is **below** baseline (negative deviation)
- Very subtle (15% opacity) - doesn't overwhelm the chart
- Updates in real-time as you zoom/pan

**How it works:**
- For each data point, calculates the distance between trend and baseline
- Creates stacked area fills:
  - `shade_above_${letter}`: Green (#4CAF50) at 15% opacity
  - `shade_below_${letter}`: Red (#f44336) at 15% opacity
- Only visible when both "Show Baselines" and "Show Deviation Shading" are checked

**Visual effect:**
```
      Above baseline
      ╱────────────  Trend line (solid color)
     ╱░░░░░░░░░░░░░ ← Green shading (positive deviation)
────────────────────  Baseline (dashed, muted color)

      Below baseline
────────────────────  Baseline (dashed, muted color)
     ░░░░░░░░░░░░░╲ ← Red shading (negative deviation)
      ╲────────────  Trend line (solid color)
```

---

## 🎛️ New Controls

### Updated Control Panel

```
┌────────────────────────────────────────────────────┐
│ [Show All]  ☑ Show Baselines  ☑ Show Deviation   │
│                                 Shading            │
│             ↑                   ↑                  │
│             │                   └─ NEW: Toggle     │
│             │                      deviation       │
│             │                      shading         │
│             └─ Existing baseline toggle            │
│                                                    │
│ [Reset Zoom] ← NEW: Appears when zoomed           │
└────────────────────────────────────────────────────┘

Letter toggles: [A] [B] [C] [D] [E] [F] [G]
```

### Control Behavior

1. **"Show Baselines"** checkbox
   - Enables/disables baseline reference lines
   - Must be ON for shading to work

2. **"Show Deviation Shading"** checkbox
   - Only enabled when "Show Baselines" is checked
   - Toggles green/red tinted areas
   - Disabled state (gray) when baselines are off

3. **"Reset Zoom"** button (orange)
   - Only appears when chart is zoomed
   - Returns to full data range
   - Hides automatically when at full view

---

## 📊 Chart Layout Changes

### Increased Height
- **Before:** 400px
- **After:** 450px
- Reason: Accommodate the 30px brush component

### Bottom Margin
- **Before:** 5px
- **After:** 60px
- Reason: Space for brush and x-axis label

### Brush Component
- Height: 30px
- Colors: Blue stroke (#2196F3), light blue fill (#e3f2fd)
- Position: Bottom of chart, above x-axis label
- Interactive: Drag handles or window

---

## 🎨 Visual Examples

### Example 1: All Letters with Baselines and Shading

```
┌──────────────────────────────────────────────────┐
│  [Show All] ☑ Baselines ☑ Shading [Reset Zoom] │
│  [A] [B] [C] [D] [E] [F] [G]                    │
├──────────────────────────────────────────────────┤
│  40% ┤     ╱─────────A (green, solid)           │
│      │    ╱░░░░░░░░░░ ← Green shading (above)   │
│      │ ─ ─ ─ A baseline (light green, dashed)   │
│  30% ┤                                           │
│      │ ─ ─ ─ B baseline (light blue, dashed)    │
│      │  ░░░░░░░░╲──────B (blue, solid)          │
│      │          ╲ ← Red shading (below)          │
│  20% ┤                                           │
│      │ ... (C, D, E, F, G with shading) ...     │
│   0% └───────────────────────────────────────    │
│                                                  │
│      [===============BRUSH================]      │
│      ^                                    ^      │
│      Drag handles to zoom                       │
└──────────────────────────────────────────────────┘
```

### Example 2: Letter B Isolated with Shading

```
┌──────────────────────────────────────────────────┐
│  [Show All] ☑ Baselines ☑ Shading              │
│  [ ] [B] [ ] [ ] [ ] [ ] [ ]  ← Only B         │
├──────────────────────────────────────────────────┤
│  25% ┤                                           │
│      │      ╱──────────────────B (blue, 3px)    │
│      │     ╱░░░░░░░░░░░░░░░░░░░                 │
│  20% ┤ ─ ─ ─ B baseline (21.1%) ─ ─ ─ ─        │
│      │                                           │
│      │  ░░░░░╲                                   │
│  15% ┤       ╲ (brief dip below baseline)       │
│      │                                           │
│  10% └───────────────────────────────────────    │
│                                                  │
│      [===========BRUSH==========]  ← Zoomed     │
│      100K               200K                     │
└──────────────────────────────────────────────────┘
```

### Example 3: Zoomed View (100K - 150K draws)

```
┌──────────────────────────────────────────────────┐
│  [Show All] ☑ Baselines ☑ Shading [Reset Zoom] │
│  [A] [B] [C] [D] [E] [F] [G]                    │
├──────────────────────────────────────────────────┤
│  Zoomed to draws 100,000 → 150,000              │
│                                                  │
│  42% ┤                                           │
│      │    ╱╲  ╱─A (clearly above baseline)      │
│      │   ╱░░╲╱░░░░░░                             │
│  38% ┤ ─ ─ ─ ─ A baseline ─ ─ ─ ─               │
│      │  ░░░░                                     │
│  34% ┤      ╲ (brief dip, red shading)          │
│      │                                           │
│  30% └──────────────────────────────────────     │
│      100K      125K      150K                    │
│                                                  │
│      [     ████████     ]  ← Brush shows zoom   │
│      5K    100K  150K   300K                     │
└──────────────────────────────────────────────────┘
```

---

## 🔧 Technical Implementation

### Data Enrichment

For each data point, the component calculates:

```javascript
// If trend above baseline
enriched[`shade_above_${letter}`] = freq - baseline
enriched[`shade_below_${letter}`] = 0

// If trend below baseline
enriched[`shade_above_${letter}`] = 0
enriched[`shade_below_${letter}`] = baseline - freq
```

This creates two stacked area series per letter:
- One for positive deviations (green)
- One for negative deviations (red)

### Recharts Components Used

**New/Updated:**
- `<Brush>` - Interactive zoom slider
- `<Area>` - Deviation shading (2 per letter when shading enabled)
- `<ReferenceLine>` - Updated colors and styling

**Existing:**
- `<Line>` - Trend lines (unchanged)
- `<XAxis>` - Now supports `domain` prop for zoom
- `<YAxis>`, `<Tooltip>`, `<Legend>` - Unchanged

### State Management

**New state:**
```javascript
const [zoomDomain, setZoomDomain] = useState(null)
const [showShading, setShowShading] = useState(true)
```

**State interactions:**
- `showShading` disabled when `showBaselines` is false
- `zoomDomain` controls x-axis range
- `zoomDomain = null` means full view (no zoom)

---

## 🎯 User Interaction Flow

### Scenario 1: Analyzing Letter A's Trend

1. User toggles chart ON
2. Clicks "A" button → Isolates letter A
3. Checks "Show Baselines" → Light green dashed line appears
4. Checks "Show Deviation Shading" → Green/red tints appear
5. Sees that A is **mostly above baseline** (green shading dominant)
6. Drags brush to zoom on draws 200K-250K
7. Notices A briefly dips **below baseline** (red shading appears)
8. Clicks "Reset Zoom" → Returns to full view
9. Conclusion: A is generally above historical average, with brief periods below

### Scenario 2: Comparing Multiple Letters

1. User toggles chart ON
2. Checks "Show Baselines" and "Show Deviation Shading"
3. Views all 7 letters with their baselines
4. Notices:
   - A (green shading dominant) → Trending above baseline
   - B (red shading dominant) → Trending below baseline
   - C (mixed) → Oscillating around baseline
5. Drags brush to focus on recent 50K draws
6. Sees that B has **crossed above** its baseline recently (green shading)
7. Clicks "Reset Zoom" to confirm in full view

---

## 📊 Data Interpretation Guide

### Green Shading (Above Baseline)
- Letter appears **more frequently** than historical average
- Could indicate recent "hot streak" (but remember: draws are independent!)
- Example: A baseline is 38.2%, recent trend at 39.5%

### Red Shading (Below Baseline)
- Letter appears **less frequently** than historical average
- Could indicate recent "cold streak" (but draws are random!)
- Example: B baseline is 21.1%, recent trend at 20.3%

### No Shading / Flat
- Trend line **matches** baseline
- Letter frequency is consistent with historical average
- Most stable state

### Important Reminder
The chart shows **what has happened**, not **what will happen**. The disclaimer remains:
> "Shows recent frequency vs historical baseline over time. This is not a predictive pattern — draws are statistically independent, so chart shapes don't forecast future draws."

---

## 🎨 Color Scheme Summary

### Trend Lines (Solid)
| Letter | Color | Hex | Line Width |
|--------|-------|-----|------------|
| A | Green | #4CAF50 | 2px (3px isolated) |
| B | Blue | #2196F3 | 2px (3px isolated) |
| C | Orange | #FF9800 | 2px (3px isolated) |
| D | Purple | #9C27B0 | 2px (3px isolated) |
| E | Red | #F44336 | 2px (3px isolated) |
| F | Cyan | #00BCD4 | 2px (3px isolated) |
| G | Amber | #FFC107 | 2px (3px isolated) |

### Baselines (Dashed)
| Letter | Color | Hex | Pattern |
|--------|-------|-----|---------|
| A | Light Green | #A5D6A7 | 8-4 dash, 2px, 70% opacity |
| B | Light Blue | #90CAF9 | 8-4 dash, 2px, 70% opacity |
| C | Light Orange | #FFCC80 | 8-4 dash, 2px, 70% opacity |
| D | Light Purple | #CE93D8 | 8-4 dash, 2px, 70% opacity |
| E | Light Red | #EF9A9A | 8-4 dash, 2px, 70% opacity |
| F | Light Cyan | #80DEEA | 8-4 dash, 2px, 70% opacity |
| G | Light Amber | #FFE082 | 8-4 dash, 2px, 70% opacity |

### Shading
| Type | Color | Hex | Opacity |
|------|-------|-----|---------|
| Above baseline | Green | #4CAF50 | 15% |
| Below baseline | Red | #f44336 | 15% |

### UI Elements
| Element | Color | Hex |
|---------|-------|-----|
| Brush stroke | Blue | #2196F3 |
| Brush fill | Light blue | #e3f2fd |
| Reset Zoom button | Orange | #FF9800 |
| Reset Zoom hover | Dark orange | #F57C00 |

---

## 🚀 Performance Notes

### Shading Calculation
- Adds 14 extra data keys per point when shading enabled (7 letters × 2 areas)
- Example: 295 data points × 14 = 4,130 additional values
- **Impact:** Minimal - Recharts handles this efficiently

### Zoom Performance
- `domain` prop on `XAxis` filters data client-side
- No additional API calls when zooming
- Smooth performance even with 300K+ draws dataset

### Render Optimization
- Shading only calculated when both baselines and shading are enabled
- Brush component adds ~30KB to bundle (already included in recharts)

---

## ✅ Testing Checklist

### Zoom Functionality
- ✅ Brush appears at bottom of chart
- ✅ Drag brush handles to zoom
- ✅ Drag brush window to pan
- ✅ "Reset Zoom" button appears when zoomed
- ✅ "Reset Zoom" returns to full view
- ✅ Zoom works with all letters visible
- ✅ Zoom works with single letter isolated

### Baseline Improvements
- ✅ Baseline colors are muted (light versions)
- ✅ Baselines use dashed pattern (8-4)
- ✅ Baselines show exact % value in label
- ✅ Baselines clearly contrast with trend lines
- ✅ Baselines only show for visible letters

### Deviation Shading
- ✅ Green shading when above baseline
- ✅ Red shading when below baseline
- ✅ Shading checkbox disabled when baselines off
- ✅ Shading updates when toggling letters
- ✅ Shading works correctly when zoomed
- ✅ Shading is subtle (15% opacity)
- ✅ Shading works with isolated letter

### Integration
- ✅ All controls work together
- ✅ Window size changes re-fetch data
- ✅ Draw submission refreshes chart
- ✅ Mobile responsive
- ✅ Dark mode compatible

---

## 📝 Summary of Enhancements

### What Changed

1. **Zoom/Pan Added**
   - Interactive brush slider
   - Click-drag to select range
   - Reset button to restore full view
   - Chart height increased to 450px

2. **Baseline Visualization Improved**
   - Muted colors (light variants)
   - Thicker dashed lines (8-4 pattern)
   - Exact % values in labels
   - Clear contrast with trend lines

3. **Deviation Shading Added**
   - Green tint above baseline
   - Red tint below baseline
   - Toggle control (linked to baseline toggle)
   - 15% opacity (subtle, not overwhelming)

4. **New Controls**
   - "Show Deviation Shading" checkbox
   - "Reset Zoom" button (conditional)
   - Improved control layout

### What Stayed the Same

- Letter isolation (click to isolate)
- Show All / Hide All button
- Letter toggle buttons
- Interactive tooltip
- Clickable legend
- Window size integration
- Color scheme (trend lines)
- Disclaimer banner

---

## 🎉 Result

The Rolling Frequency Trend chart now provides:
- **Better zoom control** for detailed analysis of specific ranges
- **Clearer visual hierarchy** between trends and baselines
- **Instant deviation detection** with color-coded shading
- **Professional appearance** with thoughtful color choices
- **Enhanced usability** with intuitive controls

All enhancements work seamlessly with existing features (letter isolation, window size changes, etc.) and maintain the chart's educational purpose while adding powerful analytical capabilities! 🚀
