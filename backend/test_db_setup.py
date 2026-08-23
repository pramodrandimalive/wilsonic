"""
Test script to verify database and model setup.

This script:
1. Creates the database tables
2. Adds a sample draw
3. Queries it back
4. Verifies the setup is working

Run with: python -m backend.test_db_setup
"""

import sys
from datetime import datetime, timezone
from backend.database import engine, SessionLocal, init_db
from backend.models import Draw


def test_database_setup():
    """Test database initialization and basic CRUD operations."""
    
    print("=" * 60)
    print("Wilsonic Database Setup Test")
    print("=" * 60)
    
    # Step 1: Initialize database (create tables)
    print("\n1. Initializing database...")
    try:
        init_db()
        print("   ✓ Database tables created successfully")
    except Exception as e:
        print(f"   ✗ Error creating database: {e}")
        sys.exit(1)
    
    # Step 2: Create a session
    print("\n2. Creating database session...")
    db = SessionLocal()
    print("   ✓ Session created")
    
    # Step 3: Add a sample draw
    print("\n3. Adding sample draw (Letter A)...")
    try:
        sample_draw = Draw(
            letter="A",
            timestamp=datetime.now(timezone.utc),
            source="manual"
        )
        db.add(sample_draw)
        db.commit()
        db.refresh(sample_draw)
        print(f"   ✓ Sample draw added with ID: {sample_draw.id}")
    except Exception as e:
        print(f"   ✗ Error adding draw: {e}")
        db.rollback()
        db.close()
        sys.exit(1)
    
    # Step 4: Query the draw back
    print("\n4. Querying draw from database...")
    try:
        retrieved_draw = db.query(Draw).filter(Draw.id == sample_draw.id).first()
        if retrieved_draw:
            print(f"   ✓ Draw retrieved successfully:")
            print(f"     - ID: {retrieved_draw.id}")
            print(f"     - Letter: {retrieved_draw.letter}")
            print(f"     - Timestamp: {retrieved_draw.timestamp}")
            print(f"     - Source: {retrieved_draw.source}")
        else:
            print("   ✗ Draw not found in database")
            db.close()
            sys.exit(1)
    except Exception as e:
        print(f"   ✗ Error querying draw: {e}")
        db.close()
        sys.exit(1)
    
    # Step 5: Test to_dict method
    print("\n5. Testing model to_dict() method...")
    try:
        draw_dict = retrieved_draw.to_dict()
        print(f"   ✓ Dictionary representation: {draw_dict}")
    except Exception as e:
        print(f"   ✗ Error converting to dict: {e}")
        db.close()
        sys.exit(1)
    
    # Step 6: Count total draws
    print("\n6. Counting total draws in database...")
    try:
        total_draws = db.query(Draw).count()
        print(f"   ✓ Total draws in database: {total_draws}")
    except Exception as e:
        print(f"   ✗ Error counting draws: {e}")
        db.close()
        sys.exit(1)
    
    # Cleanup
    db.close()
    
    print("\n" + "=" * 60)
    print("All tests passed! ✓")
    print("Database setup is working correctly.")
    print("=" * 60)
    print(f"\nDatabase location: backend/wilsonic.db")


if __name__ == "__main__":
    test_database_setup()
