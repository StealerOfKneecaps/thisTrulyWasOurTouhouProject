import sqlite3

conn = sqlite3.connect("database.db")
c = conn.cursor()

c.execute(
    "INSERT INTO users (email, passwordHash) VALUES (?, ?)",
    ("admin@example.com", "adminExamplePass12345")
)

conn.commit()
conn.close()