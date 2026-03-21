import json
from backend.config import get_settings
from backend.database import get_db

try:
    import anthropic
except ImportError:
    anthropic = None


class ContentEngine:
    def __init__(self):
        settings = get_settings()
        if anthropic and settings.anthropic_api_key:
            self.client = anthropic.Anthropic(api_key=settings.anthropic_api_key)
        else:
            self.client = None

    def _get_performance_context(self) -> str:
        db = get_db()
        videos = (
            db.table("videos")
            .select("content_type, views, likes, comments, shares, engagement_rate")
            .order("posted_at", desc=True)
            .limit(20)
            .execute()
            .data
        )
        learnings = (
            db.table("learnings")
            .select("category, insight, confidence")
            .eq("is_active", True)
            .gte("confidence", 0.5)
            .order("confidence", desc=True)
            .limit(10)
            .execute()
            .data
        )

        context = "Recent video performance:\n"
        for v in videos[:10]:
            context += f"- {v['content_type']}: {v['views']} views, {v['engagement_rate']:.2%} engagement\n"

        if learnings:
            context += "\nKey learnings:\n"
            for l in learnings:
                context += f"- [{l['category']}] {l['insight']} (confidence: {l['confidence']:.0%})\n"

        return context

    async def generate_ideas(self, count: int = 5) -> list[dict]:
        if not self.client:
            return self._fallback_ideas(count)

        performance = self._get_performance_context()
        prompt = f"""You are a TikTok content strategist for a tech/programming creator.
Based on their performance data, generate {count} content ideas.

{performance}

For each idea provide a JSON array with objects containing:
- title: catchy TikTok title
- description: brief description of the video concept
- content_type: one of (tutorial, review, day-in-life, trend, comedy)
- estimated_effort: one of (quick, medium, production)
- hashtags: list of relevant hashtags (without #)

Return ONLY the JSON array, no other text."""

        message = self.client.messages.create(
            model="claude-haiku-4-5-20251001",
            max_tokens=1500,
            messages=[{"role": "user", "content": prompt}],
        )

        try:
            text = message.content[0].text.strip()
            # Handle markdown code blocks
            if text.startswith("```"):
                text = text.split("\n", 1)[1].rsplit("```", 1)[0].strip()
            ideas = json.loads(text)
        except (json.JSONDecodeError, IndexError):
            return self._fallback_ideas(count)

        # Save to database
        db = get_db()
        saved = []
        for idea in ideas[:count]:
            idea["generated_by"] = "ai"
            idea["status"] = "idea"
            result = db.table("content_ideas").insert(idea).execute()
            saved.append(result.data[0])

        return saved

    async def suggest_hashtags(self, description: str, count: int = 10) -> list[str]:
        if not self.client:
            return ["tech", "coding", "programming", "developer", "learntocode",
                    "techcreator", "codingtips", "webdev", "softwareengineer", "techtok"]

        prompt = f"""Suggest {count} TikTok hashtags for this tech/programming video:
"{description}"

Return ONLY a JSON array of hashtag strings (without the # symbol).
Mix popular broad hashtags with niche-specific ones for maximum reach."""

        message = self.client.messages.create(
            model="claude-haiku-4-5-20251001",
            max_tokens=300,
            messages=[{"role": "user", "content": prompt}],
        )

        try:
            text = message.content[0].text.strip()
            if text.startswith("```"):
                text = text.split("\n", 1)[1].rsplit("```", 1)[0].strip()
            return json.loads(text)
        except (json.JSONDecodeError, IndexError):
            return ["tech", "coding", "programming", "developer", "techtok"]

    def _fallback_ideas(self, count: int) -> list[dict]:
        fallback = [
            {"title": "5 VS Code shortcuts you don't know", "description": "Quick keyboard shortcuts that save time", "content_type": "tutorial", "estimated_effort": "quick", "hashtags": ["vscode", "coding", "productivity"]},
            {"title": "Day in the life of a developer", "description": "Show your daily routine and workflow", "content_type": "day-in-life", "estimated_effort": "medium", "hashtags": ["devlife", "dayinthelife", "tech"]},
            {"title": "This AI tool changed everything", "description": "Review a new AI tool for developers", "content_type": "review", "estimated_effort": "medium", "hashtags": ["ai", "devtools", "techreview"]},
            {"title": "POV: debugging at 3am", "description": "Relatable coding humor", "content_type": "comedy", "estimated_effort": "quick", "hashtags": ["coding", "programmer", "debug"]},
            {"title": "Build this in 60 seconds", "description": "Speed-build a mini project", "content_type": "tutorial", "estimated_effort": "production", "hashtags": ["coding", "webdev", "tutorial"]},
        ]
        return fallback[:count]
