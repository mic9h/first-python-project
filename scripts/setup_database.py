"""
Supabase Database Setup Script

Creates all tables for the TikTok Growth Tracker app by connecting
directly to the Supabase Postgres database.

Usage:
    1. Set DATABASE_URL in your .env file (from Supabase Dashboard > Settings > Database > Connection string)
    2. Run: python scripts/setup_database.py
"""
import os
import sys
from pathlib import Path

try:
    import psycopg2
except ImportError:
    print("psycopg2 not installed. Run: pip install psycopg2-binary")
    sys.exit(1)

from dotenv import load_dotenv

load_dotenv()

DATABASE_URL = os.getenv("DATABASE_URL")
if not DATABASE_URL:
    print("ERROR: DATABASE_URL not set in .env file.")
    print()
    print("To find it:")
    print("  1. Go to your Supabase project dashboard")
    print("  2. Settings > Database > Connection string > URI")
    print("  3. Copy it and add to your .env file as DATABASE_URL=...")
    sys.exit(1)


def run_setup():
    sql_path = Path(__file__).parent / "create_tables.sql"
    if not sql_path.exists():
        print(f"ERROR: {sql_path} not found.")
        sys.exit(1)

    sql = sql_path.read_text()

    print("Connecting to Supabase Postgres...")
    try:
        conn = psycopg2.connect(DATABASE_URL)
        conn.autocommit = True
        cur = conn.cursor()
    except Exception as e:
        print(f"ERROR: Could not connect to database: {e}")
        print()
        print("Common fixes:")
        print("  - Check your DATABASE_URL is correct")
        print("  - Make sure your IP is allowed (Supabase > Settings > Database > Network)")
        sys.exit(1)

    print("Creating tables...")
    try:
        cur.execute(sql)
        print("Tables created successfully!")
    except Exception as e:
        print(f"ERROR creating tables: {e}")
        sys.exit(1)

    # Verify tables
    cur.execute("""
        SELECT table_name FROM information_schema.tables
        WHERE table_schema = 'public'
        ORDER BY table_name;
    """)
    tables = [row[0] for row in cur.fetchall()]

    expected = ["algorithm_knowledge", "config", "content_ideas", "daily_stats",
                "learnings", "session_notes", "trends", "videos"]

    print()
    print("Tables in database:")
    for t in tables:
        marker = "  [ok]" if t in expected else "  [--]"
        print(f"  {marker} {t}")

    missing = set(expected) - set(tables)
    if missing:
        print(f"\nWARNING: Missing tables: {', '.join(missing)}")
    else:
        print(f"\nAll {len(expected)} tables created successfully!")

    cur.close()
    conn.close()

    # Ask about seeding
    print()
    answer = input("Seed algorithm knowledge base? (y/n): ").strip().lower()
    if answer == "y":
        print("Seeding algorithm knowledge...")
        # Import and run seed script
        sys.path.insert(0, str(Path(__file__).parent.parent))
        from scripts.seed_algorithm_knowledge import seed
        seed()

    print()
    print("Setup complete! You can now run the app:")
    print("  Backend:  uvicorn backend.main:app --reload")
    print("  Frontend: cd frontend && npm run dev")


if __name__ == "__main__":
    run_setup()
