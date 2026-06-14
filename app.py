from flask import Flask, render_template, request
import sqlite3

app = Flask(__name__)

@app.route("/")
def home():
    return render_template("index.html")


@app.route("/register", methods=["GET", "POST"])
def register():

    if request.method == "POST":

        name = request.form["name"]
        email = request.form["email"]
        branch = request.form["branch"]
        cgpa = request.form["cgpa"]
        password = request.form["password"]

        conn = sqlite3.connect("placement.db")
        cursor = conn.cursor()

        cursor.execute(
            "INSERT INTO students (name,email,branch,cgpa,password) VALUES (?,?,?,?,?)",
            (name, email, branch, cgpa, password)
        )

        conn.commit()
        conn.close()

        return "Registration Successful!"

    return render_template("register.html")

@app.route("/login", methods=["GET", "POST"])
def login():

    if request.method == "POST":

        email = request.form["email"]
        password = request.form["password"]

        conn = sqlite3.connect("placement.db")
        cursor = conn.cursor()

        cursor.execute(
            "SELECT * FROM students WHERE email=? AND password=?",
            (email, password)
        )

        student = cursor.fetchone()

        conn.close()

        if student:
            return render_template("dashboard.html")
        else:
            return "Invalid Email or Password"

    return render_template("login.html")

@app.route("/admin")
def admin():

    conn = sqlite3.connect("placement.db")
    cursor = conn.cursor()

    cursor.execute("SELECT * FROM students")

    students = cursor.fetchall()

    conn.close()

    return render_template(
        "admin.html",
        students=students
    )

@app.route("/companies")
def companies():

    conn = sqlite3.connect("placement.db")
    cursor = conn.cursor()

    cursor.execute("SELECT * FROM companies")

    companies = cursor.fetchall()

    conn.close()

    return render_template(
        "companies.html",
        companies=companies
    )

@app.route("/apply/<company_name>")
def apply(company_name):

    conn = sqlite3.connect("placement.db")
    cursor = conn.cursor()

    cursor.execute(
        "INSERT INTO applications (student_email, company_name) VALUES (?, ?)",
        ("test@gmail.com", company_name)
    )

    conn.commit()
    conn.close()

    return f"Applied Successfully for {company_name}"

@app.route("/applications")
def applications():

    conn = sqlite3.connect("placement.db")
    cursor = conn.cursor()

    cursor.execute("SELECT * FROM applications")

    applications = cursor.fetchall()

    conn.close()

    return render_template(
        "applications.html",
        applications=applications
    )

if __name__ == "__main__":
    app.run(debug=True)