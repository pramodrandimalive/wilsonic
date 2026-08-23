# Wilsonic Frontend

React dashboard for the Wilsonic lottery prediction indicator system.

## Features

### 1. Ranked List View
- All 7 letters (A-G) sorted by probability
- Displays frequency as percentage
- 95% Wilson confidence interval ranges
- Visual progress bars
- Color-coded (top letter highlighted)

### 2. Manual Entry Form
- 7 letter buttons (A-G)
- Click to select, click "Add Draw" to submit
- Real-time feedback (success/error messages)
- Automatically refreshes data after submission

### 3. History Table
- Shows last 10 draws
- Most recent first
- Displays:
  - Letter
  - Relative time ("5 mins ago" or absolute timestamp)
  - Source (manual/scraper)
- Latest draw highlighted

### 4. Drift Indicator
- Visual badge at top of dashboard
- Three states:
  - **All Clear (Green)**: Recent patterns match historical
  - **Drift Detected (Yellow)**: 10+ consecutive violations
  - **Monitoring (Blue)**: 5+ consecutive violations
- Shows which letters are affected

## Tech Stack

- **Framework**: React 18.3
- **Build Tool**: Vite 6.4
- **Styling**: Pure CSS (no framework)
- **API**: Fetch API for backend communication

## Setup

```bash
# Install dependencies
npm install

# Start development server
npm run dev

# Build for production
npm run build

# Preview production build
npm run preview
```

## Development Server

Runs on http://localhost:3000

Auto-refreshes every 30 seconds to keep data current.

## Project Structure

```
frontend/
├── public/              # Static assets
├── src/
│   ├── components/      # React components
│   │   ├── RankedList.jsx         # Letter ranking display
│   │   ├── RankedList.css
│   │   ├── ManualEntryForm.jsx    # Draw submission form
│   │   ├── ManualEntryForm.css
│   │   ├── HistoryTable.jsx       # Recent draws table
│   │   ├── HistoryTable.css
│   │   ├── DriftIndicator.jsx     # Drift alert badge
│   │   └── DriftIndicator.css
│   ├── App.jsx          # Main application
│   ├── App.css          # Global app styles
│   ├── main.jsx         # Entry point
│   └── index.css        # Base styles
├── index.html           # HTML template
├── vite.config.js       # Vite configuration
└── package.json         # Dependencies
```

## API Integration

Connects to backend API at http://localhost:8000

### Endpoints Used

| Endpoint | Method | Purpose |
|---|---|---|
| `/stats/ranking` | GET | Fetch letter ranking |
| `/draws` | GET | Fetch recent draws |
| `/stats/drift` | GET | Check drift status |
| `/draws` | POST | Submit new draw |

### CORS

Backend already configured to allow requests from localhost:3000.

## Features

### Auto-Refresh
- Data refreshes every 30 seconds
- Keeps dashboard current without manual reload

### Responsive Design
- Works on desktop, tablet, and mobile
- Adaptive layout (stacks on smaller screens)
- Touch-friendly buttons

### Error Handling
- Network errors displayed in banner
- Form validation (must select letter)
- Loading states for async operations

### User Feedback
- Success message after draw submission
- Loading indicators during API calls
- Hover effects on interactive elements

## Component Details

### RankedList
Displays all 7 letters with:
- Rank number (#1-7)
- Letter (large display)
- Percentage (p_hat * 100)
- Progress bar (visual representation)
- 95% CI range
- Raw count

### ManualEntryForm
- 7 clickable letter buttons (A-G)
- Selected letter highlighted (blue)
- "Add Draw" button (disabled until selection)
- Success/error message display
- Calls `POST /draws` API

### HistoryTable
- Shows last 10 draws in table format
- Columns: Letter (badge), Time (relative), Source (badge)
- Latest draw highlighted with blue background
- Time formatting:
  - "Just now" (< 1 min)
  - "X mins ago" (< 60 mins)
  - "X hours ago" (< 24 hours)
  - Absolute date/time (older)

### DriftIndicator
Displays drift status with color coding:
- **Green**: All clear (no drift)
- **Yellow**: Drift detected in one or more letters
- **Blue**: Letters at risk (monitoring)

Shows affected letters and violation counts.

## Styling

- Clean, modern design
- Blue color scheme (#2563eb)
- Card-based layout with shadows
- Smooth transitions and hover effects
- Responsive grid layout

## No Authentication

As per MVP requirements, no login or authentication is needed. Single-user system.

## Building for Production

```bash
npm run build
```

Creates optimized production build in `dist/` folder.

## Environment

Development assumes backend running on http://localhost:8000.

For production, update `API_BASE` in `App.jsx` to point to deployed backend URL.

## Browser Support

Modern browsers with ES6+ support:
- Chrome/Edge (latest)
- Firefox (latest)
- Safari (latest)

---

**Status**: Complete and functional  
**Connected to**: Backend API (Phase 1)  
**Ready for**: Production deployment (Phase 3)
