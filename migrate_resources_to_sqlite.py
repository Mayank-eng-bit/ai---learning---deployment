import csv
import sqlite3
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent
DB_PATH = BASE_DIR / "database" / "ai_learning.db"
DATASET_DIR = BASE_DIR / "dataset"
RECOMMENDATIONS_CSV = DATASET_DIR / "recommendations.csv"
RESOURCES_CSV = DATASET_DIR / "resources.csv"

DB_PATH.parent.mkdir(parents=True, exist_ok=True)
conn = sqlite3.connect(DB_PATH)
conn.execute("PRAGMA foreign_keys = ON")

conn.execute("""
CREATE TABLE IF NOT EXISTS recommendations (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    interest TEXT NOT NULL,
    skill_level TEXT NOT NULL,
    course TEXT NOT NULL,
    project TEXT NOT NULL,
    career TEXT NOT NULL,
    difficulty TEXT NOT NULL,
    relevance INTEGER NOT NULL,
    skills TEXT,
    description TEXT,
    youtube_url TEXT,
    github_url TEXT,
    github_link_type TEXT
)
""")

conn.execute("""
CREATE TABLE IF NOT EXISTS resources (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    recommendation_id INTEGER,
    resource_type TEXT NOT NULL CHECK(resource_type IN ('course','project')),
    name TEXT NOT NULL,
    youtube_url TEXT,
    free_course_url TEXT,
    paid_course_url TEXT,
    project_url TEXT,
    UNIQUE(recommendation_id, resource_type),
    FOREIGN KEY(recommendation_id) REFERENCES recommendations(id) ON DELETE SET NULL
)
""")

conn.execute("CREATE INDEX IF NOT EXISTS idx_recommendations_interest_skill ON recommendations(interest, skill_level)")
conn.execute("CREATE INDEX IF NOT EXISTS idx_resources_recommendation ON resources(recommendation_id)")

with open(RECOMMENDATIONS_CSV, encoding='utf-8', newline='') as f:
    recommendations = list(csv.DictReader(f))

with open(RESOURCES_CSV, encoding='utf-8', newline='') as f:
    resource_rows = list(csv.DictReader(f))

# Preserve the existing users/history/saved-learning tables. Only content tables are rebuilt.
conn.execute("DELETE FROM resources")
conn.execute("DELETE FROM recommendations")

# Source lookup. For duplicate course names, the first matching resource is reused for each recommendation.
resource_lookup = {}
for r in resource_rows:
    key = (r.get('type','').strip(), r.get('name','').strip())
    if key not in resource_lookup:
        resource_lookup[key] = r

matched_resource_keys = set()

for row in recommendations:
    cur = conn.execute("""
        INSERT INTO recommendations
        (interest, skill_level, course, project, career, difficulty, relevance, skills, description, youtube_url, github_url, github_link_type)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    """, (
        row.get('interest','').strip(), row.get('skill_level','').strip(),
        row.get('course','').strip(), row.get('project','').strip(),
        row.get('career','').strip(), row.get('difficulty','').strip(),
        int(float(row.get('relevance') or 0)), row.get('skills','').strip(),
        row.get('description','').strip(), row.get('youtube_url','').strip(),
        row.get('github_url','').strip(), row.get('github_link_type','').strip()
    ))
    rec_id = cur.lastrowid

    course_name = row.get('course','').strip()
    project_name = row.get('project','').strip()

    course = resource_lookup.get(('course', course_name), {})
    project = resource_lookup.get(('project', project_name), {})
    if course:
        matched_resource_keys.add(('course', course_name))
    if project:
        matched_resource_keys.add(('project', project_name))

    # Every recommendation gets its own course resource record.
    conn.execute("""
        INSERT INTO resources
        (recommendation_id, resource_type, name, youtube_url, free_course_url, paid_course_url, project_url)
        VALUES (?, 'course', ?, ?, ?, ?, ?)
    """, (
        rec_id, course_name,
        (course.get('youtube_url') or row.get('youtube_url') or '').strip(),
        (course.get('free_course_url') or '').strip(),
        (course.get('paid_course_url') or '').strip(),
        (course.get('project_url') or '').strip()
    ))

    # Every recommendation gets its own project resource record.
    conn.execute("""
        INSERT INTO resources
        (recommendation_id, resource_type, name, youtube_url, free_course_url, paid_course_url, project_url)
        VALUES (?, 'project', ?, ?, '', '', ?)
    """, (
        rec_id, project_name,
        (project.get('youtube_url') or '').strip(),
        (project.get('project_url') or row.get('github_url') or '').strip()
    ))

# Keep resource entries that do not belong to any current recommendation (e.g. Data Preprocessing/Library Management).
for r in resource_rows:
    resource_type = r.get('type','').strip()
    name = r.get('name','').strip()
    key = (resource_type, name)
    if resource_type not in ('course', 'project') or not name or key in matched_resource_keys:
        continue
    conn.execute("""
        INSERT INTO resources
        (recommendation_id, resource_type, name, youtube_url, free_course_url, paid_course_url, project_url)
        VALUES (NULL, ?, ?, ?, ?, ?, ?)
    """, (
        resource_type, name,
        (r.get('youtube_url') or '').strip(),
        (r.get('free_course_url') or '').strip(),
        (r.get('paid_course_url') or '').strip(),
        (r.get('project_url') or '').strip()
    ))

conn.commit()
print(f"Imported {len(recommendations)} recommendations and {len(recommendations)*2} linked resource records.")
print(f"Database: {DB_PATH}")
conn.close()
