import sqlite3
from datetime import datetime

DB_PATH = "bookings.db"

def get_connection():
    return sqlite3.connect(DB_PATH, check_same_thread=False)

def init_db():
    conn = get_connection()
    cur = conn.cursor()

    cur.execute("""
    CREATE TABLE IF NOT EXISTS bookings (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT,
        email TEXT,
        phone TEXT,
        booking_type TEXT,
        date TEXT,
        time TEXT,
        status TEXT,
        created_at TEXT
    )
    """)

    conn.commit()
    conn.close()

def save_booking(data: dict):
    conn = get_connection()
    cur = conn.cursor()

    cur.execute(
        """
        INSERT INTO bookings
        (name, email, phone, booking_type, date, time, status, created_at)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        """,
        (
            data["name"],
            data["email"],
            data["phone"],
            data["booking_type"],
            data["date"],
            data["time"],
            "CONFIRMED",
            datetime.utcnow().isoformat()
        )
    )

    booking_id = cur.lastrowid
    conn.commit()
    conn.close()
    return booking_id

def get_all_bookings():
    conn = get_connection()
    cur = conn.cursor()

    cur.execute("""
        SELECT
            id,
            name,
            email,
            phone,
            booking_type,
            date,
            time,
            status,
            created_at
        FROM bookings
        ORDER BY created_at DESC
    """)

    rows = cur.fetchall()
    conn.close()
    return rows
