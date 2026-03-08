from fastapi import APIRouter
from backend.database import get_db
from backend.models.schemas import (
    LearningResponse,
    SessionNoteCreate,
    SessionNoteResponse,
)
from backend.services.learning_engine import LearningEngine
from datetime import date

router = APIRouter()


@router.get("/insights", response_model=list[LearningResponse])
async def get_insights(min_confidence: float = 0.0):
    db = get_db()
    result = (
        db.table("learnings")
        .select("*")
        .eq("is_active", True)
        .gte("confidence", min_confidence)
        .order("confidence", desc=True)
        .execute()
    )
    return result.data


@router.post("/analyze", response_model=dict)
async def run_analysis():
    engine = LearningEngine()
    new_insights = engine.analyze_all()
    return {"new_insights": len(new_insights), "message": "Analysis complete"}


@router.post("/sessions", response_model=dict)
async def create_session_note(note: SessionNoteCreate):
    db = get_db()
    data = note.model_dump()
    data["session_date"] = date.today().isoformat()
    result = db.table("session_notes").insert(data).execute()
    return {"id": result.data[0]["id"], "message": "Session note saved"}


@router.get("/sessions/latest", response_model=SessionNoteResponse | None)
async def get_latest_session():
    db = get_db()
    result = (
        db.table("session_notes")
        .select("*")
        .order("created_at", desc=True)
        .limit(1)
        .execute()
    )
    return result.data[0] if result.data else None


@router.get("/sessions", response_model=list[SessionNoteResponse])
async def list_sessions(limit: int = 10):
    db = get_db()
    result = (
        db.table("session_notes")
        .select("*")
        .order("created_at", desc=True)
        .limit(limit)
        .execute()
    )
    return result.data
