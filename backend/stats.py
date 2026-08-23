"""
Statistics engine for Wilsonic.

Implements frequency analysis, Wilson confidence intervals, rolling windows,
and drift detection. All logic validated against 300k historical draws.

IMPORTANT: This module does NOT implement gap-based or "overdue" logic.
Those approaches were tested and disproven in backtesting.
"""

import math
from typing import Dict, List, Optional, Tuple
from datetime import datetime
from sqlalchemy.orm import Session
from sqlalchemy import func, desc
from models import Draw


# Valid letters in the lottery system
VALID_LETTERS = ["A", "B", "C", "D", "E", "F", "G"]

# Z-score for 95% confidence interval (two-tailed)
Z_SCORE_95 = 1.96

# Default window size for rolling frequency analysis
DEFAULT_WINDOW_SIZE = 5000

# Drift detection: minimum consecutive violations to flag drift
DRIFT_THRESHOLD_CONSECUTIVE = 10

# Minimum data requirement: need 3x window size for meaningful comparison
MINIMUM_DRAWS_FOR_DRIFT = DEFAULT_WINDOW_SIZE * 3  # 15,000 draws

# In-memory drift tracking: {letter: consecutive_violation_count}
_drift_tracker: Dict[str, int] = {letter: 0 for letter in VALID_LETTERS}

# Track last evaluated state to prevent incrementing on every API call
_last_evaluated_total_draws: int = 0


# ============================================================================
# Section 5.1: Base Frequency Estimator
# ============================================================================

def calculate_base_frequency(db: Session) -> Dict[str, float]:
    """
    Calculate base frequency p_hat(L) for all letters from full history.
    
    Formula: p_hat(L) = count(L) / total_draws
    
    Args:
        db: Database session
        
    Returns:
        Dictionary mapping each letter to its frequency (0.0 to 1.0)
        
    Example:
        {"A": 0.382, "B": 0.211, "C": 0.134, ...}
    """
    # Get total number of draws
    total_draws = db.query(Draw).count()
    
    if total_draws == 0:
        # No data yet - return uniform distribution
        return {letter: 1.0 / len(VALID_LETTERS) for letter in VALID_LETTERS}
    
    # Count occurrences of each letter
    letter_counts = (
        db.query(Draw.letter, func.count(Draw.id))
        .group_by(Draw.letter)
        .all()
    )
    
    # Build frequency dictionary
    frequencies = {letter: 0.0 for letter in VALID_LETTERS}
    for letter, count in letter_counts:
        if letter in VALID_LETTERS:
            frequencies[letter] = count / total_draws
    
    return frequencies


def get_total_draws(db: Session) -> int:
    """
    Get total number of draws in the database.
    
    Args:
        db: Database session
        
    Returns:
        Total count of draws
    """
    return db.query(Draw).count()


def get_letter_counts(db: Session) -> Dict[str, int]:
    """
    Get raw count of each letter from full history.
    
    Args:
        db: Database session
        
    Returns:
        Dictionary mapping each letter to its count
        
    Example:
        {"A": 38200, "B": 21100, "C": 13400, ...}
    """
    letter_counts = (
        db.query(Draw.letter, func.count(Draw.id))
        .group_by(Draw.letter)
        .all()
    )
    
    counts = {letter: 0 for letter in VALID_LETTERS}
    for letter, count in letter_counts:
        if letter in VALID_LETTERS:
            counts[letter] = count
    
    return counts


# ============================================================================
# Section 5.3: Wilson Score Confidence Interval
# ============================================================================

def calculate_wilson_interval(p: float, n: int, z: float = Z_SCORE_95) -> Tuple[float, float]:
    """
    Calculate Wilson score confidence interval for a proportion.
    
    Formula (95% CI):
        z = 1.96
        denominator = 1 + z²/n
        center = (p + z²/(2n)) / denominator
        margin = z * sqrt((p*(1-p)/n) + z²/(4n²)) / denominator
        lower_bound = center - margin
        upper_bound = center + margin
    
    Args:
        p: Observed proportion (0.0 to 1.0)
        n: Sample size (total draws)
        z: Z-score for confidence level (default: 1.96 for 95%)
        
    Returns:
        Tuple of (lower_bound, upper_bound)
        
    Example:
        calculate_wilson_interval(0.382, 100000, 1.96)
        # Returns approximately (0.379, 0.385)
    """
    if n == 0:
        # No data - return widest possible interval
        return (0.0, 1.0)
    
    # Ensure p is in valid range
    p = max(0.0, min(1.0, p))
    
    z_squared = z * z
    
    # Calculate denominator
    denominator = 1.0 + (z_squared / n)
    
    # Calculate center point
    center = (p + z_squared / (2 * n)) / denominator
    
    # Calculate margin of error
    sqrt_term = math.sqrt((p * (1 - p) / n) + (z_squared / (4 * n * n)))
    margin = z * sqrt_term / denominator
    
    # Calculate bounds
    lower_bound = center - margin
    upper_bound = center + margin
    
    # Clamp to [0, 1]
    lower_bound = max(0.0, lower_bound)
    upper_bound = min(1.0, upper_bound)
    
    return (lower_bound, upper_bound)


def calculate_two_proportion_z_test(
    p1: float, n1: int, 
    p2: float, n2: int
) -> float:
    """
    Calculate z-score for two-proportion test.
    
    Tests whether two proportions are significantly different.
    H0: p1 = p2 (no difference)
    HA: p1 ≠ p2 (significant difference)
    
    Formula:
        pooled_p = (x1 + x2) / (n1 + n2)
        where x1 = p1 * n1, x2 = p2 * n2
        
        SE = sqrt(pooled_p * (1 - pooled_p) * (1/n1 + 1/n2))
        z = (p2 - p1) / SE
        
    A |z| > 1.96 indicates significant difference at 95% confidence level.
    
    Args:
        p1: First proportion (historical frequency)
        n1: First sample size (total draws)
        p2: Second proportion (recent window frequency)
        n2: Second sample size (window size)
        
    Returns:
        Z-score (positive = p2 > p1, negative = p2 < p1)
        
    Example:
        z = calculate_two_proportion_z_test(0.38, 100000, 0.42, 5000)
        # If |z| > 1.96, the difference is statistically significant
    """
    # Handle edge cases
    if n1 <= 0 or n2 <= 0:
        return 0.0
    
    # Ensure proportions are in valid range
    p1 = max(0.0, min(1.0, p1))
    p2 = max(0.0, min(1.0, p2))
    
    # Calculate counts from proportions
    x1 = p1 * n1
    x2 = p2 * n2
    
    # Calculate pooled proportion
    pooled_p = (x1 + x2) / (n1 + n2)
    
    # Handle extreme cases
    if pooled_p == 0.0 or pooled_p == 1.0:
        # If pooled proportion is 0 or 1, standard error is 0
        # Return large z-score if proportions differ, 0 if same
        if abs(p2 - p1) < 0.0001:
            return 0.0
        else:
            return 999.0 if p2 > p1 else -999.0
    
    # Calculate standard error
    se_term = pooled_p * (1 - pooled_p) * (1/n1 + 1/n2)
    
    # Handle numerical stability
    if se_term <= 0:
        return 0.0
    
    se = math.sqrt(se_term)
    
    # Handle zero standard error
    if se == 0:
        return 0.0
    
    # Calculate z-score
    z_score = (p2 - p1) / se
    
    # Clamp to reasonable range to avoid numerical issues
    z_score = max(-100.0, min(100.0, z_score))
    
    return z_score


def get_minimum_draws_for_drift(window_size: int) -> int:
    """
    Calculate minimum draws required for meaningful drift detection.
    
    Requires 3x the window size to ensure sufficient historical data
    for comparison.
    
    Args:
        window_size: Size of rolling window
        
    Returns:
        Minimum total draws required
    """
    return window_size * 3


# ============================================================================
# Section 5.2: Ranking
# ============================================================================

def get_ranking(db: Session) -> List[Dict]:
    """
    Get all letters ranked by frequency (descending) with confidence intervals.
    
    Returns list of dictionaries with:
        - letter: The letter (A-G)
        - p_hat: Frequency (0.0 to 1.0)
        - rank: Rank position (1 = most frequent)
        - lower_bound: Wilson CI lower bound
        - upper_bound: Wilson CI upper bound
        - count: Raw count of occurrences
    
    Args:
        db: Database session
        
    Returns:
        List of ranking entries, sorted by p_hat descending
        
    Example:
        [
            {"letter": "A", "p_hat": 0.382, "rank": 1, "lower_bound": 0.379, 
             "upper_bound": 0.385, "count": 38200},
            {"letter": "B", "p_hat": 0.211, "rank": 2, ...},
            ...
        ]
    """
    # Get base frequencies and counts
    frequencies = calculate_base_frequency(db)
    counts = get_letter_counts(db)
    total_draws = get_total_draws(db)
    
    # Build ranking list with confidence intervals
    ranking = []
    for letter in VALID_LETTERS:
        p_hat = frequencies[letter]
        count = counts[letter]
        
        # Calculate Wilson confidence interval
        lower_bound, upper_bound = calculate_wilson_interval(p_hat, total_draws)
        
        ranking.append({
            "letter": letter,
            "p_hat": p_hat,
            "count": count,
            "lower_bound": lower_bound,
            "upper_bound": upper_bound,
        })
    
    # Sort by frequency descending
    ranking.sort(key=lambda x: x["p_hat"], reverse=True)
    
    # Add rank positions (1-indexed)
    for i, entry in enumerate(ranking):
        entry["rank"] = i + 1
    
    return ranking


# ============================================================================
# Section 5.4: Rolling Window (Recent Frequency)
# ============================================================================

def calculate_rolling_frequency(
    db: Session, 
    window_size: int = DEFAULT_WINDOW_SIZE
) -> Dict[str, float]:
    """
    Calculate recent frequency p_hat_recent(L) from last N draws.
    
    Formula: p_hat_recent(L) = count(L in last N draws) / N
    
    Args:
        db: Database session
        window_size: Number of recent draws to analyze (default: 5000)
        
    Returns:
        Dictionary mapping each letter to its recent frequency
        
    Example:
        calculate_rolling_frequency(db, window_size=5000)
        # Returns {"A": 0.385, "B": 0.215, ...}
    """
    # Get last N draws, most recent first
    recent_draws = (
        db.query(Draw.letter)
        .order_by(desc(Draw.timestamp), desc(Draw.id))
        .limit(window_size)
        .all()
    )
    
    if not recent_draws:
        # No data - return uniform distribution
        return {letter: 1.0 / len(VALID_LETTERS) for letter in VALID_LETTERS}
    
    # Count letters in recent window
    recent_counts = {letter: 0 for letter in VALID_LETTERS}
    for (letter,) in recent_draws:
        if letter in VALID_LETTERS:
            recent_counts[letter] += 1
    
    # Calculate frequencies
    actual_window = len(recent_draws)
    recent_frequencies = {
        letter: count / actual_window 
        for letter, count in recent_counts.items()
    }
    
    return recent_frequencies


def get_rolling_window_size(db: Session, requested_size: int = DEFAULT_WINDOW_SIZE) -> int:
    """
    Get actual rolling window size (may be smaller than requested if insufficient data).
    
    Args:
        db: Database session
        requested_size: Desired window size
        
    Returns:
        Actual window size (min of requested and total draws)
    """
    total_draws = get_total_draws(db)
    return min(requested_size, total_draws)


# ============================================================================
# Section 5.5: Drift Detection
# ============================================================================

def detect_drift(
    db: Session,
    window_size: int = DEFAULT_WINDOW_SIZE,
    reset_tracker: bool = False
) -> Dict[str, Dict]:
    """
    Detect if recent frequency has drifted outside historical confidence interval.
    
    A letter is flagged as drifted ONLY if p_hat_recent(L) falls outside
    the Wilson CI [lower_bound, upper_bound] for 10+ consecutive NEW DRAWS.
    
    This avoids false alarms from normal statistical noise.
    
    IMPORTANT: Drift is evaluated only when NEW draws are added, not on every API call.
    The tracker increments only when total_draws has increased since last check.
    
    Args:
        db: Database session
        window_size: Size of rolling window (default: 5000)
        reset_tracker: If True, reset drift tracking counters
        
    Returns:
        Dictionary mapping each letter to drift information:
            - drift_detected: Boolean, True if 10+ consecutive violations
            - p_hat_recent: Recent frequency
            - p_hat_historical: Historical frequency
            - lower_bound: CI lower bound (from historical)
            - upper_bound: CI upper bound (from historical)
            - consecutive_violations: Number of consecutive times outside CI
            - outside_interval: Boolean, True if currently outside interval
            - insufficient_data: Boolean, True if not enough draws for drift detection
            
    Example:
        {
            "A": {
                "drift_detected": False,
                "p_hat_recent": 0.385,
                "p_hat_historical": 0.382,
                "lower_bound": 0.379,
                "upper_bound": 0.385,
                "consecutive_violations": 0,
                "outside_interval": False,
                "insufficient_data": False
            },
            ...
        }
    """
    global _drift_tracker, _last_evaluated_total_draws
    
    if reset_tracker:
        _drift_tracker = {letter: 0 for letter in VALID_LETTERS}
        _last_evaluated_total_draws = 0
    
    # Get current total draws
    total_draws = get_total_draws(db)
    
    # Check if we have enough data for meaningful drift detection
    # Need 3x window size for statistical validity
    minimum_required = get_minimum_draws_for_drift(window_size)
    
    if total_draws < minimum_required:
        # Not enough data - return status but don't track drift
        ranking = get_ranking(db)
        recent_frequencies = calculate_rolling_frequency(db, window_size)
        
        drift_status = {}
        for letter in VALID_LETTERS:
            hist_entry = next((e for e in ranking if e["letter"] == letter), None)
            p_hist = hist_entry["p_hat"] if hist_entry else 0.0
            lower = hist_entry["lower_bound"] if hist_entry else 0.0
            upper = hist_entry["upper_bound"] if hist_entry else 1.0
            p_recent = recent_frequencies.get(letter, 0.0)
            
            drift_status[letter] = {
                "drift_detected": False,
                "p_hat_recent": p_recent,
                "p_hat_historical": p_hist,
                "lower_bound": lower,
                "upper_bound": upper,
                "z_score": 0.0,
                "consecutive_violations": 0,
                "outside_interval": False,
                "insufficient_data": True,
                "required_draws": minimum_required,
                "current_draws": total_draws
            }
        
        return drift_status
    
    # Check if new draws have been added since last evaluation
    # Only update tracker if data has changed
    should_evaluate = (total_draws != _last_evaluated_total_draws)
    
    if not should_evaluate:
        # No new draws - just return current status without updating tracker
        ranking = get_ranking(db)
        recent_frequencies = calculate_rolling_frequency(db, window_size)
        
        drift_status = {}
        for letter in VALID_LETTERS:
            hist_entry = next((e for e in ranking if e["letter"] == letter), None)
            p_hist = hist_entry["p_hat"] if hist_entry else 0.0
            lower = hist_entry["lower_bound"] if hist_entry else 0.0
            upper = hist_entry["upper_bound"] if hist_entry else 1.0
            p_recent = recent_frequencies.get(letter, 0.0)
            
            # Use two-proportion z-test to check for significant deviation
            actual_window = get_rolling_window_size(db, window_size)
            z_score = calculate_two_proportion_z_test(
                p_hist, total_draws,
                p_recent, actual_window
            )
            outside_interval = abs(z_score) > Z_SCORE_95  # |z| > 1.96
            consecutive_violations = _drift_tracker[letter]
            
            drift_status[letter] = {
                "drift_detected": consecutive_violations >= DRIFT_THRESHOLD_CONSECUTIVE,
                "p_hat_recent": p_recent,
                "p_hat_historical": p_hist,
                "lower_bound": lower,
                "upper_bound": upper,
                "z_score": z_score,
                "consecutive_violations": consecutive_violations,
                "outside_interval": outside_interval,
                "insufficient_data": False
            }
        
        return drift_status
    
    # New draws added - update last evaluated count
    _last_evaluated_total_draws = total_draws
    
    # Get historical frequencies and confidence intervals
    ranking = get_ranking(db)
    historical_data = {
        entry["letter"]: {
            "p_hat": entry["p_hat"],
            "lower_bound": entry["lower_bound"],
            "upper_bound": entry["upper_bound"],
        }
        for entry in ranking
    }
    
    # Get recent frequencies
    recent_frequencies = calculate_rolling_frequency(db, window_size)
    
    # Check each letter for drift
    drift_status = {}
    
    for letter in VALID_LETTERS:
        p_recent = recent_frequencies[letter]
        historical = historical_data[letter]
        p_hist = historical["p_hat"]
        lower = historical["lower_bound"]
        upper = historical["upper_bound"]
        
        # Use two-proportion z-test to check for significant deviation
        actual_window = get_rolling_window_size(db, window_size)
        z_score = calculate_two_proportion_z_test(
            p_hist, total_draws,
            p_recent, actual_window
        )
        outside_interval = abs(z_score) > Z_SCORE_95  # |z| > 1.96
        
        # Update consecutive violation counter
        if outside_interval:
            _drift_tracker[letter] += 1
        else:
            # Reset counter if back within interval
            _drift_tracker[letter] = 0
        
        consecutive_violations = _drift_tracker[letter]
        
        # Flag drift only if 10+ consecutive violations
        drift_detected = consecutive_violations >= DRIFT_THRESHOLD_CONSECUTIVE
        
        drift_status[letter] = {
            "drift_detected": drift_detected,
            "p_hat_recent": p_recent,
            "p_hat_historical": p_hist,
            "lower_bound": lower,
            "upper_bound": upper,
            "z_score": z_score,
            "consecutive_violations": consecutive_violations,
            "outside_interval": outside_interval,
            "insufficient_data": False
        }
    
    return drift_status


def reset_drift_tracker():
    """
    Reset the drift tracking state (useful for testing or manual reset).
    """
    global _drift_tracker, _last_evaluated_total_draws
    _drift_tracker = {letter: 0 for letter in VALID_LETTERS}
    _last_evaluated_total_draws = 0


def get_drift_summary(db: Session, window_size: int = DEFAULT_WINDOW_SIZE) -> Dict:
    """
    Get high-level drift summary across all letters.
    
    Args:
        db: Database session
        window_size: Size of rolling window
        
    Returns:
        Dictionary with summary information:
            - any_drift_detected: Boolean, True if any letter has drift
            - drifted_letters: List of letters currently drifted
            - letters_at_risk: List of letters with 5+ consecutive violations
            - window_size: Actual window size used
            - total_draws: Total draws in database
            - insufficient_data: Boolean, True if not enough data for drift detection
            - required_draws: Minimum draws needed (if insufficient_data=True)
    """
    drift_status = detect_drift(db, window_size)
    
    # Check if we have insufficient data
    first_letter_status = drift_status[VALID_LETTERS[0]]
    if first_letter_status.get("insufficient_data", False):
        return {
            "any_drift_detected": False,
            "drifted_letters": [],
            "letters_at_risk": [],
            "window_size": get_rolling_window_size(db, window_size),
            "total_draws": get_total_draws(db),
            "insufficient_data": True,
            "required_draws": first_letter_status.get("required_draws", get_minimum_draws_for_drift(window_size)),
            "message": f"Drift detection requires at least {first_letter_status.get('required_draws', get_minimum_draws_for_drift(window_size)):,} draws. Currently have {first_letter_status.get('current_draws', 0):,}."
        }
    
    drifted = [
        letter for letter, status in drift_status.items() 
        if status["drift_detected"]
    ]
    
    at_risk = [
        letter for letter, status in drift_status.items()
        if status["consecutive_violations"] >= 5 and not status["drift_detected"]
    ]
    
    return {
        "any_drift_detected": len(drifted) > 0,
        "drifted_letters": drifted,
        "letters_at_risk": at_risk,
        "window_size": get_rolling_window_size(db, window_size),
        "total_draws": get_total_draws(db),
        "insufficient_data": False
    }


# ============================================================================
# Section 5.6: Explicitly Excluded Logic
# ============================================================================

# NOTE: The following logic is INTENTIONALLY NOT IMPLEMENTED:
# 
# - Gap-since-last-occurrence tracking
# - "Overdue" letter scoring
# - Hazard-rate-based "due" predictions
# - Time-weighted predictions
#
# These approaches were tested against 300k historical draws and
# performed WORSE than simple frequency ranking. The draw process
# is memoryless - "a letter hasn't appeared in a while so it's due"
# is a FALSE assumption (gambler's fallacy).
#
# Do NOT add this logic. It would be a regression, not a feature.
