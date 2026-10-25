import sqlite3
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent
DB_PATH = BASE_DIR / "database" / "ai_learning.db"

def get_content_db():
    DB_PATH.parent.mkdir(parents=True, exist_ok=True)
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA foreign_keys = ON")
    return conn

def load_recommendations_db():
    conn = get_content_db()
    rows = conn.execute("""
        SELECT id, interest, skill_level, course, project, career, difficulty,
               relevance, skills, description, youtube_url, github_url, github_link_type
        FROM recommendations
        ORDER BY id
    """).fetchall()
    conn.close()
    return [dict(row) for row in rows]

def get_resource_db(recommendation_id, resource_type):
    conn = get_content_db()
    row = conn.execute("""
        SELECT recommendation_id, resource_type, name, youtube_url,
               free_course_url, paid_course_url, project_url
        FROM resources
        WHERE recommendation_id = ? AND resource_type = ?
        LIMIT 1
    """, (recommendation_id, resource_type)).fetchone()
    conn.close()
    return dict(row) if row else {}
