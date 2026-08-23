# Records Management Feature

## Overview

The Records Management system provides comprehensive CRUD (Create, Read, Update, Delete) operations for draw records with advanced filtering, pagination, and sorting capabilities.

## Backend API Changes

### New Endpoints

#### 1. PUT /draws/{id}
Update an existing draw's letter and/or timestamp.

**Request Body:**
```json
{
  "letter": "B",  // Optional: New letter (A-G)
  "timestamp": "2026-08-15T16:00:00Z"  // Optional: New timestamp (ISO format)
}
```

**Response (200):**
```json
{
  "id": 12345,
  "letter": "B",
  "timestamp": "2026-08-15T16:00:00Z",
  "source": "manual"
}
```

**Error Responses:**
- `400`: No fields provided to update
- `404`: Draw ID not found
- `422`: Invalid letter (not A-G) or invalid timestamp format

**Validation:**
- Letter must be one of: A, B, C, D, E, F, G
- Timestamp must be valid ISO format (YYYY-MM-DDTHH:MM:SSZ)
- At least one field (letter or timestamp) must be provided

---

#### 2. DELETE /draws/{id}
Permanently delete a draw by ID.

**Response (200):**
```json
{
  "message": "Draw deleted successfully",
  "deleted_draw": {
    "id": 12345,
    "letter": "A",
    "timestamp": "2026-08-15T15:30:00Z",
    "source": "historical_import"
  }
}
```

**Error Responses:**
- `404`: Draw ID not found

**Warning:** Deleting records permanently affects statistical calculations across the entire application.

---

#### 3. GET /draws (Enhanced)
List draws with advanced filtering, sorting, and pagination.

**Query Parameters:**
- `page` (integer, default: 1): Page number (1-indexed)
- `page_size` (integer, default: 50, max: 500): Items per page
- `letter` (string, optional): Filter by letter (A-G)
- `source` (string, optional): Filter by source (manual, historical_import, scraper)
- `sort` (string, default: "newest"): Sort order
  - `"newest"`: Most recent first (DESC)
  - `"oldest"`: Oldest first (ASC)

**Example Request:**
```bash
GET /draws?page=1&page_size=25&letter=A&source=manual&sort=newest
```

**Response:**
```json
{
  "draws": [
    {
      "id": 299890,
      "letter": "A",
      "timestamp": "2026-08-16T05:43:19.903924",
      "source": "manual"
    }
  ],
  "total": 114561,
  "page": 1,
  "page_size": 25,
  "total_pages": 4583
}
```

---

## Frontend Implementation

### New Route: /records

A dedicated Records Management page accessible via navigation link from the main dashboard.

### Features

#### 1. Warning Banner
Prominent warning at the top:
> ⚠️ Editing or deleting records will change statistical calculations across the app.

#### 2. Advanced Filters
- **Letter Filter**: Dropdown (All, A, B, C, D, E, F, G)
- **Source Filter**: Dropdown (All, manual, historical_import, scraper)
- **Sort Order**: Newest First / Oldest First
- **Page Size**: 25 / 50 / 100 records per page

#### 3. Records Table
Displays:
- **ID**: Draw record ID
- **Letter**: Letter badge (A-G) with color coding
- **Timestamp**: Formatted date/time
- **Source**: Color-coded badge
  - Blue: manual
  - Purple: historical_import
  - Green: scraper
- **Actions**: Edit and Delete buttons per row

#### 4. Inline Editing
- Click "Edit" to enable inline editing for a row
- Edit letter via dropdown (A-G)
- Edit timestamp via datetime-local input
- "Save" to commit changes
- "Cancel" to discard changes

#### 5. Delete Confirmation
- Click "Delete" triggers a confirmation dialog
- Warns that deletion will affect statistics
- Confirms deletion with draw ID and letter

#### 6. Pagination Controls
- Previous / Next buttons
- Current page / total pages indicator
- Total records count
- Pagination resets to page 1 when filters change

---

## Technical Implementation

### Backend (routes.py)

#### New Pydantic Model: DrawUpdate
```python
class DrawUpdate(BaseModel):
    letter: Optional[str] = None
    timestamp: Optional[str] = None
    
    @validator('letter')
    def validate_letter(cls, v):
        if v is not None:
            v = v.upper().strip()
            if v not in stats.VALID_LETTERS:
                raise ValueError(f"Letter must be one of {', '.join(stats.VALID_LETTERS)}")
            return v
        return v
    
    @validator('timestamp')
    def validate_timestamp(cls, v):
        if v is not None:
            try:
                datetime.fromisoformat(v.replace('Z', '+00:00'))
            except (ValueError, AttributeError):
                raise ValueError("Timestamp must be in ISO format")
        return v
```

#### Enhanced list_draws() Function
- Added `letter`, `source`, `sort` query parameters
- Dynamic query building with SQLAlchemy filters
- Total count calculated with filters applied
- Conditional sorting (ASC/DESC)

---

### Frontend

#### Component: RecordsManagement.jsx
**Location:** `frontend/src/pages/RecordsManagement.jsx`

**State Management:**
- `draws`: Current page of records
- `page`, `pageSize`, `totalPages`, `total`: Pagination state
- `letterFilter`, `sourceFilter`, `sortOrder`: Filter state
- `editingId`, `editLetter`, `editTimestamp`: Editing state
- `loading`, `error`: UI state

**Key Functions:**
- `fetchDraws()`: Fetches records with current filters/pagination
- `startEdit(draw)`: Activates inline editing mode
- `cancelEdit()`: Discards editing changes
- `saveEdit(id)`: Commits changes via PUT request
- `deleteDraw(id, letter)`: Deletes record after confirmation
- `formatTimestamp(timestamp)`: Formats ISO timestamp for display

**API Integration:**
- `GET /draws`: Fetch paginated, filtered records
- `PUT /draws/{id}`: Update record
- `DELETE /draws/{id}`: Delete record

---

#### Styling: RecordsManagement.css
**Location:** `frontend/src/pages/RecordsManagement.css`

**Key Features:**
- Warning banner with gradient background and icon
- Filter controls in a flexible grid
- Responsive table with horizontal scroll
- Color-coded badges for letters and sources
- Action buttons with hover effects
- Inline editing inputs with focus states
- Pagination controls with disabled states
- Dark mode support
- Mobile responsive design

**Color Scheme:**
- Edit button: Blue (#2196f3)
- Delete button: Red (#f44336)
- Save button: Green (#4CAF50)
- Cancel button: Gray (#9e9e9e)
- Warning: Orange (#ff9800)

---

#### Updated App Structure

**App.jsx** now uses React Router:
```jsx
<Router>
  <Routes>
    <Route path="/" element={<Dashboard />} />
    <Route path="/records" element={<RecordsManagement />} />
  </Routes>
</Router>
```

**Dashboard.jsx** includes navigation link:
```jsx
<Link to="/records" className="nav-link">
  Manage Records
</Link>
```

---

## Usage Examples

### Backend API

**Update a draw's letter:**
```bash
curl -X PUT 'http://localhost:8000/draws/12345' \
  -H 'Content-Type: application/json' \
  -d '{"letter": "B"}'
```

**Update a draw's timestamp:**
```bash
curl -X PUT 'http://localhost:8000/draws/12345' \
  -H 'Content-Type: application/json' \
  -d '{"timestamp": "2026-08-15T16:00:00Z"}'
```

**Update both fields:**
```bash
curl -X PUT 'http://localhost:8000/draws/12345' \
  -H 'Content-Type: application/json' \
  -d '{"letter": "C", "timestamp": "2026-08-15T16:30:00Z"}'
```

**Delete a draw:**
```bash
curl -X DELETE 'http://localhost:8000/draws/12345'
```

**List draws with filters:**
```bash
# Filter by letter A, manual source, newest first
curl 'http://localhost:8000/draws?letter=A&source=manual&sort=newest&page=1&page_size=50'

# Get all historical_import records, oldest first
curl 'http://localhost:8000/draws?source=historical_import&sort=oldest&page=1&page_size=100'
```

---

### Frontend Usage

1. **Navigate to Records Management:**
   - Click "Manage Records" in the dashboard header

2. **Filter Records:**
   - Select a letter from the Letter dropdown
   - Select a source from the Source dropdown
   - Choose sort order (Newest/Oldest)
   - Adjust page size (25/50/100)

3. **Edit a Record:**
   - Click "Edit" on any row
   - Change the letter using the dropdown
   - Change the timestamp using the datetime picker
   - Click "Save" to commit, or "Cancel" to discard

4. **Delete a Record:**
   - Click "Delete" on any row
   - Confirm the deletion in the dialog
   - Record is permanently removed

5. **Navigate Pages:**
   - Use "Previous" and "Next" buttons
   - View current page and total pages
   - See total record count

---

## Important Notes

### Data Integrity
- Editing or deleting records **permanently affects** all statistical calculations:
  - Letter frequencies and rankings
  - Confidence intervals
  - Drift detection results
  - Summary statistics

### Performance Considerations
- GET /draws supports up to 500 records per page
- Filtering by letter or source is indexed for fast queries
- Total count is recalculated with each filter change
- Frontend auto-refreshes after edit/delete operations

### Security Considerations
- No authentication implemented (MVP phase)
- Consider adding auth before production deployment
- Audit logging recommended for delete operations
- Rate limiting recommended for API endpoints

### Best Practices
1. **Backup data** before bulk edits or deletes
2. **Use filters** to find specific records efficiently
3. **Review changes** in the statistics dashboard after edits
4. **Document reasons** for manual data corrections
5. **Avoid editing** historical_import records unless necessary

---

## Testing

### Backend Tests

Test all new endpoints:
```bash
# Test PUT with valid letter
curl -X PUT 'http://localhost:8000/draws/1' \
  -H 'Content-Type: application/json' \
  -d '{"letter": "D"}'

# Test PUT with invalid letter (expect 422)
curl -X PUT 'http://localhost:8000/draws/1' \
  -H 'Content-Type: application/json' \
  -d '{"letter": "Z"}'

# Test PUT with non-existent ID (expect 404)
curl -X PUT 'http://localhost:8000/draws/999999999' \
  -H 'Content-Type: application/json' \
  -d '{"letter": "A"}'

# Test DELETE success
curl -X DELETE 'http://localhost:8000/draws/1'

# Test DELETE non-existent (expect 404)
curl -X DELETE 'http://localhost:8000/draws/999999999'

# Test GET with all filters
curl 'http://localhost:8000/draws?page=2&page_size=25&letter=B&source=manual&sort=oldest'
```

### Frontend Tests

1. Navigate to /records
2. Verify warning banner displays
3. Test each filter independently
4. Test filter combinations
5. Test pagination navigation
6. Test inline editing (save and cancel)
7. Test delete with confirmation
8. Verify statistics update after changes
9. Test responsive design on mobile
10. Test dark mode appearance

---

## Dependencies

### Backend
- No new dependencies added
- Uses existing: FastAPI, SQLAlchemy, Pydantic

### Frontend
- **New:** `react-router-dom` (v6+)
- Existing: React, Vite

Install frontend dependency:
```bash
cd frontend
npm install react-router-dom
```

---

## File Changes Summary

### Backend
- `backend/api/routes.py`:
  - Added `DrawUpdate` Pydantic model
  - Added `PUT /draws/{id}` endpoint
  - Added `DELETE /draws/{id}` endpoint
  - Enhanced `GET /draws` with filters and sorting

### Frontend
- `frontend/src/App.jsx`: Converted to router wrapper
- `frontend/src/pages/Dashboard.jsx`: Extracted from App.jsx
- `frontend/src/pages/Dashboard.css`: Copied from App.css
- `frontend/src/pages/RecordsManagement.jsx`: New page component
- `frontend/src/pages/RecordsManagement.css`: New styles
- `frontend/src/App.css`: Added header navigation styles
- `frontend/package.json`: Added react-router-dom

---

## Future Enhancements

### Potential Improvements
1. **Bulk Operations**: Select multiple rows for batch edit/delete
2. **CSV Export**: Export filtered records to CSV
3. **Audit Log**: Track who changed what and when
4. **Undo Functionality**: Revert recent changes
5. **Search by ID**: Quick jump to specific record
6. **Date Range Filter**: Filter by timestamp range
7. **Real-time Updates**: WebSocket notifications for concurrent edits
8. **Keyboard Shortcuts**: Quick edit/delete with hotkeys
9. **Column Sorting**: Click column headers to sort
10. **Edit History**: View revision history per record

### Phase 2 Integration
When the scraper is added:
- Add "scraper" to source filter dropdown (already supported)
- Consider read-only mode for scraped records
- Add scraper-specific metadata columns

---

## Troubleshooting

### Common Issues

**Issue:** Frontend can't connect to backend
- **Solution:** Verify backend is running on http://localhost:8000
- Check CORS settings in backend/main.py

**Issue:** Timestamp editing doesn't work
- **Solution:** Ensure browser supports datetime-local input type
- Check timezone conversion in RecordsManagement.jsx

**Issue:** Filters not working
- **Solution:** Check API response for errors
- Verify filter values match valid options

**Issue:** Page breaks after routing
- **Solution:** Ensure react-router-dom is installed
- Check browser console for routing errors

**Issue:** Edit/Delete buttons don't work
- **Solution:** Check backend logs for API errors
- Verify draw ID exists before edit/delete

---

## Conclusion

The Records Management system provides a comprehensive interface for managing draw records with full CRUD capabilities, advanced filtering, and real-time statistics updates. The implementation follows best practices for both backend API design and frontend UX, with extensive validation, error handling, and user warnings for data integrity.
