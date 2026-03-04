import sqlite3

conn = sqlite3.connect("database.db")
c = conn.cursor()

c.execute(
    "INSERT INTO users (email, passwordHash) VALUES (?, ?)",
    ("admin@example.com", "adminExamplePass12345")
)

c.execute(
    "INSERT INTO firms (name, baseRate, ageRate, salaryRate, existMedCondRate, travelDurationRate, peopleTravelRate, coverage) VALUES (?, ?, ?, ?, ?, ?, ?)",
    ("exampleFirmOne", 150, 1.5 , 0.05, 300, 0.02, 15, "1001")
)

conn.commit()
conn.close()


#     name TEXT PRIMARY KEY NOT NULL,
    # baseRate REAL NOT NULL,
    # ageRate REAL NOT NULL,
    # salaryRate REAL NOT NULL,
    # existMedCondRate REAL NOT NULL,
    # travelDurationRate REAL NOT NULL,
    # coverage = TEXT NOT NULL 
