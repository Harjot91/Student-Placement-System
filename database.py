import sqlite3

conn = sqlite3.connect('placement.db')
cursor = conn.cursor()

# Students Table
cursor.execute('''
CREATE TABLE IF NOT EXISTS students (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT NOT NULL,
    email TEXT NOT NULL,
    branch TEXT NOT NULL,
    cgpa REAL NOT NULL,
    password TEXT NOT NULL
)
''')

# Companies Table
cursor.execute('''
CREATE TABLE IF NOT EXISTS companies (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    company_name TEXT NOT NULL,
    package REAL NOT NULL,
    eligibility REAL NOT NULL
)
''')

cursor.execute('''
CREATE TABLE IF NOT EXISTS applications (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    student_email TEXT NOT NULL,
    company_name TEXT NOT NULL
)
''')

conn.commit()
conn.close()

print("Database created successfully!")