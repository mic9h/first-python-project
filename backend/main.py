from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from backend.routers import analytics, content, learning

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


@app.get("/api/health")
async def health_check():
    return {"status": "ok", "version": "0.1.0"}
