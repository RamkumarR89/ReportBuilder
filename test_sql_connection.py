import pyodbc

server = 'frc-sh-int-db01.database.windows.net'
database = 'shiptech-tnt-dev'  # Correct database name
username = 'devuser'
password = 'Awst0azure_260824'

conn_str = (
    f"DRIVER={{ODBC Driver 17 for SQL Server}};"
    f"SERVER={server};"
    f"DATABASE={database};"
    f"UID={username};"
    f"PWD=***;"  # Hide password in print
    f"TrustServerCertificate=yes;"
)

print(f"Connecting to server: {server}, database: {database}, user: {username}")

conn_str_real = (
    f"DRIVER={{ODBC Driver 17 for SQL Server}};"
    f"SERVER={server};"
    f"DATABASE={database};"
    f"UID={username};"
    f"PWD={password};"
    f"TrustServerCertificate=yes;"
)

try:
    with pyodbc.connect(conn_str_real, timeout=10) as conn:
        print("Connection successful!")
except Exception as e:
    print("Connection failed:", e) 