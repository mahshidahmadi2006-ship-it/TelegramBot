import sqlite3

conn = sqlite3.connect("users.db", check_same_thread=False)
cursor = conn.cursor()

cursor.execute("""
CREATE TABLE IF NOT EXISTS history (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id INTEGER,
    role TEXT,
    message TEXT
)
""")

conn.commit()


def save_message(user_id, role, message):
    cursor.execute(
        "INSERT INTO history(user_id, role, message) VALUES (?, ?, ?)",
        (user_id, role, message),
    )
    conn.commit()


def get_history(user_id):
    cursor.execute(
        "SELECT role, message FROM history WHERE user_id=? ORDER BY id",
        (user_id,),
    )
    return cursor.fetchall()


def clear_history(user_id):
    cursor.execute(
        "DELETE FROM history WHERE user_id=?",
        (user_id,),
    )
    conn.commit()