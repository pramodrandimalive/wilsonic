"""
API routes for Wilsonic.

Implements all endpoints from Section 6 of the project brief:
- POST /draws - Manual draw entry
- GET /draws - List recent draws (paginated)
- GET /stats/ranking - Current ranked letter list
- GET /stats/drift - Drift status per letter
- GET /stats/summary - Total draws and per-letter counts
"""

from datetime import datetime, timezone
from typing import Optional, List
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from pydantic import BaseModel, Field, validator

from ..database import get_db
from ..models import Draw
from .. import stats


# Create API router
router = APIRouter()


# ============================================================================
# Pydantic Models (Request/Response schemas)
# ============================================================================

class DrawCreate(BaseModel):
    """Request model for creating a new draw."""
    letter: str = Field(..., description="Letter drawn (A-G)")
    timestamp: Optional[datetime] = Field(None, description="Draw timestamp (defaults to now)")
    
    @validator('letter')
    def validate_letter(cls, v):
        """Ensure letter is valid (A-G)."""
        v = v.upper().strip()
        if v not in stats.VALID_LETTERS:
            raise ValueError(f"Letter must be one of {', '.join(stats.VALID_LETTERS)}")
        return v
    
    class Config:
        json_schema_extra = {
            "example": {
                "letter": "A",
                "timestamp": "2026-08-15T15:30:00Z"
            }
        }


class DrawUpdate(BaseModel):
    """Request model for updating an existing draw."""
    letter: Optional[str] = Field(None, description="New letter (A-G)")
    timestamp: Optional[str] = Field(None, description="New timestamp (ISO format)")
    
    @validator('letter')
    def validate_letter(cls, v):
        """Ensure letter is valid (A-G) if provided."""
        if v is not None:
            v = v.upper().strip()
            if v not in stats.VALID_LETTERS:
                raise ValueError(f"Letter must be one of {', '.join(stats.VALID_LETTERS)}")
            return v
        return v
    
    @validator('timestamp')
    def validate_timestamp(cls, v):
        """Ensure timestamp is valid ISO format if provided."""
        if v is not None:
            try:
                datetime.fromisoformat(v.replace('Z', '+00:00'))
            except (ValueError, AttributeError):
                raise ValueError("Timestamp must be in ISO format (e.g., '2026-08-15T15:30:00Z')")
        return v
    
    class Config:
        json_schema_extra = {
            "example": {
                "letter": "B",
                "timestamp": "2026-08-15T16:00:00Z"
            }
        }


class DrawResponse(BaseModel):
    """Response model for a draw."""
    id: int
    letter: str
    timestamp: datetime
    source: str
    
    class Config:
        from_attributes = True


class DrawsListResponse(BaseModel):
    """Response model for paginated draws list."""
    draws: List[DrawResponse]
    total: int
    page: int
    page_size: int
    total_pages: int


class RankingEntry(BaseModel):
    """Single entry in ranking response."""
    letter: str
    p_hat: float
    rank: int
    count: int
    lower_bound: float
    upper_bound: float


class RankingResponse(BaseModel):
    """Response model for ranking endpoint."""
    total_draws: int
    ranking: List[RankingEntry]


class DriftLetterStatus(BaseModel):
    """Drift status for a single letter."""
    drift_detected: bool
    p_hat_recent: float
    p_hat_historical: float
    lower_bound: float
    upper_bound: float
    consecutive_violations: int
    outside_interval: bool


class DriftResponse(BaseModel):
    """Response model for drift endpoint."""
    any_drift_detected: bool
    drifted_letters: List[str]
    letters_at_risk: List[str]
    window_size: int
    total_draws: int
    drift_status: dict  # Letter -> DriftLetterStatus
    insufficient_data: bool = False
    required_draws: Optional[int] = None
    message: Optional[str] = None


class SummaryResponse(BaseModel):
    """Response model for summary endpoint."""
    total_draws: int
    letter_counts: dict
    frequencies: dict
    last_draw: Optional[DrawResponse]
    last_updated: datetime


# ============================================================================
# POST /draws - Manual Draw Entry
# ============================================================================

@router.post("/draws", response_model=DrawResponse, status_code=201)
def create_draw(
    draw: DrawCreate,
    db: Session = Depends(get_db)
):
    """
    Submit a new draw manually.
    
    Args:
        draw: Draw data (letter required, timestamp optional)
        db: Database session
        
    Returns:
        Created draw with ID
        
    Raises:
        HTTPException: If letter is invalid
    """
    try:
        # Create new draw
        new_draw = Draw(
            letter=draw.letter,
            timestamp=draw.timestamp if draw.timestamp else datetime.now(timezone.utc),
            source="manual"
        )
        
        db.add(new_draw)
        db.commit()
        db.refresh(new_draw)
        
        return new_draw
        
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=f"Failed to create draw: {str(e)}")


# ============================================================================
# PUT /draws/{id} - Update Draw
# ============================================================================

@router.put("/draws/{draw_id}", response_model=DrawResponse)
def update_draw(
    draw_id: int,
    draw_update: DrawUpdate,
    db: Session = Depends(get_db)
):
    """
    Update an existing draw's letter and/or timestamp.
    
    WARNING: Modifying historical draws will affect statistical calculations.
    
    Args:
        draw_id: ID of the draw to update
        draw_update: Fields to update (letter and/or timestamp)
        db: Database session
        
    Returns:
        Updated draw record
        
    Raises:
        HTTPException: 404 if draw not found, 400 if no fields provided
    """
    try:
        # Validate at least one field is provided
        if draw_update.letter is None and draw_update.timestamp is None:
            raise HTTPException(
                status_code=400, 
                detail="Must provide at least one field to update (letter or timestamp)"
            )
        
        # Find the draw
        draw = db.query(Draw).filter(Draw.id == draw_id).first()
        
        if not draw:
            raise HTTPException(
                status_code=404, 
                detail=f"Draw with id {draw_id} not found"
            )
        
        # Update fields if provided
        if draw_update.letter is not None:
            draw.letter = draw_update.letter
        
        if draw_update.timestamp is not None:
            # Parse ISO format timestamp
            draw.timestamp = datetime.fromisoformat(
                draw_update.timestamp.replace('Z', '+00:00')
            )
        
        # Commit changes
        db.commit()
        db.refresh(draw)
        
        return draw
        
    except HTTPException:
        raise
    except Exception as e:
        db.rollback()
        raise HTTPException(
            status_code=500, 
            detail=f"Failed to update draw: {str(e)}"
        )


# ============================================================================
# DELETE /draws/{id} - Delete Draw
# ============================================================================

@router.delete("/draws/{draw_id}")
def delete_draw(
    draw_id: int,
    db: Session = Depends(get_db)
):
    """
    Delete a draw by ID.
    
    WARNING: This permanently removes the draw and will affect
    all statistical calculations across the entire application.
    
    Args:
        draw_id: ID of the draw to delete
        db: Database session
        
    Returns:
        Confirmation message with deleted draw info
        
    Raises:
        HTTPException: 404 if draw not found
    """
    try:
        # Find the draw
        draw = db.query(Draw).filter(Draw.id == draw_id).first()
        
        if not draw:
            raise HTTPException(
                status_code=404, 
                detail=f"Draw with id {draw_id} not found"
            )
        
        # Store info for response before deleting
        draw_info = {
            "id": draw.id,
            "letter": draw.letter,
            "timestamp": draw.timestamp.isoformat(),
            "source": draw.source
        }
        
        # Delete the draw
        db.delete(draw)
        db.commit()
        
        return {
            "message": "Draw deleted successfully",
            "deleted_draw": draw_info
        }
        
    except HTTPException:
        raise
    except Exception as e:
        db.rollback()
        raise HTTPException(
            status_code=500, 
            detail=f"Failed to delete draw: {str(e)}"
        )


# ============================================================================
# GET /draws - List Recent Draws (Paginated)
# ============================================================================

@router.get("/draws", response_model=DrawsListResponse)
def list_draws(
    page: int = Query(1, ge=1, description="Page number (1-indexed)"),
    page_size: int = Query(50, ge=1, le=500, description="Items per page"),
    letter: Optional[str] = Query(None, description="Filter by letter (A-G)"),
    source: Optional[str] = Query(None, description="Filter by source (manual, historical_import, scraper)"),
    sort: str = Query("newest", description="Sort order: 'newest' or 'oldest'"),
    db: Session = Depends(get_db)
):
    """
    List draws with pagination, filtering, and sorting.
    
    Args:
        page: Page number (1-indexed)
        page_size: Number of draws per page (max 500)
        letter: Optional filter by letter (A-G)
        source: Optional filter by source
        sort: Sort order - 'newest' (default, desc) or 'oldest' (asc)
        db: Database session
        
    Returns:
        Paginated list of draws with applied filters and sort
    """
    try:
        # Build base query
        query = db.query(Draw)
        
        # Apply filters
        if letter:
            letter_upper = letter.upper().strip()
            if letter_upper in stats.VALID_LETTERS:
                query = query.filter(Draw.letter == letter_upper)
        
        if source:
            query = query.filter(Draw.source == source)
        
        # Get total count with filters applied
        total = query.count()
        
        # Calculate pagination
        offset = (page - 1) * page_size
        total_pages = (total + page_size - 1) // page_size  # Ceiling division
        
        # Apply sorting
        if sort == "oldest":
            query = query.order_by(Draw.timestamp.asc(), Draw.id.asc())
        else:  # newest (default)
            query = query.order_by(Draw.timestamp.desc(), Draw.id.desc())
        
        # Apply pagination
        draws = query.offset(offset).limit(page_size).all()
        
        return DrawsListResponse(
            draws=draws,
            total=total,
            page=page,
            page_size=page_size,
            total_pages=total_pages
        )
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to fetch draws: {str(e)}")


# ============================================================================
# GET /stats/ranking - Current Ranked Letter List
# ============================================================================

@router.get("/stats/ranking", response_model=RankingResponse)
def get_ranking(db: Session = Depends(get_db)):
    """
    Get current ranked letter list with probabilities and confidence intervals.
    
    Returns letters sorted by frequency (most to least likely), with:
    - p_hat: Observed frequency
    - rank: Position (1 = most likely)
    - count: Number of occurrences
    - lower_bound, upper_bound: 95% Wilson confidence interval
    
    Args:
        db: Database session
        
    Returns:
        Ranking with all letters and total draw count
    """
    try:
        ranking = stats.get_ranking(db)
        total_draws = stats.get_total_draws(db)
        
        return RankingResponse(
            total_draws=total_draws,
            ranking=ranking
        )
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to calculate ranking: {str(e)}")


# ============================================================================
# GET /stats/drift - Drift Status Per Letter
# ============================================================================

@router.get("/stats/drift", response_model=DriftResponse)
def get_drift_status(
    window_size: int = Query(
        stats.DEFAULT_WINDOW_SIZE,
        ge=100,
        le=100000,
        description="Rolling window size for recent frequency"
    ),
    db: Session = Depends(get_db)
):
    """
    Get drift detection status for all letters.
    
    Compares recent frequency (last N draws) to historical confidence interval.
    A letter is flagged as "drifted" only after 10+ consecutive violations,
    to avoid false alarms from normal statistical noise.
    
    Args:
        window_size: Number of recent draws to analyze (default: 5000)
        db: Database session
        
    Returns:
        Drift summary and detailed status per letter
    """
    try:
        # Get drift summary
        summary = stats.get_drift_summary(db, window_size)
        
        # Get detailed status
        drift_status = stats.detect_drift(db, window_size)
        
        return DriftResponse(
            any_drift_detected=summary["any_drift_detected"],
            drifted_letters=summary["drifted_letters"],
            letters_at_risk=summary["letters_at_risk"],
            window_size=summary["window_size"],
            total_draws=summary["total_draws"],
            drift_status=drift_status,
            insufficient_data=summary.get("insufficient_data", False),
            required_draws=summary.get("required_draws"),
            message=summary.get("message")
        )
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to detect drift: {str(e)}")


# ============================================================================
# GET /stats/summary - Total Draws and Per-Letter Counts
# ============================================================================

@router.get("/stats/summary", response_model=SummaryResponse)
def get_summary(db: Session = Depends(get_db)):
    """
    Get summary statistics: total draws, per-letter counts, frequencies.
    
    Args:
        db: Database session
        
    Returns:
        Summary with totals, counts, frequencies, and last draw info
    """
    try:
        total_draws = stats.get_total_draws(db)
        letter_counts = stats.get_letter_counts(db)
        frequencies = stats.calculate_base_frequency(db)
        
        # Get most recent draw
        last_draw = (
            db.query(Draw)
            .order_by(Draw.timestamp.desc(), Draw.id.desc())
            .first()
        )
        
        return SummaryResponse(
            total_draws=total_draws,
            letter_counts=letter_counts,
            frequencies=frequencies,
            last_draw=last_draw,
            last_updated=datetime.now(timezone.utc)
        )
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to get summary: {str(e)}")


# ============================================================================
# Health Check Endpoint (Bonus)
# ============================================================================

@router.get("/health")
def health_check(db: Session = Depends(get_db)):
    """
    Health check endpoint to verify API and database are working.
    
    Returns:
        Status information
    """
    try:
        # Test database connection
        total = stats.get_total_draws(db)
        
        return {
            "status": "healthy",
            "database": "connected",
            "total_draws": total,
            "timestamp": datetime.now(timezone.utc).isoformat()
        }
    except Exception as e:
        raise HTTPException(status_code=503, detail=f"Service unhealthy: {str(e)}")


# ============================================================================
# GET /stats/rolling-trend - Rolling Frequency Trend Data
# ============================================================================

@router.get("/stats/rolling-trend")
def get_rolling_trend(
    window_size: int = Query(5000, ge=100, le=50000, description="Rolling window size"),
    interval: int = Query(500, ge=100, le=10000, description="Sample interval (draws between data points)"),
    db: Session = Depends(get_db)
):
    """
    Get rolling frequency trend data for charting.
    
    Calculates p_hat for each letter at regular intervals across the entire dataset
    using a rolling window. This shows how letter frequencies have evolved over time.
    
    Args:
        window_size: Size of rolling window for each calculation
        interval: Number of draws between each data point
        db: Database session
        
    Returns:
        Trend data with timestamps and frequencies per letter
    """
    try:
        total_draws = stats.get_total_draws(db)
        
        # Need at least window_size draws to start
        if total_draws < window_size:
            return {
                "data_points": [],
                "baseline_frequencies": {},
                "total_draws": total_draws,
                "window_size": window_size,
                "interval": interval,
                "message": f"Need at least {window_size} draws for trend analysis"
            }
        
        # Calculate baseline (full-history) frequencies
        baseline_freqs = stats.calculate_base_frequency(db)
        
        # Generate data points at intervals
        data_points = []
        start_position = window_size  # First point at window_size draws
        
        for position in range(start_position, total_draws + 1, interval):
            # Get the window of draws ending at this position
            window_draws = (
                db.query(Draw)
                .order_by(Draw.timestamp.asc(), Draw.id.asc())
                .offset(max(0, position - window_size))
                .limit(window_size)
                .all()
            )
            
            if len(window_draws) < window_size:
                continue
            
            # Count letters in this window
            letter_counts = {letter: 0 for letter in stats.VALID_LETTERS}
            for draw in window_draws:
                if draw.letter in letter_counts:
                    letter_counts[draw.letter] += 1
            
            # Calculate frequencies
            point = {
                "position": position,
                "draw_id": window_draws[-1].id,
                "timestamp": window_draws[-1].timestamp.isoformat()
            }
            
            for letter in stats.VALID_LETTERS:
                point[f"freq_{letter}"] = (letter_counts[letter] / window_size) * 100
            
            data_points.append(point)
        
        return {
            "data_points": data_points,
            "baseline_frequencies": {
                letter: baseline_freqs.get(letter, 0) * 100 
                for letter in stats.VALID_LETTERS
            },
            "total_draws": total_draws,
            "window_size": window_size,
            "interval": interval
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to calculate trend: {str(e)}")


# ============================================================================
# DEBUG ENDPOINT - Drift Tracker State
# ============================================================================

@router.get("/debug/drift-tracker")
def debug_drift_tracker(db: Session = Depends(get_db)):
    """
    Debug endpoint to inspect drift tracker state.
    
    Returns current state of the in-memory drift violation tracker
    and detailed drift analysis.
    """
    # Get raw tracker state
    tracker_state = {
        letter: stats._drift_tracker[letter] 
        for letter in stats.VALID_LETTERS
    }
    
    # Get drift status
    drift_status = stats.detect_drift(db, window_size=5000)
    
    # Get summary
    summary = stats.get_drift_summary(db, window_size=5000)
    
    # Calculate some diagnostic info
    total_draws = stats.get_total_draws(db)
    window_size = 5000
    overlap_percentage = (window_size / total_draws * 100) if total_draws > 0 else 0
    
    return {
        "tracker_state": tracker_state,
        "drift_status": drift_status,
        "summary": summary,
        "diagnostics": {
            "total_draws": total_draws,
            "window_size": window_size,
            "window_overlap_percentage": overlap_percentage,
            "warning": "High overlap!" if overlap_percentage > 40 else None
        }
    }
