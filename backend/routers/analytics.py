from fastapi import APIRouter, HTTPException, UploadFile, File
from backend.database import get_db
from backend.models.schemas import (
    VideoCreate,
    VideoUpdate,
    VideoResponse,
    DailyStatsCreate,
    DailyStatsResponse,
    OverviewStats,
    ContentTypePerformance,
    PostingHeatmapCell,
)
from backend.services.analytics_engine import AnalyticsEngine
from datetime import datetime
import csv
import io

router = APIRouter()


@router.post("/videos", response_model=dict)
async def create_video(video: VideoCreate):
    db = get_db()
    data = video.model_dump()
    data["posted_at"] = data["posted_at"].isoformat()
    result = db.table("videos").insert(data).execute()
    return {"id": result.data[0]["id"], "message": "Video added successfully"}


@router.get("/videos", response_model=list[VideoResponse])
async def list_videos(
    content_type: str | None = None,
    sort_by: str = "posted_at",
    order: str = "desc",
    limit: int = 50,
):
    db = get_db()
    query = db.table("videos").select("*")
    if content_type:
        query = query.eq("content_type", content_type)
    query = query.order(sort_by, desc=(order == "desc")).limit(limit)
    result = query.execute()
    return result.data


@router.get("/videos/{video_id}", response_model=VideoResponse)
async def get_video(video_id: int):
    db = get_db()
    result = db.table("videos").select("*").eq("id", video_id).execute()
    if not result.data:
        raise HTTPException(status_code=404, detail="Video not found")
    return result.data[0]


@router.put("/videos/{video_id}", response_model=dict)
async def update_video(video_id: int, video: VideoUpdate):
    db = get_db()
    data = {k: v for k, v in video.model_dump().items() if v is not None}
    if not data:
        raise HTTPException(status_code=400, detail="No fields to update")

    # Recalculate engagement rate if metrics changed
    if any(k in data for k in ("views", "likes", "comments", "shares", "saves")):
        existing = db.table("videos").select("*").eq("id", video_id).execute()
        if not existing.data:
            raise HTTPException(status_code=404, detail="Video not found")
        merged = {**existing.data[0], **data}
        views = merged["views"]
        if views > 0:
            data["engagement_rate"] = (
                merged["likes"] + merged["comments"] + merged["shares"] + merged["saves"]
            ) / views
        else:
            data["engagement_rate"] = 0.0

    data["updated_at"] = datetime.utcnow().isoformat()
    db.table("videos").update(data).eq("id", video_id).execute()
    return {"message": "Video updated successfully"}


@router.delete("/videos/{video_id}", response_model=dict)
async def delete_video(video_id: int):
    db = get_db()
    db.table("videos").delete().eq("id", video_id).execute()
    return {"message": "Video deleted successfully"}


@router.post("/videos/import-csv", response_model=dict)
async def import_csv(file: UploadFile = File(...)):
    contents = await file.read()
    text = contents.decode("utf-8")
    reader = csv.DictReader(io.StringIO(text))

    db = get_db()
    count = 0
    for row in reader:
        views = int(row.get("views", 0))
        likes = int(row.get("likes", 0))
        comments = int(row.get("comments", 0))
        shares = int(row.get("shares", 0))
        saves = int(row.get("saves", 0))
        engagement_rate = (likes + comments + shares + saves) / views if views > 0 else 0.0

        hashtags_raw = row.get("hashtags", "")
        hashtags = [h.strip() for h in hashtags_raw.split(",") if h.strip()]

        data = {
            "title": row.get("title", "Untitled"),
            "description": row.get("description", ""),
            "posted_at": row.get("posted_at", datetime.utcnow().isoformat()),
            "duration_sec": int(row.get("duration_sec", 0)),
            "content_type": row.get("content_type", "general"),
            "hashtags": hashtags,
            "sound_name": row.get("sound_name", ""),
            "views": views,
            "likes": likes,
            "comments": comments,
            "shares": shares,
            "saves": saves,
            "engagement_rate": engagement_rate,
            "source": "manual",
        }
        db.table("videos").insert(data).execute()
        count += 1

    return {"message": f"Imported {count} videos successfully"}


# --- Daily Stats ---

@router.post("/daily-stats", response_model=dict)
async def create_daily_stats(stats: DailyStatsCreate):
    db = get_db()
    data = stats.model_dump()
    data["date"] = data["date"].isoformat()

    # Calculate new_followers from previous day
    prev = (
        db.table("daily_stats")
        .select("followers")
        .lt("date", data["date"])
        .order("date", desc=True)
        .limit(1)
        .execute()
    )
    prev_followers = prev.data[0]["followers"] if prev.data else 0
    data["new_followers"] = data["followers"] - prev_followers

    result = db.table("daily_stats").insert(data).execute()
    return {"id": result.data[0]["id"], "message": "Daily stats recorded"}


@router.get("/daily-stats", response_model=list[DailyStatsResponse])
async def list_daily_stats(days: int = 30):
    db = get_db()
    result = (
        db.table("daily_stats")
        .select("*")
        .order("date", desc=True)
        .limit(days)
        .execute()
    )
    return result.data


# --- Overview Analytics ---

@router.get("/overview", response_model=OverviewStats)
async def get_overview():
    engine = AnalyticsEngine()
    return engine.get_overview()


@router.get("/content-performance", response_model=list[ContentTypePerformance])
async def get_content_performance():
    engine = AnalyticsEngine()
    return engine.get_content_type_performance()


@router.get("/posting-heatmap", response_model=list[PostingHeatmapCell])
async def get_posting_heatmap():
    engine = AnalyticsEngine()
    return engine.get_posting_heatmap()
