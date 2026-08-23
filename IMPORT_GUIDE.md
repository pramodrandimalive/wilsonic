# Historical Data Import Guide

## Overview

The `backend/import_historical.py` script imports your custom 300,000-record dataset from an Excel file into the Wilsonic database.

## Prerequisites

Install required packages:
```bash
source venv/bin/activate
pip install pandas==2.2.2 openpyxl==3.1.5
```

## Usage

### Basic Usage (Auto-detect column)
```bash
python -m backend.import_historical <path_to_excel_file>
```

### Specify Column Name
```bash
python -m backend.import_historical <path_to_excel_file> <column_name>
```

### Examples
```bash
# Auto-detect column containing letters
python -m backend.import_historical ~/data/historical_draws.xlsx

# Specify column name explicitly
python -m backend.import_historical ~/data/draws.xlsx letter

# With relative path
python -m backend.import_historical ./data/wilsonic_history.xlsx
```

## What the Script Does

1. **Clears existing data**: Deletes all current draws from database
2. **Resets drift tracker**: Clears in-memory drift tracking state
3. **Reads Excel file**: Loads your custom dataset
4. **Extracts letters**: Auto-detects or uses specified column
5. **Filters valid entries**: Keeps only A-G, skips invalid (~127 "?" entries)
6. **Generates timestamps**: 
   - 3 minutes apart
   - Counts backward from now
   - Oldest record furthest in past
7. **Inserts in batches**: 1000 rows per batch for efficiency
8. **Progress reporting**: Updates every 10,000 rows
9. **Verification**: Calculates ranking and compares to expected percentages
10. **Drift check**: Confirms drift detection activates with sufficient data

## Expected Output

```
======================================================================
Wilsonic Historical Data Import
======================================================================

1. Initializing database...

2. Clearing existing draws...
  Deleting 1 existing draws...
  ✓ Deleted 1 rows

3. Resetting drift tracker...
  ✓ Drift tracker reset

4. Reading Excel file...
Reading Excel file: /path/to/data.xlsx
✓ Loaded 300,127 rows from Excel
  Columns: ['letter']

5. Extracting letters...
  Auto-detected column: 'letter'
  ✓ Extracted 300,127 raw entries

6. Filtering valid letters (A-G only)...
  ✓ Valid letters: 300,000
  ✗ Skipped (invalid): 127

7. Generating synthetic timestamps...
  Time interval: 3 minutes apart
  ✓ Generated 300,000 timestamps
  Oldest: 2025-01-15 12:38:45 UTC
  Newest: 2026-08-15 17:08:45 UTC
  Time span: 577 days, 4 hours

8. Preparing insert batches...
  Batch size: 1,000 rows
  Total batches: 300

9. Inserting historical data...
  Progress: 10,000 / 300,000 (3.3%)
  Progress: 20,000 / 300,000 (6.7%)
  Progress: 30,000 / 300,000 (10.0%)
  ...
  Progress: 290,000 / 300,000 (96.7%)
  Progress: 300,000 / 300,000 (100.0%)
  ✓ Inserted all 300,000 rows

======================================================================
Import Complete!
======================================================================
Total rows processed: 300,127
Valid letters inserted: 300,000
Invalid rows skipped: 127
Source: historical_import
Time span: 577 days
======================================================================

10. Verifying data with ranking calculation...

Expected vs Actual Letter Frequencies:
--------------------------------------------------
A:  38.20%  (expected  38.2%, diff: +0.00%)
B:  21.10%  (expected  21.1%, diff: +0.00%)
C:  13.40%  (expected  13.4%, diff: +0.00%)
D:  12.10%  (expected  12.1%, diff: +0.00%)
E:  11.00%  (expected  11.0%, diff: +0.00%)
F:   3.60%  (expected   3.6%, diff: +0.00%)
G:   0.70%  (expected   0.7%, diff: +0.00%)
--------------------------------------------------
Total draws: 300,000

11. Checking drift detection status...
  ✓ Drift detection: Active
  Any drift detected: False

======================================================================
Import successful! Database ready for analysis.
======================================================================
```

## Data Format

### Excel File Requirements
- Must contain a column with letter values (A-G)
- Column name can be any of:
  - `letter`, `Letter`, `LETTER`
  - `draw`, `Draw`, `DRAW`
  - `value`, `Value`, `VALUE`
  - `result`, `Result`, `RESULT`
  - Or specify custom name as second argument
- Invalid entries (non A-G) will be automatically skipped

### Example Excel Structure

**Option 1: Single column**
```
letter
A
B
C
A
...
```

**Option 2: Multiple columns (will auto-detect or use specified)**
```
id    letter    date
1     A         ...
2     B         ...
3     C         ...
...
```

## Timestamp Generation

For 300,000 records at 3-minute intervals:
- **Total time span**: ~577 days (~1.58 years)
- **Oldest record**: ~577 days before now
- **Newest record**: Current time
- **Direction**: Counting backward (oldest record = earliest timestamp)

This means:
- First row in Excel → Oldest timestamp
- Last row in Excel → Newest timestamp (now)

## Expected Frequency Distribution

After import, the ranking should show:

| Letter | Expected % | Typical Range |
|--------|-----------|---------------|
| A      | 38.2%     | 38.0 - 38.4%  |
| B      | 21.1%     | 20.9 - 21.3%  |
| C      | 13.4%     | 13.2 - 13.6%  |
| D      | 12.1%     | 11.9 - 12.3%  |
| E      | 11.0%     | 10.8 - 11.2%  |
| F      | 3.6%      | 3.4 - 3.8%    |
| G      | 0.7%      | 0.5 - 0.9%    |

Small deviations (±0.1-0.2%) are normal due to sampling variation.

## Troubleshooting

### Column Not Found
If you see an error about column names:
```bash
# List columns first to see what's available
python -c "import pandas as pd; print(pd.read_excel('your_file.xlsx').columns.tolist())"

# Then specify the correct column
python -m backend.import_historical your_file.xlsx correct_column_name
```

### Permission Error
Make sure the Excel file is not open in Excel or another program.

### Memory Issues (Large Files)
The script uses batch inserts (1000 rows at a time) to handle large datasets efficiently. 300k rows should work fine with default settings.

## Verification

After import, verify the data:

```bash
# Check total draws
curl http://localhost:8000/draws?limit=1 | python3 -m json.tool

# Check ranking
curl http://localhost:8000/stats/ranking | python3 -m json.tool

# Check drift status
curl http://localhost:8000/stats/drift | python3 -m json.tool

# Check oldest and newest draws
curl "http://localhost:8000/draws?limit=5&offset=0" | python3 -m json.tool  # Oldest
curl "http://localhost:8000/draws?limit=5" | python3 -m json.tool  # Newest
```

## Database After Import

- **Total draws**: 300,000
- **All sources**: `historical_import`
- **Timestamp range**: ~577 days
- **Drift detection**: Active (threshold met)
- **Ready for**: Manual entry, frontend use, API queries

## Next Steps

After successful import:
1. Restart the backend if running: `uvicorn backend.main:app --reload`
2. Refresh the frontend dashboard
3. Verify ranking shows expected percentages
4. Check drift indicator (should show "All Clear" initially)
5. Begin manual entry or prepare scraper for new draws
