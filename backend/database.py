import sqlite3
import os

DB_FILE = os.path.join(os.path.dirname(os.path.abspath(__file__)), "database.db")

def get_db_connection():
    """Establish a connection to the SQLite database."""
    conn = sqlite3.connect(DB_FILE)
    conn.row_factory = sqlite3.Row  # Access columns by name
    return conn

def init_db():
    """Initialize the database tables if they do not exist."""
    conn = get_db_connection()
    cursor = conn.cursor()

    # Table for predicted emissions
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS predicted_emissions (
        building_id TEXT,
        timestamp TEXT,
        emission REAL,
        scaled_emission REAL,
        PRIMARY KEY (building_id, timestamp)
    )
    """)

    # Table for carbon emission safety alerts
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS peak_alerts (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        building_id TEXT,
        timestamp TEXT,
        emission REAL,
        limit_value REAL,
        alert_msg TEXT,
        severity TEXT,
        resolved INTEGER DEFAULT 0,
        UNIQUE(building_id, timestamp)
    )
    """)

    # Table to cache AI insights from Gemini
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS cached_insights (
        date_key TEXT PRIMARY KEY,
        insights_json TEXT
    )
    """)

    conn.commit()
    conn.close()

if __name__ == "__main__":
    init_db()
    print("Database initialized successfully at:", DB_FILE)
