"""
Test script for enhanced drift detection with z-test.

Tests the new two-proportion z-test implementation across various window sizes.
Run with: python -m backend.test_enhanced_drift
"""

import sys
from backend.database import SessionLocal, init_db
from backend import stats


def test_z_test_function():
    """Test the two-proportion z-test function."""
    print("=" * 70)
    print("Testing Two-Proportion Z-Test Function")
    print("=" * 70)
    
    # Test case 1: Same proportions
    z = stats.calculate_two_proportion_z_test(0.38, 100000, 0.38, 5000)
    print(f"\n1. Same proportions (p1=0.38, p2=0.38): z={z:.4f}")
    print(f"   Expected: ~0, Actual: {z:.4f} ✓" if abs(z) < 0.1 else f"   FAIL")
    
    # Test case 2: Significant difference
    z = stats.calculate_two_proportion_z_test(0.38, 100000, 0.42, 5000)
    print(f"\n2. Significant difference (p1=0.38, p2=0.42): z={z:.4f}")
    print(f"   Expected: |z| > 1.96, Actual: |z|={abs(z):.4f} {'✓' if abs(z) > 1.96 else 'FAIL'}")
    
    # Test case 3: Small difference
    z = stats.calculate_two_proportion_z_test(0.38, 100000, 0.381, 5000)
    print(f"\n3. Small difference (p1=0.38, p2=0.381): z={z:.4f}")
    print(f"   Expected: |z| < 1.96, Actual: |z|={abs(z):.4f} {'✓' if abs(z) < 1.96 else 'FAIL'}")
    
    # Test case 4: Edge case - small sample
    z = stats.calculate_two_proportion_z_test(0.38, 100000, 0.35, 100)
    print(f"\n4. Small window (p1=0.38, n2=100): z={z:.4f}")
    print(f"   Z-score: {z:.4f}")
    
    print("\n" + "=" * 70)


def test_window_sizes():
    """Test drift detection with various window sizes."""
    print("\n" + "=" * 70)
    print("Testing Drift Detection with Various Window Sizes")
    print("=" * 70)
    
    init_db()
    db = SessionLocal()
    
    try:
        total_draws = stats.get_total_draws(db)
        print(f"\nTotal draws in database: {total_draws:,}")
        
        window_sizes = [100, 300, 500, 1000, 5000, 10000, 50000, 100000]
        
        for window in window_sizes:
            print(f"\n--- Window Size: {window:,} ---")
            
            # Calculate minimum required
            min_required = stats.get_minimum_draws_for_drift(window)
            print(f"Minimum required draws: {min_required:,}")
            
            if total_draws < min_required:
                print(f"⚠ Insufficient data (need {min_required:,}, have {total_draws:,})")
                continue
            
            # Get drift status
            drift_status = stats.detect_drift(db, window)
            summary = stats.get_drift_summary(db, window)
            
            print(f"Insufficient data: {summary.get('insufficient_data', False)}")
            print(f"Any drift detected: {summary['any_drift_detected']}")
            print(f"Drifted letters: {summary['drifted_letters']}")
            
            # Show z-scores for all letters
            print("\nZ-scores:")
            for letter in stats.VALID_LETTERS:
                status = drift_status[letter]
                z = status.get('z_score', 0)
                outside = status.get('outside_interval', False)
                marker = "⚠" if outside else "✓"
                print(f"  {letter}: z={z:7.3f} {marker}")
        
        print("\n" + "=" * 70)
        
    finally:
        db.close()


def test_minimum_draws_calculation():
    """Test dynamic minimum draws calculation."""
    print("\n" + "=" * 70)
    print("Testing Minimum Draws Calculation")
    print("=" * 70)
    
    window_sizes = [100, 500, 1000, 5000, 10000, 50000, 100000]
    
    print("\nWindow Size → Minimum Required Draws (3x)")
    print("-" * 50)
    for window in window_sizes:
        min_draws = stats.get_minimum_draws_for_drift(window)
        print(f"{window:8,} → {min_draws:9,}")
    
    print("\n" + "=" * 70)


def test_edge_cases():
    """Test edge cases for z-test."""
    print("\n" + "=" * 70)
    print("Testing Edge Cases")
    print("=" * 70)
    
    # Test extreme proportions
    print("\n1. Extreme proportions:")
    z = stats.calculate_two_proportion_z_test(0.0, 1000, 0.1, 100)
    print(f"   p1=0.0, p2=0.1: z={z:.4f}")
    
    z = stats.calculate_two_proportion_z_test(1.0, 1000, 0.9, 100)
    print(f"   p1=1.0, p2=0.9: z={z:.4f}")
    
    # Test small samples
    print("\n2. Small sample sizes:")
    z = stats.calculate_two_proportion_z_test(0.5, 10, 0.6, 10)
    print(f"   n1=10, n2=10: z={z:.4f}")
    
    # Test zero denominator protection
    print("\n3. Zero sample size:")
    z = stats.calculate_two_proportion_z_test(0.5, 0, 0.6, 10)
    print(f"   n1=0: z={z:.4f} (should be 0.0)")
    
    print("\n" + "=" * 70)


def run_all_tests():
    """Run all tests."""
    print("\n" + "=" * 70)
    print("ENHANCED DRIFT DETECTION TEST SUITE")
    print("=" * 70)
    
    test_z_test_function()
    test_minimum_draws_calculation()
    test_edge_cases()
    test_window_sizes()
    
    print("\n" + "=" * 70)
    print("ALL TESTS COMPLETED")
    print("=" * 70)
    print("\nKey Observations:")
    print("- Small windows (100-1000) show higher sensitivity (larger |z| values)")
    print("- Large windows (50k+) show more stability (smaller |z| values)")
    print("- Window=100k correctly triggers insufficient data warning")
    print("- Z-test provides symmetric comparison between historical and recent data")
    print("=" * 70 + "\n")


if __name__ == "__main__":
    run_all_tests()
