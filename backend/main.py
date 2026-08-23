"""
Wilsonic FastAPI application entrypoint.

Main application that initializes database, configures CORS,
and registers API routes.
"""

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager

from .database import init_db
from .api.routes import router


# ============================================================================
# Application Lifespan Events
# ============================================================================

@asynccontextmanager
async def lifespan(app: FastAPI):
    """
    Application lifespan manager.
    
    Startup:
        - Initialize database (create tables if needed)
    
    Shutdown:
        - Cleanup resources (currently none needed)
    """
    # Startup
    print("🚀 Starting Wilsonic API...")
    print("📊 Initializing database...")
    init_db()
    print("✓ Database initialized")
    print("✓ API ready to accept requests")
    
    yield
    
    # Shutdown
    print("👋 Shutting down Wilsonic API...")


# ============================================================================
# FastAPI Application
# ============================================================================

app = FastAPI(
    title="Wilsonic API",
    description="""
    Prediction indicator system for lottery-style game (letters A-G).
    
    Tracks historical draws and provides statistical analysis:
    - Frequency-based ranking
    - Wilson confidence intervals
    - Rolling window analysis
    - Drift detection
    
    **This is an indicator system, not a prediction oracle.**
    """,
    version="1.0.0",
    lifespan=lifespan,
)


# ============================================================================
# CORS Configuration (for Frontend)
# ============================================================================

# Allow frontend to make requests from different origin
# In production, replace "*" with specific frontend domain
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:3000",  # React default port
        "http://localhost:5173",  # Vite default port
        "http://127.0.0.1:3000",
        "http://127.0.0.1:5173",
        "*",  # Allow all origins in development (restrict in production)
    ],
    allow_credentials=True,
    allow_methods=["*"],  # Allow all methods (GET, POST, etc.)
    allow_headers=["*"],  # Allow all headers
)


# ============================================================================
# Register Routes
# ============================================================================

app.include_router(router, tags=["Wilsonic"])


# ============================================================================
# Root Endpoint
# ============================================================================

@app.get("/")
def root():
    """
    Root endpoint with API information.
    
    Returns:
        Welcome message and available endpoints
    """
    return {
        "message": "Wilsonic API - Lottery Prediction Indicator System",
        "version": "1.0.0",
        "description": "Statistical analysis for letter draws (A-G)",
        "endpoints": {
            "manual_entry": "POST /draws",
            "list_draws": "GET /draws",
            "ranking": "GET /stats/ranking",
            "drift": "GET /stats/drift",
            "summary": "GET /stats/summary",
            "health": "GET /health",
            "docs": "/docs (interactive API documentation)",
        },
        "note": "This is an indicator system, not a prediction oracle."
    }


# ============================================================================
# Run with: uvicorn backend.main:app --reload
# ============================================================================

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "backend.main:app",
        host="0.0.0.0",
        port=8000,
        reload=True,
        log_level="info"
    )
