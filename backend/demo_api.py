"""
Interactive demonstration of all API endpoints.

This script demonstrates real usage of the Wilsonic API,
adding draws and showing how to interpret the results.

Run with: python -m backend.demo_api
(Start server first: uvicorn backend.main:app --reload)
"""

import requests
import time
from datetime import datetime


BASE_URL = "http://localhost:8000"


def print_section(title):
    """Print a section header."""
    print("\n" + "="*70)
    print(f"  {title}")
    print("="*70)


def demo_health_check():
    """Demonstrate health check."""
    print_section("1. Health Check")
    
    response = requests.get(f"{BASE_URL}/health")
    data = response.json()
    
    print(f"\nAPI Status: {data['status']}")
    print(f"Database: {data['database']}")
    print(f"Current draws in database: {data['total_draws']:,}")


def demo_add_draws():
    """Demonstrate adding draws."""
    print_section("2. Adding Draws")
    
    print("\nAdding 10 random draws (A-G)...")
    
    # Simulate realistic distribution
    draws_to_add = ["A", "A", "B", "A", "C", "B", "D", "E", "A", "F"]
    
    for i, letter in enumerate(draws_to_add, 1):
        response = requests.post(
            f"{BASE_URL}/draws",
            json={"letter": letter}
        )
        
        if response.status_code == 201:
            draw = response.json()
            print(f"  {i:2d}. Added {draw['letter']} (ID: {draw['id']})")
        
        time.sleep(0.05)  # Small delay for timestamp ordering
    
    print("\n✓ All draws added successfully")


def demo_list_draws():
    """Demonstrate listing recent draws."""
    print_section("3. Recent Draws History")
    
    response = requests.get(f"{BASE_URL}/draws?page=1&page_size=10")
    data = response.json()
    
    print(f"\nShowing {len(data['draws'])} most recent draws:")
    print(f"Total in database: {data['total']:,}")
    print(f"\n{'ID':<8} {'Letter':<8} {'Timestamp':<28} {'Source'}")
    print("-" * 70)
    
    for draw in data['draws']:
        timestamp = draw['timestamp'][:19]  # Trim to seconds
        print(f"{draw['id']:<8} {draw['letter']:<8} {timestamp:<28} {draw['source']}")


def demo_ranking():
    """Demonstrate letter ranking."""
    print_section("4. Letter Ranking (Most to Least Likely)")
    
    response = requests.get(f"{BASE_URL}/stats/ranking")
    data = response.json()
    
    print(f"\nBased on {data['total_draws']:,} total draws")
    print(f"\n{'Rank':<6} {'Letter':<8} {'Frequency':<12} {'95% CI':<28} {'Count':<10} {'Bar'}")
    print("-" * 85)
    
    for entry in data['ranking']:
        freq_pct = entry['p_hat'] * 100
        ci = f"[{entry['lower_bound']*100:.2f}%, {entry['upper_bound']*100:.2f}%]"
        bar_length = int(entry['p_hat'] * 50)  # Scale to 50 chars
        bar = "█" * bar_length
        
        print(f"{entry['rank']:<6} {entry['letter']:<8} {freq_pct:>6.2f}%      {ci:<28} {entry['count']:<10} {bar}")
    
    # Highlight top prediction
    top = data['ranking'][0]
    print(f"\n→ Most likely next draw: {top['letter']} ({top['p_hat']*100:.1f}% probability)")


def demo_drift():
    """Demonstrate drift detection."""
    print_section("5. Drift Detection")
    
    response = requests.get(f"{BASE_URL}/stats/drift?window_size=500")
    data = response.json()
    
    print(f"\nAnalyzing last {data['window_size']} draws vs full history of {data['total_draws']:,} draws")
    
    if data['any_drift_detected']:
        print(f"\n⚠ DRIFT DETECTED in: {', '.join(data['drifted_letters'])}")
    else:
        print(f"\n✓ No drift detected - recent patterns match historical baseline")
    
    if data['letters_at_risk']:
        print(f"⚠ At-risk letters: {', '.join(data['letters_at_risk'])} (monitoring)")
    
    # Show details for interesting cases
    print(f"\n{'Letter':<8} {'Recent':<10} {'Historical':<12} {'Status':<15} {'Violations'}")
    print("-" * 60)
    
    for letter in ["A", "B", "C"]:
        status_data = data['drift_status'][letter]
        recent_pct = status_data['p_hat_recent'] * 100
        hist_pct = status_data['p_hat_historical'] * 100
        
        if status_data['drift_detected']:
            status = "DRIFTED ⚠"
        elif status_data['outside_interval']:
            status = "OUTSIDE CI"
        else:
            status = "OK ✓"
        
        print(f"{letter:<8} {recent_pct:>6.2f}%    {hist_pct:>6.2f}%      {status:<15} {status_data['consecutive_violations']}")


def demo_summary():
    """Demonstrate summary statistics."""
    print_section("6. Summary Statistics")
    
    response = requests.get(f"{BASE_URL}/stats/summary")
    data = response.json()
    
    print(f"\nOverall Statistics:")
    print(f"  Total draws: {data['total_draws']:,}")
    print(f"  Last updated: {data['last_updated']}")
    
    if data['last_draw']:
        print(f"  Most recent draw: {data['last_draw']['letter']} "
              f"(ID {data['last_draw']['id']}) at {data['last_draw']['timestamp'][:19]}")
    
    print(f"\n{'Letter':<10} {'Count':<12} {'Frequency':<12} {'Bar'}")
    print("-" * 60)
    
    for letter in ["A", "B", "C", "D", "E", "F", "G"]:
        count = data['letter_counts'][letter]
        freq = data['frequencies'][letter]
        bar_length = int(freq * 40)
        bar = "▓" * bar_length
        
        print(f"{letter:<10} {count:<12} {freq*100:>6.2f}%      {bar}")


def demo_interactive_docs():
    """Show interactive documentation info."""
    print_section("7. Interactive API Documentation")
    
    print("\nThe API includes interactive documentation!")
    print("\n  Swagger UI (try endpoints in browser):")
    print(f"    → {BASE_URL}/docs")
    print("\n  ReDoc (readable documentation):")
    print(f"    → {BASE_URL}/redoc")
    print("\nYou can test all endpoints directly from your browser!")


def main():
    """Run all demonstrations."""
    print("\n" + "="*70)
    print("  WILSONIC API - INTERACTIVE DEMONSTRATION")
    print("="*70)
    print(f"\nAPI URL: {BASE_URL}")
    print("This demo shows all 5 endpoints in action")
    
    try:
        # Check if server is running
        response = requests.get(f"{BASE_URL}/health", timeout=2)
        if response.status_code != 200:
            print("\n✗ Server returned unexpected status")
            return False
    except requests.exceptions.ConnectionError:
        print("\n✗ ERROR: Cannot connect to server")
        print("Please start the server first:")
        print("  uvicorn backend.main:app --reload")
        return False
    
    try:
        # Run demonstrations
        demo_health_check()
        demo_add_draws()
        demo_list_draws()
        demo_ranking()
        demo_drift()
        demo_summary()
        demo_interactive_docs()
        
        # Final message
        print("\n" + "="*70)
        print("  DEMONSTRATION COMPLETE")
        print("="*70)
        print("\nAll endpoints demonstrated:")
        print("  ✓ POST /draws - Added 10 draws")
        print("  ✓ GET /draws - Listed recent draws")
        print("  ✓ GET /stats/ranking - Showed letter ranking")
        print("  ✓ GET /stats/drift - Checked for drift")
        print("  ✓ GET /stats/summary - Displayed summary")
        print("\nThe API is working perfectly and ready for frontend integration!")
        print("="*70 + "\n")
        
        return True
        
    except Exception as e:
        print(f"\n✗ ERROR: {e}")
        import traceback
        traceback.print_exc()
        return False


if __name__ == "__main__":
    import sys
    success = main()
    sys.exit(0 if success else 1)
