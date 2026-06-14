import sqlite3

conn = sqlite3.connect("placement.db")
cursor = conn.cursor()

companies = [
    ("TCS", 4.5, 6.0),
    ("Infosys", 5.0, 6.5),
    ("Wipro", 4.2, 6.0),
    ("Accenture", 6.5, 7.0)
]

cursor.executemany(
    "INSERT INTO companies (company_name, package, eligibility) VALUES (?,?,?)",
    companies
)

conn.commit()
conn.close()

print("Companies Added Successfully!")