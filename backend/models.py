"""
SQLAlchemy models for Wilsonic.

Defines the Draw model that stores historical lottery draw data.
"""

from datetime import datetime, timezone
from sqlalchemy import Column, Integer, String, DateTime
from .database import Base


class Draw(Base):
    """
    Draw model - stores individual letter draw records.
    
    Each record represents one draw where a letter (A-G) was selected.
    
    Attributes:
        id: Auto-incrementing primary key
        letter: Single letter A-G
        timestamp: When the draw occurred (timezone-aware UTC)
        source: How the draw was recorded:
                - "manual": Entered via frontend form
                - "scraper": Automated scraper (Phase 2)
                - "historical_import": One-time bulk import of historical data
    """
    
    __tablename__ = "draws"
    
    # Primary key
    id = Column(Integer, primary_key=True, autoincrement=True, index=True)
    
    # Letter drawn (one of A, B, C, D, E, F, G)
    letter = Column(String(1), nullable=False, index=True)
    
    # When the draw happened (defaults to current time if not specified)
    timestamp = Column(DateTime, nullable=False, default=lambda: datetime.now(timezone.utc), index=True)
    
    # Source of the draw entry: "manual", "scraper", or "historical_import"
    source = Column(String(20), nullable=False, default="manual")
    
    def __repr__(self):
        """String representation for debugging."""
        return f"<Draw(id={self.id}, letter='{self.letter}', timestamp={self.timestamp}, source='{self.source}')>"
    
    def to_dict(self):
        """
        Convert model instance to dictionary for API responses.
        
        Returns:
            dict: Dictionary representation of the draw
        """
        return {
            "id": self.id,
            "letter": self.letter,
            "timestamp": self.timestamp.isoformat() if self.timestamp else None,
            "source": self.source
        }
