import sqlite3

DB_PATH = 'reports.db'  # Use the root database file

conn = sqlite3.connect(DB_PATH)
cursor = conn.cursor()

cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
tables = cursor.fetchall()

print('Tables in database:')
for table in tables:
    print(table[0])

conn.close() 