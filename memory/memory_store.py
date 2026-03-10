import sqlite3
import json

DB_PATH = "memory.db"

conn   = sqlite3.connect(DB_PATH, check_same_thread=False)
cursor = conn.cursor()

# ── Create table if it doesn't exist (full schema) ──
cursor.execute("""
CREATE TABLE IF NOT EXISTS history(
    id             INTEGER PRIMARY KEY AUTOINCREMENT,
    input_type     TEXT,
    question       TEXT,
    parsed         TEXT,
    context        TEXT,
    solution       TEXT,
    verifier_conf  REAL,
    feedback       TEXT,
    timestamp      DATETIME DEFAULT CURRENT_TIMESTAMP
)
""")
conn.commit()

# ── Migrate old DB: add missing columns if they don't exist ──
existing_cols = {row[1] for row in cursor.execute("PRAGMA table_info(history)")}

migrations = {
    "id":            "ALTER TABLE history ADD COLUMN id INTEGER",
    "input_type":    "ALTER TABLE history ADD COLUMN input_type TEXT DEFAULT 'text'",
    "parsed":        "ALTER TABLE history ADD COLUMN parsed TEXT DEFAULT '{}'",
    "context":       "ALTER TABLE history ADD COLUMN context TEXT DEFAULT '[]'",
    "verifier_conf": "ALTER TABLE history ADD COLUMN verifier_conf REAL DEFAULT 0.5",
    "timestamp":     "ALTER TABLE history ADD COLUMN timestamp TEXT DEFAULT ''",
}

for col, sql in migrations.items():
    if col not in existing_cols:
        try:
            cursor.execute(sql)
            conn.commit()
        except Exception:
            pass   # ignore if already exists or unsupported


def store_solution(question, solution, feedback="",
                   input_type="text", parsed=None,
                   context=None, verifier_conf=0.5):
    """Store a full interaction record."""
    cursor.execute(
        """INSERT INTO history
           (input_type, question, parsed, context, solution, verifier_conf, feedback)
           VALUES (?, ?, ?, ?, ?, ?, ?)""",
        (
            input_type,
            question,
            json.dumps(parsed  or {}),
            json.dumps(context or []),
            solution,
            verifier_conf,
            feedback,
        )
    )
    conn.commit()


def get_similar_problem(question: str):
    """
    Returns (solution, context_list) for the most similar stored problem,
    or (None, []) if nothing matches.
    """
    try:
        cursor.execute("SELECT question, solution, context FROM history ORDER BY rowid DESC")
    except Exception:
        return None, []

    rows = cursor.fetchall()
    q_lower = question.lower()

    # Pass 1: substring match
    for q, s, ctx in rows:
        if q_lower in (q or "").lower() or (q or "").lower() in q_lower:
            try:
                return s, json.loads(ctx or "[]")
            except Exception:
                return s, []

    # Pass 2: keyword overlap (≥ 3 words in common)
    q_words = {w for w in q_lower.split() if len(w) > 3}
    for q, s, ctx in rows:
        row_words = {w for w in (q or "").lower().split() if len(w) > 3}
        if len(q_words & row_words) >= 3:
            try:
                return s, json.loads(ctx or "[]")
            except Exception:
                return s, []

    return None, []


def get_recent_history(limit=10):
    """Return the last N records for sidebar display."""
    try:
        # Use COALESCE so timestamp works even if column was added mid-life
        cursor.execute(
            """SELECT question, solution, verifier_conf, feedback,
                      COALESCE(timestamp, '') as timestamp
               FROM history ORDER BY rowid DESC LIMIT ?""",
            (limit,)
        )
    except Exception:
        return []

    rows = cursor.fetchall()
    return [
        {
            "question":   r[0],
            "solution":   r[1],
            "confidence": r[2] if r[2] is not None else 0.5,
            "feedback":   r[3],
            "timestamp":  r[4],
        }
        for r in rows
    ]