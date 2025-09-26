import sqlite3
import datetime

DB_NAME = "qa_oraculo_history.db"

def get_db_connection():
    conn = sqlite3.connect(DB_NAME, check_same_thread=False)
    conn.row_factory = sqlite3.Row
    return conn

def init_db():
    with get_db_connection() as conn:
        cursor = conn.cursor()
        cursor.execute("""
        CREATE TABLE IF NOT EXISTS analysis_history (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            created_at TIMESTAMP NOT NULL,
            user_story TEXT NOT NULL,
            analysis_report TEXT,
            test_plan_report TEXT
        );
        """)
        conn.commit()

def save_analysis_to_history(user_story: str, analysis_report: str, test_plan_report: str):
    with get_db_connection() as conn:
        cursor = conn.cursor()
        timestamp_iso = datetime.datetime.now().isoformat()
        cursor.execute("""
        INSERT INTO analysis_history (created_at, user_story, analysis_report, test_plan_report)
        VALUES (?, ?, ?, ?);
        """, (timestamp_iso, user_story, analysis_report, test_plan_report))
        conn.commit()

def get_all_analysis_history():
    with get_db_connection() as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT id, created_at, user_story FROM analysis_history ORDER BY created_at DESC;")
        history = cursor.fetchall()
        return history

def get_analysis_by_id(analysis_id: int):
    with get_db_connection() as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM analysis_history WHERE id = ?;", (analysis_id,))
        analysis_entry = cursor.fetchone()
        return analysis_entry