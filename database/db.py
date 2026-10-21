import sqlite3

conn = sqlite3.connect("database.db")
cursor = conn.cursor()

def create_tables():
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS users (
        user_id INTEGER PRIMARY KEY,
        reminder_time TEXT DEFAULT '22:00'
    )
    """)

    cursor.execute("""
    CREATE TABLE IF NOT EXISTS habits (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        user_id INTEGER,
        habit_name TEXT,
        total_days INTEGER,
        start_date TEXT,
        end_date TEXT,
        success_days INTEGER DEFAULT 0,
        failed_days INTEGER DEFAULT 0,
        status TEXT DEFAULT 'active',
        last_check_date TEXT
    )
    """)

    cursor.execute("""
    CREATE TABLE IF NOT EXISTS habit_logs (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        habit_id INTEGER,
        check_date TEXT,
        status TEXT
    )
    """)

    cursor.execute("""
    CREATE TABLE IF NOT EXISTS goals (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        user_id INTEGER,
        goal_name TEXT,
        total_days INTEGER,
        start_date TEXT,
        success_days INTEGER DEFAULT 0,
        failed_days INTEGER DEFAULT 0,
        last_check_date TEXT
    )
    """)

    cursor.execute("""
    CREATE TABLE IF NOT EXISTS notifications (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        user_id INTEGER,
        morning_time TEXT DEFAULT '08:00',
        evening_time TEXT DEFAULT '22:00'
    )
    """)

    conn.commit()