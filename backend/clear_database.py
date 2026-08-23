"""
Clear all draws from the database.

This script deletes all rows from the draws table and resets the drift tracker.
Use this to start with a clean database before importing real historical data.

Run with: python -m backend.clear_database
"""

import sys
from backend.database import SessionLocal, init_db
from backend.models import Draw
from backend import stats


def clear_database():
    """Clear all draws and reset drift tracker."""
    print("=" * 70)
    print("Clear Wilsonic Database")
    print("=" * 70)
    
    # Confirm with user
    print("\nWARNING: This will delete ALL draws from the database.")
    response = input("Are you sure you want to continue? (yes/no): ")
    
    if response.lower() != 'yes':
        print("Operation cancelled.")
        return False
    
    # Initialize database
    init_db()
    
    # Create session
    db = SessionLocal()
    
    try:
        # Count current draws
        current_count = db.query(Draw).count()
        print(f"\nCurrent draws in database: {current_count:,}")
        
        if current_count == 0:
            print("Database is already empty.")
            db.close()
            return True
        
        # Delete all draws
        print("\nDeleting all draws...")
        deleted_count = db.query(Draw).delete()
        db.commit()
        
        print(f"✓ Deleted {deleted_count:,} draws")
        
        # Reset drift tracker
        print("\nResetting drift tracker...")
        stats.reset_drift_tracker()
        print("✓ Drift tracker reset")
        
        # Verify
        final_count = db.query(Draw).count()
        print(f"\nFinal draw count: {final_count}")
        
        print("\n" + "=" * 70)
        print("Database cleared successfully!")
        print("=" * 70)
        print("\nThe database is now empty and ready for:")
        print("  - Importing real historical data")
        print("  - Fresh manual entry")
        print("  - Automated scraper (Phase 2)")
        print("=" * 70 + "\n")
        
        return True
        
    except Exception as e:
        print(f"\n✗ Error: {e}")
        db.rollback()
        return False
        
    finally:
        db.close()


if __name__ == "__main__":
    success = clear_database()
    sys.exit(0 if success else 1)
