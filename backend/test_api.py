"""
Test script for API endpoints.

Tests all 5 endpoints from Section 6:
- POST /draws
- GET /draws
- GET /stats/ranking
- GET /stats/drift
- GET /stats/summary

Run with: python -m backend.test_api
(Start server first: uvicorn backend.main:app --reload)
"""

import sys
import time
import requests
from datetime import datetime, timezone


BASE_URL = "http://localhost:8000"


def print_section(title):
    """Print a section header."""
    print("\n" + "="*70)
    print(f"{title}")
    print("="*70)


def test_root():
    """Test root endpoint."""
    print_section("TEST: GET / (Root)")
    
    response = requests.get(f"{BASE_URL}/")
    print(f"Status: {response.status_code}")
    print(f"Response: {response.json()}")
    
    assert response.status_code == 200, "Root endpoint should return 200"
    print("✓ Root endpoint working")


def test_health():
    """Test health check endpoint."""
    print_section("TEST: GET /health")
    
    response = requests.get(f"{BASE_URL}/health")
    print(f"Status: {response.status_code}")
    data = response.json()
    print(f"Response: {data}")
    
    assert response.status_code == 200, "Health check should return 200"
    assert data["status"] == "healthy", "Status should be healthy"
    print("✓ Health check working")


def test_create_draw():
    """Test POST /draws endpoint."""
    print_section("TEST: POST /draws (Create Draw)")
    
    # Test 1: Valid draw
    print("\n1. Creating valid draw (Letter A)...")
    payload = {"letter": "A"}
    response = requests.post(f"{BASE_URL}/draws", json=payload)
    print(f"Status: {response.status_code}")
    data = response.json()
    print(f"Response: {data}")
    
    assert response.status_code == 201, "Should return 201 Created"
    assert data["letter"] == "A", "Letter should be A"
    assert data["source"] == "manual", "Source should be manual"
    assert "id" in data, "Should have ID"
    print("✓ Valid draw created successfully")
    
    # Test 2: Invalid letter
    print("\n2. Testing invalid letter (should fail)...")
    payload = {"letter": "Z"}
    response = requests.post(f"{BASE_URL}/draws", json=payload)
    print(f"Status: {response.status_code}")
    print(f"Response: {response.json()}")
    
    assert response.status_code == 422, "Should return 422 for invalid letter"
    print("✓ Invalid letter rejected correctly")
    
    # Test 3: Create multiple draws for testing
    print("\n3. Creating test draws (A, B, C)...")
    for letter in ["A", "A", "B", "C", "A"]:
        payload = {"letter": letter}
        response = requests.post(f"{BASE_URL}/draws", json=payload)
        assert response.status_code == 201, f"Failed to create draw {letter}"
        time.sleep(0.1)  # Small delay for timestamp ordering
    print("✓ Multiple test draws created")


def test_list_draws():
    """Test GET /draws endpoint."""
    print_section("TEST: GET /draws (List Draws)")
    
    # Test 1: Default pagination
    print("\n1. Fetching draws (default pagination)...")
    response = requests.get(f"{BASE_URL}/draws")
    print(f"Status: {response.status_code}")
    data = response.json()
    print(f"Total: {data['total']}, Page: {data['page']}, Page Size: {data['page_size']}")
    print(f"First draw: {data['draws'][0] if data['draws'] else 'None'}")
    
    assert response.status_code == 200, "Should return 200"
    assert "draws" in data, "Should have draws list"
    assert "total" in data, "Should have total count"
    assert data["total"] > 0, "Should have at least one draw"
    print("✓ Draws list retrieved successfully")
    
    # Test 2: Custom pagination
    print("\n2. Testing pagination (page_size=2)...")
    response = requests.get(f"{BASE_URL}/draws?page=1&page_size=2")
    data = response.json()
    print(f"Returned {len(data['draws'])} draws (max 2)")
    print(f"Total pages: {data['total_pages']}")
    
    assert len(data['draws']) <= 2, "Should return at most 2 draws"
    print("✓ Pagination working correctly")


def test_ranking():
    """Test GET /stats/ranking endpoint."""
    print_section("TEST: GET /stats/ranking")
    
    response = requests.get(f"{BASE_URL}/stats/ranking")
    print(f"Status: {response.status_code}")
    data = response.json()
    
    print(f"\nTotal draws: {data['total_draws']}")
    print(f"\nRanking (top 5):")
    print(f"{'Rank':<6} {'Letter':<8} {'Frequency':<12} {'95% CI':<25} {'Count'}")
    print("-" * 70)
    
    for entry in data['ranking'][:5]:
        ci = f"[{entry['lower_bound']:.4f}, {entry['upper_bound']:.4f}]"
        print(f"{entry['rank']:<6} {entry['letter']:<8} {entry['p_hat']:.6f}    {ci:<25} {entry['count']}")
    
    assert response.status_code == 200, "Should return 200"
    assert len(data['ranking']) == 7, "Should have 7 letters"
    assert data['ranking'][0]['rank'] == 1, "First entry should be rank 1"
    assert data['ranking'][0]['p_hat'] >= data['ranking'][1]['p_hat'], "Should be sorted by frequency"
    print("\n✓ Ranking retrieved successfully")


def test_drift():
    """Test GET /stats/drift endpoint."""
    print_section("TEST: GET /stats/drift")
    
    # Test 1: Default window size
    print("\n1. Checking drift status (default window)...")
    response = requests.get(f"{BASE_URL}/stats/drift")
    print(f"Status: {response.status_code}")
    data = response.json()
    
    print(f"\nDrift Summary:")
    print(f"  Any drift detected: {data['any_drift_detected']}")
    print(f"  Drifted letters: {data['drifted_letters']}")
    print(f"  At-risk letters: {data['letters_at_risk']}")
    print(f"  Window size: {data['window_size']}")
    print(f"  Total draws: {data['total_draws']}")
    
    assert response.status_code == 200, "Should return 200"
    assert "drift_status" in data, "Should have drift_status dict"
    print("✓ Drift status retrieved successfully")
    
    # Test 2: Custom window size
    print("\n2. Testing custom window size (100)...")
    response = requests.get(f"{BASE_URL}/stats/drift?window_size=100")
    data = response.json()
    print(f"  Window size: {data['window_size']}")
    assert data['window_size'] <= 100, "Window should be capped at requested or total"
    print("✓ Custom window size working")


def test_summary():
    """Test GET /stats/summary endpoint."""
    print_section("TEST: GET /stats/summary")
    
    response = requests.get(f"{BASE_URL}/stats/summary")
    print(f"Status: {response.status_code}")
    data = response.json()
    
    print(f"\nSummary:")
    print(f"  Total draws: {data['total_draws']}")
    print(f"  Last updated: {data['last_updated']}")
    
    print(f"\n  Letter counts:")
    for letter in ["A", "B", "C", "D", "E", "F", "G"]:
        count = data['letter_counts'].get(letter, 0)
        freq = data['frequencies'].get(letter, 0)
        print(f"    {letter}: {count} ({freq*100:.2f}%)")
    
    if data['last_draw']:
        print(f"\n  Last draw: {data['last_draw']['letter']} at {data['last_draw']['timestamp']}")
    
    assert response.status_code == 200, "Should return 200"
    assert data['total_draws'] > 0, "Should have draws"
    assert len(data['letter_counts']) == 7, "Should have counts for all 7 letters"
    print("\n✓ Summary retrieved successfully")


def test_error_handling():
    """Test error handling."""
    print_section("TEST: Error Handling")
    
    # Test 1: Invalid endpoint
    print("\n1. Testing invalid endpoint...")
    response = requests.get(f"{BASE_URL}/invalid")
    print(f"Status: {response.status_code}")
    assert response.status_code == 404, "Should return 404 for invalid endpoint"
    print("✓ 404 for invalid endpoint")
    
    # Test 2: Invalid query parameter
    print("\n2. Testing invalid query parameter...")
    response = requests.get(f"{BASE_URL}/draws?page=-1")
    print(f"Status: {response.status_code}")
    assert response.status_code == 422, "Should return 422 for invalid page"
    print("✓ 422 for invalid query parameter")


def run_all_tests():
    """Run all API tests."""
    print("\n" + "="*70)
    print("WILSONIC API TEST SUITE")
    print("="*70)
    print(f"\nTesting API at: {BASE_URL}")
    print("Make sure server is running: uvicorn backend.main:app --reload")
    
    try:
        # Check if server is running
        print("\nChecking if server is running...")
        response = requests.get(f"{BASE_URL}/", timeout=2)
        if response.status_code != 200:
            print("✗ Server returned unexpected status")
            sys.exit(1)
        print("✓ Server is running\n")
        
    except requests.exceptions.ConnectionError:
        print("\n✗ ERROR: Cannot connect to server")
        print("Please start the server first:")
        print("  uvicorn backend.main:app --reload")
        sys.exit(1)
    
    try:
        # Run tests
        test_root()
        test_health()
        test_create_draw()
        test_list_draws()
        test_ranking()
        test_drift()
        test_summary()
        test_error_handling()
        
        # Final summary
        print("\n" + "="*70)
        print("ALL API TESTS PASSED ✓")
        print("="*70)
        print("\nAll 5 endpoints working correctly:")
        print("  ✓ POST /draws - Manual draw entry")
        print("  ✓ GET /draws - List recent draws (paginated)")
        print("  ✓ GET /stats/ranking - Letter ranking with CIs")
        print("  ✓ GET /stats/drift - Drift detection")
        print("  ✓ GET /stats/summary - Summary statistics")
        print("\nAPI is ready for frontend integration!")
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
