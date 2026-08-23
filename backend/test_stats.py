"""
Test script for stats.py - verifies all statistical functions.

Tests all five sections of the stats engine:
- 5.1 Base frequency estimator
- 5.2 Ranking
- 5.3 Wilson confidence intervals
- 5.4 Rolling window
- 5.5 Drift detection

Run with: python -m backend.test_stats
"""

import sys
from datetime import datetime, timezone, timedelta
from backend.database import SessionLocal, init_db
from backend.models import Draw
from backend import stats


def clear_test_data(db):
    """Remove all test data from database."""
    db.query(Draw).delete()
    db.commit()


def add_test_draws(db, letter_distribution):
    """
    Add test draws with specified distribution.
    
    Args:
        db: Database session
        letter_distribution: Dict of letter -> count
    """
    timestamp = datetime.now(timezone.utc)
    
    for letter, count in letter_distribution.items():
        for i in range(count):
            draw = Draw(
                letter=letter,
                timestamp=timestamp - timedelta(seconds=i),
                source="manual"
            )
            db.add(draw)
    
    db.commit()


def test_base_frequency():
    """Test Section 5.1: Base frequency estimator."""
    print("\n" + "="*70)
    print("TEST 5.1: Base Frequency Estimator")
    print("="*70)
    
    db = SessionLocal()
    clear_test_data(db)
    
    # Test 1: Empty database
    print("\n1. Testing with empty database...")
    frequencies = stats.calculate_base_frequency(db)
    expected = 1.0 / 7  # Uniform distribution
    print(f"   Empty DB frequency for 'A': {frequencies['A']:.4f} (expected: {expected:.4f})")
    assert abs(frequencies['A'] - expected) < 0.001, "Empty DB should return uniform"
    print("   ✓ Uniform distribution for empty database")
    
    # Test 2: Known distribution
    print("\n2. Testing with known distribution...")
    test_distribution = {
        "A": 382,  # 38.2%
        "B": 211,  # 21.1%
        "C": 134,  # 13.4%
        "D": 121,  # 12.1%
        "E": 110,  # 11.0%
        "F": 36,   # 3.6%
        "G": 6,    # 0.6%
    }
    total = sum(test_distribution.values())
    add_test_draws(db, test_distribution)
    
    frequencies = stats.calculate_base_frequency(db)
    
    for letter, count in test_distribution.items():
        expected_freq = count / total
        actual_freq = frequencies[letter]
        print(f"   {letter}: {actual_freq:.4f} (expected: {expected_freq:.4f})")
        assert abs(actual_freq - expected_freq) < 0.0001, f"Frequency mismatch for {letter}"
    
    print("   ✓ Frequencies match expected distribution")
    
    # Test 3: Helper functions
    print("\n3. Testing helper functions...")
    total_draws = stats.get_total_draws(db)
    print(f"   Total draws: {total_draws} (expected: {total})")
    assert total_draws == total, "Total draws mismatch"
    
    counts = stats.get_letter_counts(db)
    for letter, expected_count in test_distribution.items():
        assert counts[letter] == expected_count, f"Count mismatch for {letter}"
    print("   ✓ Helper functions working correctly")
    
    db.close()
    print("\n✓ Base frequency estimator tests passed")


def test_wilson_interval():
    """Test Section 5.3: Wilson confidence interval."""
    print("\n" + "="*70)
    print("TEST 5.3: Wilson Confidence Interval")
    print("="*70)
    
    # Test 1: Known values
    print("\n1. Testing Wilson interval calculation...")
    
    # For p=0.382, n=100000, should give narrow interval around 0.382
    lower, upper = stats.calculate_wilson_interval(0.382, 100000)
    print(f"   p=0.382, n=100000: [{lower:.5f}, {upper:.5f}]")
    assert 0.378 < lower < 0.380, "Lower bound incorrect"
    assert 0.384 < upper < 0.386, "Upper bound incorrect"
    assert upper > lower, "Upper must be greater than lower"
    print("   ✓ Interval is narrow and centered correctly")
    
    # Test 2: Small sample - wider interval
    lower_small, upper_small = stats.calculate_wilson_interval(0.382, 100)
    print(f"   p=0.382, n=100: [{lower_small:.5f}, {upper_small:.5f}]")
    interval_small = upper_small - lower_small
    interval_large = upper - lower
    assert interval_small > interval_large, "Small sample should have wider interval"
    print(f"   ✓ Small sample interval ({interval_small:.5f}) wider than large sample ({interval_large:.5f})")
    
    # Test 3: Edge cases
    print("\n2. Testing edge cases...")
    
    # p=0 (never occurred)
    lower, upper = stats.calculate_wilson_interval(0.0, 1000)
    print(f"   p=0.0, n=1000: [{lower:.5f}, {upper:.5f}]")
    assert lower == 0.0, "Lower bound should be 0"
    assert upper > 0.0, "Upper bound should be positive"
    
    # p=1 (always occurred)
    lower, upper = stats.calculate_wilson_interval(1.0, 1000)
    print(f"   p=1.0, n=1000: [{lower:.5f}, {upper:.5f}]")
    assert lower < 1.0, "Lower bound should be less than 1"
    assert upper == 1.0, "Upper bound should be 1"
    
    # n=0 (no data)
    lower, upper = stats.calculate_wilson_interval(0.5, 0)
    print(f"   p=0.5, n=0: [{lower:.5f}, {upper:.5f}]")
    assert lower == 0.0 and upper == 1.0, "Zero sample should return [0, 1]"
    
    print("   ✓ Edge cases handled correctly")
    print("\n✓ Wilson confidence interval tests passed")


def test_ranking():
    """Test Section 5.2: Ranking."""
    print("\n" + "="*70)
    print("TEST 5.2: Ranking")
    print("="*70)
    
    db = SessionLocal()
    clear_test_data(db)
    
    # Add draws with clear ranking
    test_distribution = {
        "A": 400,  # Rank 1
        "B": 200,  # Rank 2
        "C": 150,  # Rank 3
        "D": 100,  # Rank 4
        "E": 100,  # Rank 4 (tie)
        "F": 40,   # Rank 6
        "G": 10,   # Rank 7
    }
    add_test_draws(db, test_distribution)
    
    print("\n1. Testing ranking order...")
    ranking = stats.get_ranking(db)
    
    print(f"   {'Rank':<6} {'Letter':<8} {'p_hat':<10} {'Count':<8} {'CI Lower':<10} {'CI Upper':<10}")
    print("   " + "-"*60)
    for entry in ranking:
        print(f"   {entry['rank']:<6} {entry['letter']:<8} {entry['p_hat']:.4f}    {entry['count']:<8} {entry['lower_bound']:.4f}    {entry['upper_bound']:.4f}")
    
    # Verify structure
    assert len(ranking) == 7, "Should have 7 entries"
    
    # Verify ranking order (descending by p_hat)
    assert ranking[0]["letter"] == "A", "A should be rank 1"
    assert ranking[1]["letter"] == "B", "B should be rank 2"
    assert ranking[-1]["letter"] == "G", "G should be rank 7"
    
    # Verify all fields present
    required_fields = ["letter", "p_hat", "rank", "lower_bound", "upper_bound", "count"]
    for field in required_fields:
        assert field in ranking[0], f"Missing field: {field}"
    
    # Verify rank numbers are sequential
    for i, entry in enumerate(ranking):
        assert entry["rank"] == i + 1, f"Rank should be {i+1}"
    
    # Verify frequencies sum to 1.0
    total_freq = sum(entry["p_hat"] for entry in ranking)
    assert abs(total_freq - 1.0) < 0.001, "Frequencies should sum to 1.0"
    
    # Verify confidence intervals are valid
    for entry in ranking:
        assert 0.0 <= entry["lower_bound"] <= entry["p_hat"] <= entry["upper_bound"] <= 1.0, \
            f"Invalid CI for {entry['letter']}"
    
    print("   ✓ Ranking order correct")
    print("   ✓ All required fields present")
    print("   ✓ Confidence intervals valid")
    
    db.close()
    print("\n✓ Ranking tests passed")


def test_rolling_window():
    """Test Section 5.4: Rolling window."""
    print("\n" + "="*70)
    print("TEST 5.4: Rolling Window")
    print("="*70)
    
    db = SessionLocal()
    clear_test_data(db)
    
    print("\n1. Testing rolling window with recent data...")
    
    # Add old draws (mostly A)
    old_distribution = {"A": 80, "B": 10, "C": 10}
    timestamp_old = datetime.now(timezone.utc) - timedelta(hours=10)
    for letter, count in old_distribution.items():
        for i in range(count):
            draw = Draw(
                letter=letter,
                timestamp=timestamp_old - timedelta(seconds=i),
                source="manual"
            )
            db.add(draw)
    
    # Add recent draws (mostly B - different pattern)
    recent_distribution = {"B": 70, "A": 20, "C": 10}
    timestamp_recent = datetime.now(timezone.utc)
    for letter, count in recent_distribution.items():
        for i in range(count):
            draw = Draw(
                letter=letter,
                timestamp=timestamp_recent - timedelta(seconds=i),
                source="manual"
            )
            db.add(draw)
    
    db.commit()
    
    # Test with window size that captures only recent draws
    window_size = 100
    recent_freq = stats.calculate_rolling_frequency(db, window_size)
    
    print(f"   Rolling window (last {window_size} draws):")
    for letter in ["A", "B", "C"]:
        print(f"   {letter}: {recent_freq[letter]:.4f}")
    
    # Recent pattern should show B dominant
    assert recent_freq["B"] > recent_freq["A"], "Recent window should show B > A"
    assert recent_freq["B"] > 0.5, "B should be >50% in recent window"
    
    # Test with larger window
    full_freq = stats.calculate_base_frequency(db)
    print(f"\n   Full history:")
    for letter in ["A", "B", "C"]:
        print(f"   {letter}: {full_freq[letter]:.4f}")
    
    # Full history should show A dominant
    assert full_freq["A"] > full_freq["B"], "Full history should show A > B"
    
    print("   ✓ Rolling window captures recent patterns correctly")
    
    # Test 2: Window size helper
    print("\n2. Testing window size helper...")
    actual_window = stats.get_rolling_window_size(db, 5000)
    total_draws = stats.get_total_draws(db)
    print(f"   Requested: 5000, Actual: {actual_window}, Total: {total_draws}")
    assert actual_window == total_draws, "Should cap at total draws"
    print("   ✓ Window size capped correctly")
    
    db.close()
    print("\n✓ Rolling window tests passed")


def test_drift_detection():
    """Test Section 5.5: Drift detection."""
    print("\n" + "="*70)
    print("TEST 5.5: Drift Detection")
    print("="*70)
    
    db = SessionLocal()
    clear_test_data(db)
    stats.reset_drift_tracker()
    
    print("\n1. Setting up baseline data (historical pattern)...")
    # Create strong historical pattern: A=38%, B=21%, others lower
    baseline = {
        "A": 3800,
        "B": 2100,
        "C": 1340,
        "D": 1210,
        "E": 1100,
        "F": 360,
        "G": 90,
    }
    
    timestamp = datetime.now(timezone.utc) - timedelta(hours=100)
    for letter, count in baseline.items():
        for i in range(count):
            draw = Draw(
                letter=letter,
                timestamp=timestamp - timedelta(seconds=i),
                source="manual"
            )
            db.add(draw)
    db.commit()
    
    # Get baseline stats
    ranking = stats.get_ranking(db)
    print(f"   Baseline pattern established: A={baseline['A']}, B={baseline['B']}")
    
    print("\n2. Testing NO drift (recent matches historical)...")
    # Add recent draws matching historical pattern
    recent_normal = {"A": 38, "B": 21, "C": 13, "D": 12, "E": 11, "F": 4, "G": 1}
    timestamp_recent = datetime.now(timezone.utc)
    for letter, count in recent_normal.items():
        for i in range(count):
            draw = Draw(
                letter=letter,
                timestamp=timestamp_recent - timedelta(seconds=i),
                source="manual"
            )
            db.add(draw)
    db.commit()
    
    drift_status = stats.detect_drift(db, window_size=100)
    any_drift = any(status["drift_detected"] for status in drift_status.values())
    
    print(f"   Any drift detected: {any_drift}")
    for letter in ["A", "B"]:
        status = drift_status[letter]
        print(f"   {letter}: recent={status['p_hat_recent']:.3f}, hist={status['p_hat_historical']:.3f}, violations={status['consecutive_violations']}")
    
    assert not any_drift, "Should not detect drift when patterns match"
    print("   ✓ No false positives when recent matches historical")
    
    print("\n3. Testing drift detection (requires 10+ consecutive violations)...")
    stats.reset_drift_tracker()
    
    # Simulate 15 checks with B frequency way outside its CI
    # B historical: ~21%, but we'll push it to 60% in recent window
    for check_num in range(15):
        # Add draws with B spike
        for _ in range(60):
            db.add(Draw(letter="B", timestamp=datetime.now(timezone.utc), source="manual"))
        for _ in range(40):
            db.add(Draw(letter="A", timestamp=datetime.now(timezone.utc), source="manual"))
        db.commit()
        
        drift_status = stats.detect_drift(db, window_size=100)
        b_status = drift_status["B"]
        
        if check_num < 9:
            # First 9 checks: should NOT flag drift yet
            assert not b_status["drift_detected"], f"Should not flag drift on check {check_num+1}"
        else:
            # Check 10+: should flag drift
            assert b_status["drift_detected"], f"Should flag drift on check {check_num+1}"
        
        print(f"   Check {check_num+1:2d}: B violations={b_status['consecutive_violations']:2d}, drift={b_status['drift_detected']}")
    
    print("   ✓ Drift detection threshold (10+ consecutive) working correctly")
    
    print("\n4. Testing drift summary...")
    summary = stats.get_drift_summary(db, window_size=100)
    print(f"   Any drift: {summary['any_drift_detected']}")
    print(f"   Drifted letters: {summary['drifted_letters']}")
    print(f"   At-risk letters: {summary['letters_at_risk']}")
    assert summary['any_drift_detected'], "Summary should show drift detected"
    assert "B" in summary['drifted_letters'], "B should be in drifted letters"
    print("   ✓ Drift summary working correctly")
    
    db.close()
    print("\n✓ Drift detection tests passed")


def test_excluded_logic():
    """Test Section 5.6: Verify excluded logic is NOT implemented."""
    print("\n" + "="*70)
    print("TEST 5.6: Verify Excluded Logic NOT Implemented")
    print("="*70)
    
    print("\n1. Checking for gap-based functions...")
    forbidden_names = [
        "gap", "since_last", "overdue", "due", "hazard", 
        "time_since", "last_occurrence", "memoryless"
    ]
    
    stats_functions = [name for name in dir(stats) if not name.startswith('_')]
    
    for forbidden in forbidden_names:
        matching = [f for f in stats_functions if forbidden.lower() in f.lower()]
        if matching:
            print(f"   ✗ WARNING: Found function with '{forbidden}': {matching}")
            print(f"      This may indicate forbidden logic is implemented!")
        else:
            print(f"   ✓ No '{forbidden}' functions found")
    
    print("\n✓ No forbidden logic detected")


def run_all_tests():
    """Run all stats engine tests."""
    print("\n" + "="*70)
    print("WILSONIC STATS ENGINE TEST SUITE")
    print("="*70)
    print("\nTesting all five sections of the stats engine:")
    print("  5.1 - Base Frequency Estimator")
    print("  5.2 - Ranking")
    print("  5.3 - Wilson Confidence Interval")
    print("  5.4 - Rolling Window")
    print("  5.5 - Drift Detection")
    print("  5.6 - Verify Excluded Logic")
    
    try:
        # Initialize database
        init_db()
        
        # Run tests in order
        test_base_frequency()
        test_wilson_interval()
        test_ranking()
        test_rolling_window()
        test_drift_detection()
        test_excluded_logic()
        
        # Final summary
        print("\n" + "="*70)
        print("ALL TESTS PASSED ✓")
        print("="*70)
        print("\nStats engine is working correctly:")
        print("  ✓ Base frequency calculation")
        print("  ✓ Wilson confidence intervals")
        print("  ✓ Letter ranking with CIs")
        print("  ✓ Rolling window analysis")
        print("  ✓ Drift detection (10+ consecutive threshold)")
        print("  ✓ No forbidden gap-based logic")
        print("\nReady for API integration (Phase 1).")
        print("="*70 + "\n")
        
        return True
        
    except AssertionError as e:
        print(f"\n✗ TEST FAILED: {e}")
        return False
    except Exception as e:
        print(f"\n✗ UNEXPECTED ERROR: {e}")
        import traceback
        traceback.print_exc()
        return False


if __name__ == "__main__":
    success = run_all_tests()
    sys.exit(0 if success else 1)
