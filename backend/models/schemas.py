from pydantic import BaseModel, Field, computed_field
from datetime import datetime, date
from typing import Optional


# --- Config ---

class ConfigCreate(BaseModel):
    tiktok_handle: str
    settings: dict = Field(default_factory=dict)


class ConfigResponse(BaseModel):
    id: int
    tiktok_handle: str
    settings: dict
    created_at: datetime


# --- Videos ---

class VideoCreate(BaseModel):
    title: str
    description: str = ""
    posted_at: datetime
    duration_sec: int = 0
    content_type: str = "general"  # tutorial, review, day-in-life, trend, comedy, general
    hashtags: list[str] = Field(default_factory=list)
    sound_name: str = ""
    views: int = 0
    likes: int = 0
    comments: int = 0
    shares: int = 0
    saves: int = 0
    source: str = "manual"

    @computed_field
    @property
    def engagement_rate(self) -> float:
        if self.views == 0:
            return 0.0
        return (self.likes + self.comments + self.shares + self.saves) / self.views


class VideoUpdate(BaseModel):
    title: Optional[str] = None
    description: Optional[str] = None
    views: Optional[int] = None
    likes: Optional[int] = None
    comments: Optional[int] = None
    shares: Optional[int] = None
    saves: Optional[int] = None
    content_type: Optional[str] = None
    hashtags: Optional[list[str]] = None


class VideoResponse(BaseModel):
    id: int
    title: str
    description: str
    posted_at: datetime
    duration_sec: int
    content_type: str
    hashtags: list[str]
    sound_name: str
    views: int
    likes: int
    comments: int
    shares: int
    saves: int
    engagement_rate: float
    source: str
    created_at: datetime
    updated_at: datetime


# --- Daily Stats ---

class DailyStatsCreate(BaseModel):
    date: date
    followers: int = 0
    following: int = 0
    total_likes: int = 0
    total_views: int = 0
    profile_views: int = 0


class DailyStatsResponse(BaseModel):
    id: int
    date: date
    followers: int
    following: int
    total_likes: int
    total_views: int
    profile_views: int
    new_followers: int
    created_at: datetime


# --- Content Ideas ---

class ContentIdeaCreate(BaseModel):
    title: str
    description: str = ""
    content_type: str = "general"
    estimated_effort: str = "medium"  # quick, medium, production
    hashtags: list[str] = Field(default_factory=list)
    status: str = "idea"  # idea, planned, filming, editing, posted
    scheduled_for: Optional[datetime] = None
    generated_by: str = "manual"  # ai, manual


class ContentIdeaResponse(BaseModel):
    id: int
    title: str
    description: str
    content_type: str
    estimated_effort: str
    hashtags: list[str]
    status: str
    scheduled_for: Optional[datetime]
    generated_by: str
    created_at: datetime


# --- Learnings ---

class LearningResponse(BaseModel):
    id: int
    category: str
    insight: str
    evidence: dict
    confidence: float
    source: str
    is_active: bool
    created_at: datetime
    updated_at: datetime


# --- Session Notes ---

class SessionNoteCreate(BaseModel):
    notes: str
    action_items: list[dict] = Field(default_factory=list)
    metrics_snapshot: dict = Field(default_factory=dict)


class SessionNoteResponse(BaseModel):
    id: int
    session_date: date
    notes: str
    action_items: list[dict]
    metrics_snapshot: dict
    created_at: datetime


# --- Analytics ---

class OverviewStats(BaseModel):
    current_followers: int = 0
    follower_growth: int = 0
    total_videos: int = 0
    total_views: int = 0
    avg_engagement_rate: float = 0.0
    best_content_type: str = ""
    best_posting_hour: int = -1


class TimeSeriesPoint(BaseModel):
    date: str
    value: float


class ContentTypePerformance(BaseModel):
    content_type: str
    avg_views: float
    avg_engagement: float
    count: int


class PostingHeatmapCell(BaseModel):
    day: int  # 0=Monday, 6=Sunday
    hour: int  # 0-23
    avg_views: float
    count: int
