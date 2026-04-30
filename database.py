import sqlite3

conn = sqlite3.connect("school.db")
cursor = conn.cursor()

# Create tables (based on your ERD)
cursor.execute("""
CREATE TABLE IF NOT EXISTS students (
    student_id TEXT PRIMARY KEY,
    name TEXT
)
""")

cursor.execute("""
CREATE TABLE IF NOT EXISTS subjects (
    subject_id TEXT PRIMARY KEY,
    name TEXT
)
""")

cursor.execute("""
CREATE TABLE IF NOT EXISTS assignments (
    assignment_id TEXT PRIMARY KEY,
    subject_id TEXT,
    title TEXT
)
""")

cursor.execute("""
CREATE TABLE IF NOT EXISTS results (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    student_id TEXT,
    assignment_id TEXT,
    score REAL,
    letter TEXT
)
""")

conn.commit()
conn.close()
