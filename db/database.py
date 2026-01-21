import sqlite3
from datetime import datetime

DB = "bookings.db"

def get_db():
    return sqlite3.connect(DB, check_same_thread=False)

def init_db():
    conn = get_db()
    cur = conn.cursor()

    cur.execute("""
    CREATE TABLE IF NOT EXISTS customers (
        customer_id INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT,
        email TEXT,
        phone TEXT
    )
    """)

    cur.execute("""
    CREATE TABLE IF NOT EXISTS bookings (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        customer_id INTEGER,
        booking_type TEXT,
        date TEXT,
        time TEXT,
        status TEXT,
        created_at TEXT
    )
    """)

    conn.commit()
    conn.close()

def save_booking(data):
    conn = get_db()
    cur = conn.cursor()

    cur.execute(
        "INSERT INTO customers (name,email,phone) VALUES (?,?,?)",
        (data["name"], data["email"], data["phone"])
    )
    cid = cur.lastrowid

    cur.execute(
        """
        INSERT INTO bookings
        (customer_id, booking_type, date, time, status, created_at)
        VALUES (?,?,?,?,?,?)
        """,
        (cid, data["booking_type"], data["date"], data["time"],
         "CONFIRMED", datetime.utcnow().isoformat())
    )

    bid = cur.lastrowid
    conn.commit()
    conn.close()
    return bid

def get_all_bookings():
    conn = get_db()
    cur = conn.cursor()
    cur.execute("""
    SELECT b.id,c.name,c.email,c.phone,
           b.booking_type,b.date,b.time,
           b.status,b.created_at
    FROM bookings b
    JOIN customers c ON b.customer_id=c.customer_id
    ORDER BY b.created_at DESC
    """)
    rows = cur.fetchall()
    conn.close()
    return rows
