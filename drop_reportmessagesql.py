import sqlite3
conn = sqlite3.connect('reports.db')
conn.execute('DROP TABLE IF EXISTS ReportMessageSQL;')
conn.commit()
conn.close()
print("Dropped ReportMessageSQL table.") 