import logging
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from backend.routers import analytics, content, learning

logger = logging.getLogger("tiktok-tracker")

EXPECTED_TABLES = [
    "config", "videos", "daily_stats", "content_ideas",
    "learnings", "session_notes", "algorithm_knowledge", "trends",
]

app = FastAPI(
    title="TikTok Growth Tracker",
    description="Track, analyze, and grow your TikTok presence",
    version="0.1.0",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173"],  # Vite dev server
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(analytics.router, prefix="/api/analytics", tags=["analytics"])
app.include_router(content.router, prefix="/api/content", tags=["content"])
app.include_router(learning.router, prefix="/api/learning", tags=["learning"])


def _check_tables() -> list[str]:
    """Return list of missing tables. Empty list means all good."""
    from backend.database import get_db

    missing = []
    db = get_db()
    for table in EXPECTED_TABLES:
        try:
            db.table(table).select("id", count="exact").limit(0).execute()
        except Exception:
            missing.append(table)
    return missing


@app.on_event("startup")
async def check_database():
    try:
        missing = _check_tables()
        if missing:
            logger.warning(
                "Missing tables: %s. Run: python scripts/setup_database.py",
                ", ".join(missing),
            )
    except Exception as e:
        logger.warning("Could not connect to database: %s", e)


@app.get("/api/health")
async def health_check():
    result = {"status": "ok", "version": "0.1.0"}
    try:
        missing = _check_tables()
        if missing:
            result["status"] = "degraded"
            result["missing_tables"] = missing
            result["setup_hint"] = "Run: python scripts/setup_database.py"
    except Exception as e:
        result["status"] = "error"
        result["database"] = str(e)
    return result
