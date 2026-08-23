"""
One-time import script for historical letter draw data.

Imports 300,000-record dataset from Excel file (sheet "Draws", column "letter"),
generates synthetic timestamps (3 minutes apart, counting backward from now),
and inserts rows with source="historical_import".

Run with: python -m backend.import_historical <path_to_excel_file>
"""

import sys
from datetime import datetime, timedelta, timezone
from pathlib import Path
from typing import List, Tuple

import pandas as pd

from backend.database import SessionLocal, init_db
from backend.models import Draw
from backend import stats


# Valid letters A-G
VALID_LETTERS = {'A', 'B', 'C', 'D', 'E', 'F', 'G'}

# Excel file structure
SHEET_NAME = "Draws"
COLUMN_NAME = "letter"

# Batch size for inserts
BATCH_SIZE = 1000

# Progress reporting interval
PROGRESS_INTERVAL = 10000

# Time interval between draws (3 minutes)
TIME_INTERVAL = timedelta(minutes=3)


def read_excel_file(file_path: str) -> List[str]:
    """
    Read letter sequence from Excel file.
    
    Reads sheet "Draws", column "letter" directly.
    
    Args:
        file_path: Path to Excel file
        
    Returns:
        List of raw letter strings
    """
    print(f"Reading Excel file: {file_path}")
    print(f"  Sheet: '{SHEET_NAME}'")
    print(f"  Column: '{COLUMN_NAME}'")
    
    try:
        df = pd.read_excel(file_path, sheet_name=SHEET_NAME)
        print(f"  ✓ Loaded {len(df):,} rows")
        
        # Extract letter column
        if COLUMN_NAME not in df.columns:
            print(f"  ✗ Error: Column '{COLUMN_NAME}' not found")
            print(f"  Available columns: {list(df.columns)}")
            sys.exit(1)
        
        letters = df[COLUMN_NAME].astype(str).str.strip().str.upper().tolist()
        return letters
        
    except Exception as e:
        print(f"  ✗ Error reading Excel file: {e}")
        sys.exit(1)


def filter_valid_letters(letters: List[str]) -> Tuple[List[str], int]:
    """
    Filter out invalid letters (non A-G entries).
    
    Args:
        letters: List of letter strings
        
    Returns:
        Tuple of (valid_letters, skipped_count)
    """
    valid = []
    skipped = 0
    
    for letter in letters:
        if letter in VALID_LETTERS:
            valid.append(letter)
        else:
            skipped += 1
    
    return valid, skipped


def generate_timestamps(count: int, end_time: datetime = None) -> List[datetime]:
    """
    Generate synthetic timestamps counting backward from end_time.
    
    Timestamps are 3 minutes apart, with the oldest record furthest in the past.
    
    Args:
        count: Number of timestamps to generate
        end_time: End timestamp (default: now)
        
    Returns:
        List of timestamps in chronological order (oldest first)
    """
    if end_time is None:
        end_time = datetime.now(timezone.utc)
    
    # Generate timestamps backward from end_time
    timestamps = []
    current_time = end_time
    
    for i in range(count):
        timestamps.append(current_time)
        current_time = current_time - TIME_INTERVAL
    
    # Reverse to get chronological order (oldest first)
    timestamps.reverse()
    
    return timestamps


def clear_existing_draws(db):
    """Clear all existing draws from database."""
    count = db.query(Draw).count()
    
    if count == 0:
        print("  Database is already empty")
        return 0
    
    print(f"  Deleting {count:,} existing draws...")
    deleted = db.query(Draw).delete()
    db.commit()
    print(f"  ✓ Deleted {deleted:,} rows")
    
    return deleted


def insert_batch(db, batch: List[Draw], batch_num: int, total_batches: int):
    """Insert a batch of draws."""
    try:
        db.bulk_save_objects(batch)
        db.commit()
        return len(batch)
    except Exception as e:
        print(f"\n✗ Error inserting batch {batch_num}/{total_batches}: {e}")
        db.rollback()
        raise


def import_historical_data(file_path: str):
    """
    Import historical letter draw data from Excel file.
    
    Reads sheet "Draws", column "letter" directly.
    
    Args:
        file_path: Path to Excel file
    """
    print("=" * 70)
    print("Wilsonic Historical Data Import")
    print("=" * 70)
    
    # Validate file exists
    if not Path(file_path).exists():
        print(f"\n✗ Error: File not found: {file_path}")
        sys.exit(1)
    
    # Initialize database
    print("\n1. Initializing database...")
    init_db()
    db = SessionLocal()
    
    try:
        # Clear existing draws
        print("\n2. Clearing existing draws...")
        clear_existing_draws(db)
        
        # Reset drift tracker
        print("\n3. Resetting drift tracker...")
        stats.reset_drift_tracker()
        print("  ✓ Drift tracker reset")
        
        # Read Excel file
        print("\n4. Reading Excel file...")
        letters = read_excel_file(file_path)
        print(f"  ✓ Extracted {len(letters):,} raw entries")
        
        # Filter valid letters
        print("\n5. Filtering valid letters (A-G only)...")
        valid_letters, skipped = filter_valid_letters(letters)
        print(f"  ✓ Valid letters: {len(valid_letters):,}")
        print(f"  ✗ Skipped (invalid): {skipped:,}")
        
        if len(valid_letters) == 0:
            print("\n✗ Error: No valid letters to import")
            sys.exit(1)
        
        # Generate timestamps
        print("\n6. Generating synthetic timestamps...")
        print(f"  Time interval: 3 minutes apart")
        end_time = datetime.now(timezone.utc)
        timestamps = generate_timestamps(len(valid_letters), end_time)
        oldest = timestamps[0]
        newest = timestamps[-1]
        time_span = newest - oldest
        print(f"  ✓ Generated {len(timestamps):,} timestamps")
        print(f"  Oldest: {oldest.strftime('%Y-%m-%d %H:%M:%S')} UTC")
        print(f"  Newest: {newest.strftime('%Y-%m-%d %H:%M:%S')} UTC")
        print(f"  Time span: {time_span.days} days, {time_span.seconds // 3600} hours")
        
        # Create Draw objects
        print("\n7. Preparing insert batches...")
        total_batches = (len(valid_letters) + BATCH_SIZE - 1) // BATCH_SIZE
        print(f"  Batch size: {BATCH_SIZE:,} rows")
        print(f"  Total batches: {total_batches:,}")
        
        # Insert in batches
        print("\n8. Inserting historical data...")
        inserted_total = 0
        
        for i in range(0, len(valid_letters), BATCH_SIZE):
            batch_letters = valid_letters[i:i + BATCH_SIZE]
            batch_timestamps = timestamps[i:i + BATCH_SIZE]
            
            # Create Draw objects
            batch = []
            for letter, timestamp in zip(batch_letters, batch_timestamps):
                draw = Draw(
                    letter=letter,
                    timestamp=timestamp,
                    source="historical_import"
                )
                batch.append(draw)
            
            # Insert batch
            batch_num = (i // BATCH_SIZE) + 1
            inserted = insert_batch(db, batch, batch_num, total_batches)
            inserted_total += inserted
            
            # Progress reporting
            if inserted_total % PROGRESS_INTERVAL == 0:
                progress = (inserted_total / len(valid_letters)) * 100
                print(f"  Progress: {inserted_total:,} / {len(valid_letters):,} ({progress:.1f}%)")
        
        print(f"  ✓ Inserted all {inserted_total:,} rows")
        
        # Final summary
        print("\n" + "=" * 70)
        print("Import Complete!")
        print("=" * 70)
        print(f"Total rows processed: {len(letters):,}")
        print(f"Valid letters inserted: {inserted_total:,}")
        print(f"Invalid rows skipped: {skipped:,}")
        print(f"Source: historical_import")
        print(f"Time span: {time_span.days} days")
        print("=" * 70)
        
        # Verify with ranking
        print("\n9. Verifying data with ranking calculation...")
        ranking = stats.get_ranking(db)
        
        print("\nExpected vs Actual Letter Frequencies:")
        print("-" * 50)
        expected = {
            'A': 38.2, 'B': 21.1, 'C': 13.4, 'D': 12.1,
            'E': 11.0, 'F': 3.6, 'G': 0.7
        }
        
        for entry in ranking:
            letter = entry['letter']
            actual = entry['p_hat'] * 100
            exp = expected[letter]
            diff = actual - exp
            diff_str = f"{diff:+.2f}%"
            
            print(f"{letter}: {actual:6.2f}%  (expected {exp:5.1f}%, diff: {diff_str})")
        
        print("-" * 50)
        print(f"Total draws: {stats.get_total_draws(db):,}")
        
        # Check drift status
        print("\n10. Checking drift detection status...")
        summary = stats.get_drift_summary(db, window_size=5000)
        
        if summary.get('insufficient_data'):
            print(f"  ⓘ Drift detection: Inactive (need {summary['required_draws']:,} draws)")
        else:
            print(f"  ✓ Drift detection: Active")
            print(f"  Any drift detected: {summary['any_drift_detected']}")
            if summary['drifted_letters']:
                print(f"  Drifted letters: {', '.join(summary['drifted_letters'])}")
            if summary['letters_at_risk']:
                print(f"  Letters at risk: {', '.join(summary['letters_at_risk'])}")
        
        print("\n" + "=" * 70)
        print("Import successful! Database ready for analysis.")
        print("=" * 70 + "\n")
        
    except Exception as e:
        print(f"\n✗ Import failed: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
        
    finally:
        db.close()


if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python -m backend.import_historical <path_to_excel_file>")
        print("\nExample:")
        print("  python -m backend.import_historical ~/data/historical_draws.xlsx")
        print("  python -m backend.import_historical ./data/draws.xlsx")
        print("\nExpects Excel file with:")
        print("  - Sheet name: 'Draws'")
        print("  - Column name: 'letter'")
        print("  - Header in row 1, data starting row 2")
        sys.exit(1)
    
    file_path = sys.argv[1]
    
    import_historical_data(file_path)
