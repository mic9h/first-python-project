"""Seed the algorithm_knowledge table with known TikTok algorithm rules."""
import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from backend.database import get_db
from datetime import datetime

RULES = [
    {
        "topic": "hook",
        "rule": "First 1-3 seconds must hook the viewer",
        "details": "Use text overlay, a question, face close-up, or unexpected visual in the first 1-3 seconds. Videos that lose viewers in the first second get suppressed.",
        "source": "official",
        "confidence": 0.95,
    },
    {
        "topic": "watch_time",
        "rule": "Completion rate is the #1 ranking factor",
        "details": "Videos where viewers watch to the end (or rewatch) get pushed to more For You pages. Keep videos concise and avoid unnecessary padding.",
        "source": "official",
        "confidence": 0.95,
    },
    {
        "topic": "engagement",
        "rule": "Reply to comments within the first hour",
        "details": "Engagement in the first 1-2 hours after posting strongly influences distribution. Replying to comments boosts the video in the algorithm.",
        "source": "community",
        "confidence": 0.8,
    },
    {
        "topic": "duration",
        "rule": "21-34 seconds is the sweet spot for tutorials",
        "details": "Short enough for high completion rate, long enough to deliver value. For tech content, this means one concept per video.",
        "source": "community",
        "confidence": 0.7,
    },
    {
        "topic": "posting_time",
        "rule": "Post when your audience is active",
        "details": "For US tech audiences: 7-9 AM, 12-1 PM, 7-10 PM EST tend to perform well. Check your own analytics for your specific audience.",
        "source": "community",
        "confidence": 0.65,
    },
    {
        "topic": "hashtags",
        "rule": "Mix broad and niche hashtags",
        "details": "Use 3-5 hashtags: 1-2 broad (#tech, #coding), 2-3 niche (#pythontips, #webdevtutorial). Avoid banned or oversaturated tags.",
        "source": "community",
        "confidence": 0.75,
    },
    {
        "topic": "consistency",
        "rule": "Post 1-3 times daily for fastest growth",
        "details": "The algorithm favors consistent creators. Quality over quantity, but 1 video/day minimum is recommended for growth phase.",
        "source": "community",
        "confidence": 0.7,
    },
    {
        "topic": "for_you_page",
        "rule": "Videos are tested in small batches first",
        "details": "TikTok shows your video to ~200-500 people first. If engagement is high (likes, comments, shares, completion), it expands to larger audiences in waves.",
        "source": "official",
        "confidence": 0.9,
    },
    {
        "topic": "captions",
        "rule": "On-screen text increases watch time",
        "details": "Adding captions/subtitles increases watch time because viewers read along. This also helps with accessibility and sound-off viewing.",
        "source": "community",
        "confidence": 0.8,
    },
    {
        "topic": "trending",
        "rule": "Use trending sounds for discovery",
        "details": "Videos using trending sounds get boosted in discovery. For tech content, you can add a trending sound at low volume behind your voiceover.",
        "source": "community",
        "confidence": 0.75,
    },
    {
        "topic": "retention",
        "rule": "Pattern interrupts prevent scroll-away",
        "details": "Change visuals, camera angles, or add text every 2-3 seconds to maintain attention. Monotone delivery and static shots lose viewers.",
        "source": "community",
        "confidence": 0.8,
    },
    {
        "topic": "sharing",
        "rule": "Shareable content gets exponential reach",
        "details": "Videos that get shared (via DMs or other platforms) receive massive algorithmic boosts. Create content people want to send to friends — tips, relatable humor, surprising facts.",
        "source": "official",
        "confidence": 0.85,
    },
]


def seed():
    db = get_db()
    now = datetime.utcnow().isoformat()
    for rule in RULES:
        rule["last_verified"] = now
        rule["is_current"] = True
        db.table("algorithm_knowledge").upsert(rule, on_conflict="topic,rule").execute()
    print(f"Seeded {len(RULES)} algorithm rules.")


if __name__ == "__main__":
    seed()
