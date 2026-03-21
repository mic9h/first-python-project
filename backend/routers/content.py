from fastapi import APIRouter, HTTPException
from backend.database import get_db
from backend.models.schemas import ContentIdeaCreate, ContentIdeaResponse
from backend.services.content_engine import ContentEngine

router = APIRouter()


@router.post("/ideas/generate", response_model=list[ContentIdeaResponse])
async def generate_ideas(count: int = 5):
    engine = ContentEngine()
    ideas = await engine.generate_ideas(count=count)
    return ideas


@router.post("/ideas", response_model=dict)
async def create_idea(idea: ContentIdeaCreate):
    db = get_db()
    data = idea.model_dump()
    if data.get("scheduled_for"):
        data["scheduled_for"] = data["scheduled_for"].isoformat()
    result = db.table("content_ideas").insert(data).execute()
    return {"id": result.data[0]["id"], "message": "Idea created"}


@router.get("/ideas", response_model=list[ContentIdeaResponse])
async def list_ideas(status: str | None = None, limit: int = 50):
    db = get_db()
    query = db.table("content_ideas").select("*")
    if status:
        query = query.eq("status", status)
    result = query.order("created_at", desc=True).limit(limit).execute()
    return result.data


@router.put("/ideas/{idea_id}/status", response_model=dict)
async def update_idea_status(idea_id: int, status: str):
    valid = {"idea", "planned", "filming", "editing", "posted"}
    if status not in valid:
        raise HTTPException(status_code=400, detail=f"Status must be one of: {valid}")
    db = get_db()
    db.table("content_ideas").update({"status": status}).eq("id", idea_id).execute()
    return {"message": f"Idea status updated to {status}"}


@router.delete("/ideas/{idea_id}", response_model=dict)
async def delete_idea(idea_id: int):
    db = get_db()
    db.table("content_ideas").delete().eq("id", idea_id).execute()
    return {"message": "Idea deleted"}


@router.post("/hashtags/suggest", response_model=dict)
async def suggest_hashtags(description: str, count: int = 10):
    engine = ContentEngine()
    hashtags = await engine.suggest_hashtags(description, count)
    return {"hashtags": hashtags}
