from collections import defaultdict
from datetime import datetime
from backend.database import get_db
from backend.models.schemas import (
    OverviewStats,
    ContentTypePerformance,
    PostingHeatmapCell,
)


class AnalyticsEngine:
    def __init__(self):
        self.db = get_db()

    def get_overview(self) -> OverviewStats:
        videos = self.db.table("videos").select("*").execute().data
        daily = (
            self.db.table("daily_stats")
            .select("*")
            .order("date", desc=True)
            .limit(2)
            .execute()
            .data
        )

        current_followers = daily[0]["followers"] if daily else 0
        follower_growth = daily[0].get("new_followers", 0) if daily else 0
        total_views = sum(v["views"] for v in videos)

        engagement_rates = [v["engagement_rate"] for v in videos if v.get("engagement_rate")]
        avg_engagement = sum(engagement_rates) / len(engagement_rates) if engagement_rates else 0.0

        # Best content type by avg engagement
        by_type: dict[str, list[float]] = defaultdict(list)
        for v in videos:
            if v.get("engagement_rate"):
                by_type[v["content_type"]].append(v["engagement_rate"])
        best_type = ""
        if by_type:
            best_type = max(by_type, key=lambda t: sum(by_type[t]) / len(by_type[t]))

        # Best posting hour by avg views
        by_hour: dict[int, list[int]] = defaultdict(list)
        for v in videos:
            if v.get("posted_at"):
                hour = datetime.fromisoformat(v["posted_at"]).hour
                by_hour[hour].append(v["views"])
        best_hour = -1
        if by_hour:
            best_hour = max(by_hour, key=lambda h: sum(by_hour[h]) / len(by_hour[h]))

        return OverviewStats(
            current_followers=current_followers,
            follower_growth=follower_growth,
            total_videos=len(videos),
            total_views=total_views,
            avg_engagement_rate=round(avg_engagement, 4),
            best_content_type=best_type,
            best_posting_hour=best_hour,
        )

    def get_content_type_performance(self) -> list[ContentTypePerformance]:
        videos = self.db.table("videos").select("*").execute().data
        by_type: dict[str, list[dict]] = defaultdict(list)
        for v in videos:
            by_type[v["content_type"]].append(v)

        results = []
        for ct, vids in by_type.items():
            avg_views = sum(v["views"] for v in vids) / len(vids)
            avg_eng = sum(v.get("engagement_rate", 0) for v in vids) / len(vids)
            results.append(
                ContentTypePerformance(
                    content_type=ct,
                    avg_views=round(avg_views, 1),
                    avg_engagement=round(avg_eng, 4),
                    count=len(vids),
                )
            )
        return sorted(results, key=lambda r: r.avg_engagement, reverse=True)

    def get_posting_heatmap(self) -> list[PostingHeatmapCell]:
        videos = self.db.table("videos").select("posted_at, views").execute().data
        grid: dict[tuple[int, int], list[int]] = defaultdict(list)

        for v in videos:
            if not v.get("posted_at"):
                continue
            dt = datetime.fromisoformat(v["posted_at"])
            day = dt.weekday()  # 0=Monday
            hour = dt.hour
            grid[(day, hour)].append(v["views"])

        cells = []
        for (day, hour), views_list in grid.items():
            cells.append(
                PostingHeatmapCell(
                    day=day,
                    hour=hour,
                    avg_views=round(sum(views_list) / len(views_list), 1),
                    count=len(views_list),
                )
            )
        return cells
