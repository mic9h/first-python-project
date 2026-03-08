"""
Supabase Database Setup Script

Creates all tables for the TikTok Growth Tracker app.

Two modes:
  1. Direct connection: connects to Supabase Postgres via psycopg2
  2. SQL dump fallback: prints SQL for pasting into Supabase Dashboard SQL Editor

Usage:
    python scripts/setup_database.py            # Try connect, fallback to SQL dump
    python scripts/setup_database.py --dump-sql  # Just print the SQL
    python scripts/setup_database.py --seed      # Include seed data without prompting
"""
import os
import sys
from pathlib import Path
from urllib.parse import urlparse, parse_qs, urlencode, urlunparse

from dotenv import load_dotenv

load_dotenv()

SCRIPT_DIR = Path(__file__).parent
SQL_PATH = SCRIPT_DIR / "create_tables.sql"

EXPECTED_TABLES = [
    "algorithm_knowledge", "config", "content_ideas", "daily_stats",
    "learnings", "session_notes", "trends", "videos",
]

# Algorithm knowledge seed data (duplicated here so SQL dump works without imports)
SEED_RULES = [
    ("hook", "First 1-3 seconds must hook the viewer",
     "Use text overlay, a question, face close-up, or unexpected visual in the first 1-3 seconds. Videos that lose viewers in the first second get suppressed.",
     "official", 0.95),
    ("watch_time", "Completion rate is the #1 ranking factor",
     "Videos where viewers watch to the end (or rewatch) get pushed to more For You pages. Keep videos concise and avoid unnecessary padding.",
     "official", 0.95),
    ("engagement", "Reply to comments within the first hour",
     "Engagement in the first 1-2 hours after posting strongly influences distribution. Replying to comments boosts the video in the algorithm.",
     "community", 0.8),
    ("duration", "21-34 seconds is the sweet spot for tutorials",
     "Short enough for high completion rate, long enough to deliver value. For tech content, this means one concept per video.",
     "community", 0.7),
    ("posting_time", "Post when your audience is active",
     "For US tech audiences: 7-9 AM, 12-1 PM, 7-10 PM EST tend to perform well. Check your own analytics for your specific audience.",
     "community", 0.65),
    ("hashtags", "Mix broad and niche hashtags",
     "Use 3-5 hashtags: 1-2 broad (#tech, #coding), 2-3 niche (#pythontips, #webdevtutorial). Avoid banned or oversaturated tags.",
     "community", 0.75),
    ("consistency", "Post 1-3 times daily for fastest growth",
     "The algorithm favors consistent creators. Quality over quantity, but 1 video/day minimum is recommended for growth phase.",
     "community", 0.7),
    ("for_you_page", "Videos are tested in small batches first",
     "TikTok shows your video to ~200-500 people first. If engagement is high (likes, comments, shares, completion), it expands to larger audiences in waves.",
     "official", 0.9),
    ("captions", "On-screen text increases watch time",
     "Adding captions/subtitles increases watch time because viewers read along. This also helps with accessibility and sound-off viewing.",
     "community", 0.8),
    ("trending", "Use trending sounds for discovery",
     "Videos using trending sounds get boosted in discovery. For tech content, you can add a trending sound at low volume behind your voiceover.",
     "community", 0.75),
    ("retention", "Pattern interrupts prevent scroll-away",
     "Change visuals, camera angles, or add text every 2-3 seconds to maintain attention. Monotone delivery and static shots lose viewers.",
     "community", 0.8),
    ("sharing", "Shareable content gets exponential reach",
     "Videos that get shared (via DMs or other platforms) receive massive algorithmic boosts. Create content people want to send to friends — tips, relatable humor, surprising facts.",
     "official", 0.85),
]


def sql_escape(s: str) -> str:
    """Escape a string for SQL single-quoted literals."""
    return s.replace("'", "''")


def ensure_ssl(url: str) -> str:
    """Add sslmode=require to DATABASE_URL if missing."""
    if "sslmode" not in url:
        separator = "&" if "?" in url else "?"
        return url + separator + "sslmode=require"
    return url


def generate_seed_sql() -> str:
    """Generate INSERT statements for algorithm_knowledge seed data."""
    lines = ["-- Seed: Algorithm Knowledge Base"]
    for topic, rule, details, source, confidence in SEED_RULES:
        lines.append(
            f"INSERT INTO algorithm_knowledge (topic, rule, details, source, confidence, is_current, last_verified) "
            f"VALUES ('{sql_escape(topic)}', '{sql_escape(rule)}', '{sql_escape(details)}', "
            f"'{sql_escape(source)}', {confidence}, true, now()) "
            f"ON CONFLICT (topic, rule) DO NOTHING;"
        )
    return "\n".join(lines)


def run_via_psycopg2(database_url: str, sql: str, include_seed: bool):
    """Tier 1: direct Postgres connection."""
    import psycopg2

    url = ensure_ssl(database_url)
    print(f"Connecting to Supabase Postgres...")

    try:
        conn = psycopg2.connect(url, connect_timeout=10)
        conn.autocommit = True
        cur = conn.cursor()
    except Exception as e:
        raise ConnectionError(
            f"Could not connect: {e}\n\n"
            "Common fixes:\n"
            "  - Go to Supabase Dashboard > Settings > Database > Connection string > URI\n"
            "  - Copy the full connection string and set it as DATABASE_URL in .env\n"
            "  - Make sure sslmode=require is in the URL\n"
            "  - Check that your IP is allowed (Settings > Database > Network)"
        )

    print("Creating tables...")
    cur.execute(sql)
    print("Tables created!")

    if include_seed:
        print("Seeding algorithm knowledge...")
        cur.execute(generate_seed_sql())
        print("Seed data inserted!")

    # Verify
    cur.execute("""
        SELECT table_name FROM information_schema.tables
        WHERE table_schema = 'public' ORDER BY table_name;
    """)
    tables = [row[0] for row in cur.fetchall()]

    print("\nTables in database:")
    for t in tables:
        marker = "  [ok]" if t in EXPECTED_TABLES else "  [--]"
        print(f"  {marker} {t}")

    missing = set(EXPECTED_TABLES) - set(tables)
    if missing:
        print(f"\nWARNING: Missing tables: {', '.join(sorted(missing))}")
    else:
        print(f"\nAll {len(EXPECTED_TABLES)} tables created successfully!")

    cur.close()
    conn.close()


def print_sql_dump(sql: str, include_seed: bool):
    """Tier 2: print SQL for manual execution in Supabase Dashboard."""
    print()
    print("=" * 60)
    print("  SQL DUMP MODE")
    print("=" * 60)
    print()
    print("Could not connect to the database automatically.")
    print("Paste the SQL below into the Supabase SQL Editor:")
    print()
    print("  1. Go to https://supabase.com/dashboard")
    print("  2. Select your project")
    print("  3. Click 'SQL Editor' in the left sidebar")
    print("  4. Click '+ New query'")
    print("  5. Paste ALL the SQL below and click 'Run'")
    print()
    print("-" * 60)
    print(sql)
    if include_seed:
        print()
        print(generate_seed_sql())
    print("-" * 60)
    print()
    print("After running the SQL, start the app:")
    print("  uvicorn backend.main:app --reload")
    print()


def main():
    if not SQL_PATH.exists():
        print(f"ERROR: {SQL_PATH} not found")
        sys.exit(1)

    sql = SQL_PATH.read_text()
    dump_only = "--dump-sql" in sys.argv
    include_seed = "--seed" in sys.argv

    # Ask about seeding if not specified via flag
    if not dump_only and not include_seed:
        answer = input("Include algorithm knowledge seed data? (y/n): ").strip().lower()
        include_seed = answer == "y"

    # --dump-sql: skip connection, just print SQL
    if dump_only:
        print_sql_dump(sql, include_seed)
        return

    # Try psycopg2 connection first
    database_url = os.getenv("DATABASE_URL", "")

    try:
        import psycopg2  # noqa: F401
    except ImportError:
        print("psycopg2 not installed (pip install psycopg2-binary)")
        print("Falling back to SQL dump mode...")
        print_sql_dump(sql, include_seed)
        return

    if not database_url:
        print("DATABASE_URL not set in .env file.")
        print("Falling back to SQL dump mode...")
        print_sql_dump(sql, include_seed)
        return

    try:
        run_via_psycopg2(database_url, sql, include_seed)
        print()
        print("Setup complete! Start the app:")
        print("  Backend:  uvicorn backend.main:app --reload")
        print("  Frontend: cd frontend && npm run dev")
    except (ConnectionError, Exception) as e:
        print(f"\n{e}")
        print("\nFalling back to SQL dump mode...")
        print_sql_dump(sql, include_seed)


if __name__ == "__main__":
    main()
