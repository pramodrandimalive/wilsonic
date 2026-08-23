"""
Example usage of the stats engine functions.

This demonstrates how to use each function from stats.py in a real scenario.

Run with: python -m backend.example_stats_usage
"""

from datetime import datetime, timezone, timedelta
from backend.database import SessionLocal, init_db
from backend.models import Draw
from backend import stats


def populate_sample_data(db, num_draws=1000):
    """
    Populate database with sample draws following realistic distribution.
    
    Based on observed frequencies from 300k historical draws:
    A≈38.2%, B≈21.1%, C≈13.4%, D≈12.1%, E≈11.0%, F≈3.6%, G≈0.7%
    """
    distribution = {
        "A": 382,
        "B": 211,
        "C": 134,
        "D": 121,
        "E": 110,
        "F": 36,
        "G": 6,
    }
    
    # Scale to desired number of draws
    scale = num_draws / 1000
    
    timestamp = datetime.now(timezone.utc)
    
    for letter, base_count in distribution.items():
        count = int(base_count * scale)
        for i in range(count):
            draw = Draw(
                letter=letter,
                timestamp=timestamp - timedelta(minutes=3*i),  # 3 min intervals
                source="manual"
            )
            db.add(draw)
    
    db.commit()
    print(f"✓ Added {num_draws} sample draws to database")


def example_basic_stats():
    """Example: Get basic frequency statistics."""
    print("\n" + "="*70)
    print("EXAMPLE 1: Basic Frequency Statistics")
    print("="*70)
    
    db = SessionLocal()
    
    # Get base frequencies
    frequencies = stats.calculate_base_frequency(db)
    
    print("\nBase frequencies for each letter:")
    print(f"{'Letter':<10} {'Frequency':<15} {'Percentage'}")
    print("-" * 40)
    for letter in stats.VALID_LETTERS:
        freq = frequencies[letter]
        percentage = freq * 100
        print(f"{letter:<10} {freq:<15.6f} {percentage:>6.2f}%")
    
    # Get total draws
    total = stats.get_total_draws(db)
    print(f"\nTotal draws in database: {total:,}")
    
    db.close()


def example_ranking():
    """Example: Get ranked letter list with confidence intervals."""
    print("\n" + "="*70)
    print("EXAMPLE 2: Letter Ranking with Confidence Intervals")
    print("="*70)
    
    db = SessionLocal()
    
    ranking = stats.get_ranking(db)
    
    print("\nLetters ranked by frequency (most to least likely):")
    print(f"{'Rank':<6} {'Letter':<8} {'Frequency':<12} {'95% CI Range':<25} {'Count'}")
    print("-" * 70)
    
    for entry in ranking:
        ci_range = f"[{entry['lower_bound']:.4f}, {entry['upper_bound']:.4f}]"
        print(f"{entry['rank']:<6} {entry['letter']:<8} "
              f"{entry['p_hat']:.6f}    {ci_range:<25} {entry['count']:>6,}")
    
    print("\nInterpretation:")
    print(f"  • {ranking[0]['letter']} is most likely to appear next ({ranking[0]['p_hat']*100:.1f}%)")
    print(f"  • {ranking[-1]['letter']} is least likely to appear next ({ranking[-1]['p_hat']*100:.1f}%)")
    print(f"  • Confidence intervals show statistical uncertainty")
    
    db.close()


def example_rolling_window():
    """Example: Compare recent vs historical frequencies."""
    print("\n" + "="*70)
    print("EXAMPLE 3: Rolling Window (Recent vs Historical)")
    print("="*70)
    
    db = SessionLocal()
    
    # Get historical frequencies
    historical = stats.calculate_base_frequency(db)
    
    # Get recent frequencies (last 500 draws)
    window_size = 500
    recent = stats.calculate_rolling_frequency(db, window_size)
    
    print(f"\nComparing last {window_size} draws to full history:")
    print(f"{'Letter':<10} {'Historical':<15} {'Recent':<15} {'Change'}")
    print("-" * 60)
    
    for letter in stats.VALID_LETTERS:
        hist_pct = historical[letter] * 100
        recent_pct = recent[letter] * 100
        change = recent_pct - hist_pct
        change_str = f"{change:+.2f}%" if abs(change) > 0.01 else "~"
        
        print(f"{letter:<10} {hist_pct:>6.2f}%         {recent_pct:>6.2f}%         {change_str:>8}")
    
    print("\nInterpretation:")
    print(f"  • Recent patterns may differ from long-term averages")
    print(f"  • '+' means letter appearing more frequently recently")
    print(f"  • '-' means letter appearing less frequently recently")
    
    db.close()


def example_drift_detection():
    """Example: Detect if recent frequency has drifted from historical baseline."""
    print("\n" + "="*70)
    print("EXAMPLE 4: Drift Detection")
    print("="*70)
    
    db = SessionLocal()
    
    # Reset drift tracker for fresh analysis
    stats.reset_drift_tracker()
    
    # Get drift status
    drift_status = stats.detect_drift(db, window_size=500)
    
    # Get summary
    summary = stats.get_drift_summary(db, window_size=500)
    
    print(f"\nDrift Analysis (window size: {summary['window_size']}):")
    print(f"  • Any drift detected: {'YES ⚠' if summary['any_drift_detected'] else 'NO ✓'}")
    print(f"  • Drifted letters: {', '.join(summary['drifted_letters']) if summary['drifted_letters'] else 'None'}")
    print(f"  • Letters at risk: {', '.join(summary['letters_at_risk']) if summary['letters_at_risk'] else 'None'}")
    
    print(f"\nDetailed drift status by letter:")
    print(f"{'Letter':<8} {'Status':<15} {'Recent':<10} {'Historical':<12} {'Violations'}")
    print("-" * 65)
    
    for letter in stats.VALID_LETTERS:
        status = drift_status[letter]
        status_str = "DRIFTED ⚠" if status["drift_detected"] else "OK ✓"
        
        print(f"{letter:<8} {status_str:<15} "
              f"{status['p_hat_recent']*100:>5.2f}%    "
              f"{status['p_hat_historical']*100:>5.2f}%       "
              f"{status['consecutive_violations']:>2}")
    
    print("\nInterpretation:")
    print(f"  • Drift flagged when recent frequency is outside historical CI")
    print(f"  • Requires 10+ consecutive violations to avoid false alarms")
    print(f"  • Violations counter resets when frequency returns to normal range")
    
    db.close()


def example_full_workflow():
    """Example: Complete workflow for API endpoint."""
    print("\n" + "="*70)
    print("EXAMPLE 5: Complete Workflow (for API /stats/ranking)")
    print("="*70)
    
    db = SessionLocal()
    
    # Get comprehensive stats
    ranking = stats.get_ranking(db)
    summary = stats.get_drift_summary(db)
    total_draws = stats.get_total_draws(db)
    
    # Simulate API response
    api_response = {
        "total_draws": total_draws,
        "ranking": ranking,
        "drift_alert": summary['any_drift_detected'],
        "drifted_letters": summary['drifted_letters'],
    }
    
    print("\nAPI Response Structure:")
    print("-" * 70)
    print(f"Total draws: {api_response['total_draws']:,}")
    print(f"Drift alert: {api_response['drift_alert']}")
    print(f"\nTop 3 most likely letters:")
    
    for i in range(min(3, len(ranking))):
        entry = ranking[i]
        print(f"  {i+1}. {entry['letter']} - {entry['p_hat']*100:.2f}% "
              f"(CI: {entry['lower_bound']*100:.2f}%-{entry['upper_bound']*100:.2f}%)")
    
    db.close()


def main():
    """Run all examples."""
    print("\n" + "="*70)
    print("WILSONIC STATS ENGINE - USAGE EXAMPLES")
    print("="*70)
    
    # Initialize database
    init_db()
    
    # Clear existing data and populate fresh sample data
    db = SessionLocal()
    db.query(Draw).delete()
    db.commit()
    db.close()
    
    populate_sample_data(SessionLocal(), num_draws=10000)
    
    # Run examples
    example_basic_stats()
    example_ranking()
    example_rolling_window()
    example_drift_detection()
    example_full_workflow()
    
    print("\n" + "="*70)
    print("All examples completed successfully!")
    print("="*70)
    print("\nThese functions are ready to be integrated into API endpoints.")
    print("See backend/api/routes.py for endpoint implementations.")
    print("="*70 + "\n")


if __name__ == "__main__":
    main()
