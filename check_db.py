from db import get_connection

conn = get_connection()
rows = conn.execute("SELECT * FROM tasks").fetchall()
print(len(rows), "rows")
for row in rows:
    print(dict(row))
conn.close()