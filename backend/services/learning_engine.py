from collections import defaultdict
from datetime import datetime
from backend.database import get_db


class LearningEngine:
    def __init__(self):
        self.db = get_db()

    def analyze_all(self) -> list[dict]:
        videos = self.db.table("videos").select("*").execute().data
        if len(videos) < 3:
            return []

        new_insights = []
        new_insights.extend(self._analyze_content_types(videos))
        new_insights.extend(self._analyze_posting_times(videos))
        new_insights.extend(self._analyze_hashtags(videos))
        new_insights.extend(self._analyze_duration(videos))

        # Save new insights
        for insight in new_insights:
            self._upsert_learning(insight)

        return new_insights

    def _analyze_content_types(self, videos: list[dict]) -> list[dict]:
        insights = []
        by_type: dict[str, list[dict]] = defaultdict(list)
        for v in videos:
            by_type[v["content_type"]].append(v)

        overall_avg = sum(v.get("engagement_rate", 0) for v in videos) / len(videos)

        for ct, vids in by_type.items():
            if len(vids) < 3:
                continue
            avg_eng = sum(v.get("engagement_rate", 0) for v in vids) / len(vids)
            avg_views = sum(v["views"] for v in vids) / len(vids)
            ratio = avg_eng / overall_avg if overall_avg > 0 else 1.0

            if ratio > 1.2:
                insights.append({
                    "category": "content_type",
                    "insight": f"Your {ct} videos get {ratio:.1f}x better engagement than average ({avg_eng:.1%} vs {overall_avg:.1%})",
                    "evidence": {"content_type": ct, "count": len(vids), "avg_engagement": avg_eng, "avg_views": avg_views},
                    "confidence": min(len(vids) / 10, 0.9),
                    "source": "auto_analysis",
                })
            elif ratio < 0.8:
                insights.append({
                    "category": "content_type",
                    "insight": f"Your {ct} videos underperform at {avg_eng:.1%} engagement (average is {overall_avg:.1%})",
                    "evidence": {"content_type": ct, "count": len(vids), "avg_engagement": avg_eng, "avg_views": avg_views},
                    "confidence": min(len(vids) / 10, 0.9),
                    "source": "auto_analysis",
                })

        return insights

    def _analyze_posting_times(self, videos: list[dict]) -> list[dict]:
        insights = []
        by_hour: dict[int, list[dict]] = defaultdict(list)
        by_day: dict[int, list[dict]] = defaultdict(list)

        for v in videos:
            if not v.get("posted_at"):
                continue
            dt = datetime.fromisoformat(v["posted_at"])
            by_hour[dt.hour].append(v)
            by_day[dt.weekday()].append(v)

        # Best hour
        if by_hour:
            best_hour = max(by_hour, key=lambda h: sum(v["views"] for v in by_hour[h]) / len(by_hour[h]))
            hour_vids = by_hour[best_hour]
            if len(hour_vids) >= 2:
                avg_views = sum(v["views"] for v in hour_vids) / len(hour_vids)
                overall_avg = sum(v["views"] for v in videos) / len(videos)
                if avg_views > overall_avg * 1.1:
                    hour_label = f"{best_hour}:00" if best_hour >= 10 else f"0{best_hour}:00"
                    insights.append({
                        "category": "posting_time",
                        "insight": f"Videos posted around {hour_label} get {avg_views:.0f} avg views vs {overall_avg:.0f} overall",
                        "evidence": {"hour": best_hour, "count": len(hour_vids), "avg_views": avg_views},
                        "confidence": min(len(hour_vids) / 5, 0.8),
                        "source": "auto_analysis",
                    })

        # Best day
        day_names = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"]
        if by_day:
            best_day = max(by_day, key=lambda d: sum(v["views"] for v in by_day[d]) / len(by_day[d]))
            day_vids = by_day[best_day]
            if len(day_vids) >= 2:
                avg_views = sum(v["views"] for v in day_vids) / len(day_vids)
                insights.append({
                    "category": "posting_time",
                    "insight": f"{day_names[best_day]}s are your best posting day with {avg_views:.0f} avg views",
                    "evidence": {"day": best_day, "day_name": day_names[best_day], "count": len(day_vids), "avg_views": avg_views},
                    "confidence": min(len(day_vids) / 5, 0.8),
                    "source": "auto_analysis",
                })

        return insights

    def _analyze_hashtags(self, videos: list[dict]) -> list[dict]:
        insights = []
        hashtag_perf: dict[str, list[float]] = defaultdict(list)

        for v in videos:
            for tag in v.get("hashtags", []):
                hashtag_perf[tag].append(v.get("engagement_rate", 0))

        overall_avg = sum(v.get("engagement_rate", 0) for v in videos) / len(videos)

        for tag, rates in hashtag_perf.items():
            if len(rates) < 3:
                continue
            avg = sum(rates) / len(rates)
            if avg > overall_avg * 1.3:
                insights.append({
                    "category": "hashtag",
                    "insight": f"#{tag} correlates with higher engagement ({avg:.1%} vs {overall_avg:.1%} average)",
                    "evidence": {"hashtag": tag, "count": len(rates), "avg_engagement": avg},
                    "confidence": min(len(rates) / 8, 0.85),
                    "source": "auto_analysis",
                })

        return insights

    def _analyze_duration(self, videos: list[dict]) -> list[dict]:
        insights = []
        short = [v for v in videos if 0 < v.get("duration_sec", 0) <= 30]
        medium = [v for v in videos if 30 < v.get("duration_sec", 0) <= 60]
        long = [v for v in videos if v.get("duration_sec", 0) > 60]

        buckets = [("under 30 seconds", short), ("30-60 seconds", medium), ("over 60 seconds", long)]
        best_bucket = None
        best_avg = 0

        for label, vids in buckets:
            if len(vids) < 2:
                continue
            avg = sum(v.get("engagement_rate", 0) for v in vids) / len(vids)
            if avg > best_avg:
                best_avg = avg
                best_bucket = (label, vids, avg)

        if best_bucket:
            label, vids, avg = best_bucket
            insights.append({
                "category": "format",
                "insight": f"Videos {label} perform best for you ({avg:.1%} engagement, {len(vids)} videos)",
                "evidence": {"duration_bucket": label, "count": len(vids), "avg_engagement": avg},
                "confidence": min(len(vids) / 6, 0.8),
                "source": "auto_analysis",
            })

        return insights

    def _upsert_learning(self, insight: dict):
        existing = (
            self.db.table("learnings")
            .select("*")
            .eq("category", insight["category"])
            .eq("source", "auto_analysis")
            .execute()
            .data
        )

        # Check if a similar insight already exists
        for e in existing:
            evidence = e.get("evidence", {})
            new_evidence = insight.get("evidence", {})
            # Match by key identifiers
            if (insight["category"] == "content_type" and evidence.get("content_type") == new_evidence.get("content_type")) or \
               (insight["category"] == "hashtag" and evidence.get("hashtag") == new_evidence.get("hashtag")) or \
               (insight["category"] == "posting_time" and evidence.get("hour") == new_evidence.get("hour") and evidence.get("day") == new_evidence.get("day")) or \
               (insight["category"] == "format" and evidence.get("duration_bucket") == new_evidence.get("duration_bucket")):
                # Update existing
                new_confidence = min(e["confidence"] + 0.1, 1.0)
                self.db.table("learnings").update({
                    "insight": insight["insight"],
                    "evidence": insight["evidence"],
                    "confidence": new_confidence,
                    "updated_at": datetime.utcnow().isoformat(),
                }).eq("id", e["id"]).execute()
                return

        # Insert new
        insight["is_active"] = True
        self.db.table("learnings").insert(insight).execute()
