import mysql.connector

# Create connection with MySQL
conn = mysql.connector.connect(
    host="localhost",
    user="root",
    password="your_password",   # put your MySQL password
    database="placement_db"
)

cursor = conn.cursor()

# Data to insert
companies = [
    ("TCS", 4.5, 6.0),
    ("Infosys", 5.0, 6.5),
    ("Wipro", 4.2, 6.0),
    ("Accenture", 6.5, 7.0)
]

# Insert query
query = """
INSERT INTO companies (company_name, package, eligibility)
VALUES (%s, %s, %s)
"""

cursor.executemany(query, companies)

conn.commit()
conn.close()

print("Companies Added Successfully!")