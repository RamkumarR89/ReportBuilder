import sqlite3

DB_PATH = 'app/reports.db'

conn = sqlite3.connect(DB_PATH)
cursor = conn.cursor()

try:
    cursor.execute("ALTER TABLE settings ADD COLUMN db_name TEXT;")
    print("db_name column added successfully.")
except Exception as e:
    print(f"Error: {e}")

conn.commit()
conn.close() 