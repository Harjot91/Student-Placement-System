from flask import Flask, render_template, request, session, redirect, send_from_directory
import mysql.connector
import os
from werkzeug.utils import secure_filename
app = Flask(__name__)
app.secret_key = "secret123"
UPLOAD_FOLDER = "uploads"
app.config["UPLOAD_FOLDER"] = UPLOAD_FOLDER
if not os.path.exists(UPLOAD_FOLDER):
    os.makedirs(UPLOAD_FOLDER)
# DATABASE
def get_db():
    return mysql.connector.connect(
        host="localhost",
        user="root",
        password="H@rde0l/",
        database="placement_db"
    )
# INIT DB
def init_db():
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS students (
        id INT AUTO_INCREMENT PRIMARY KEY,
        name VARCHAR(100),
        email VARCHAR(100) UNIQUE,
        branch VARCHAR(50),
        cgpa VARCHAR(10),
        password VARCHAR(100),
        resume VARCHAR(255)
    )
    """)
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS companies (
        id INT AUTO_INCREMENT PRIMARY KEY,
        name VARCHAR(100),
        role VARCHAR(100),
        package VARCHAR(50)
    )
    """)
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS applications (
        id INT AUTO_INCREMENT PRIMARY KEY,
        student_email VARCHAR(100),
        company_id INT,
        status VARCHAR(20) DEFAULT 'pending'
    )
    """)
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS placement_calendar (
        id INT AUTO_INCREMENT PRIMARY KEY,
        company_name VARCHAR(100),
        drive_date DATE,
        venue VARCHAR(100)
    )
    """)
    conn.commit()
    conn.close()
init_db()
# Admin credentials (change before production)
ADMIN_USER = "admin"
ADMIN_PASS = "admin123"
# --- Admin Panel Routes ---
@app.route("/admin_login", methods=["GET", "POST"])
def admin_login():
    if request.method == "POST":
        username = (request.form.get("username") or "").strip()
        password = (request.form.get("password") or "").strip()
        if username == ADMIN_USER and password == ADMIN_PASS:
            session["admin"] = True
            session["admin_user"] = username
            return redirect("/admin_dashboard")
        return "❌ Invalid admin credentials"
    return render_template("admin_login.html")
@app.route("/admin_dashboard")
def admin_dashboard():
    if not session.get("admin"):
        return redirect("/admin_login")
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute("SELECT COUNT(*) FROM students")
    students_count = cursor.fetchone()[0]
    cursor.execute("SELECT COUNT(*) FROM companies")
    companies_count = cursor.fetchone()[0]
    cursor.execute("SELECT COUNT(*) FROM applications")
    apps_count = cursor.fetchone()[0]
    conn.close()
    return render_template("admin_dashboard.html", students_count=students_count, companies_count=companies_count, apps_count=apps_count)

@app.route("/admin/calendar")
def admin_calendar():
    if not session.get("admin"):
        return redirect("/admin_login")
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute("""
        SELECT id, company_name, drive_date, venue
        FROM placement_calendar
        ORDER BY drive_date ASC
    """)
    events = cursor.fetchall()
    conn.close()
    return render_template("admin_calendar.html", events=events)
@app.route("/admin/calendar/add", methods=["GET", "POST"])
def admin_add_calendar_event():
    if not session.get("admin"):
        return redirect("/admin_login")
    if request.method == "POST":
        company_name = (request.form.get("company_name") or "").strip()
        drive_date = (request.form.get("drive_date") or "").strip()
        venue = (request.form.get("venue") or "").strip()
        if company_name and drive_date and venue:
            conn = get_db()
            cursor = conn.cursor()
            cursor.execute(
                "INSERT INTO placement_calendar (company_name, drive_date, venue) VALUES (%s, %s, %s)",
                (company_name, drive_date, venue)
            )
            conn.commit()
            conn.close()
        return redirect("/admin/calendar")
    return render_template("admin_calendar.html")
@app.route("/admin/calendar/edit/<int:event_id>", methods=["GET", "POST"])
def admin_edit_calendar_event(event_id):
    if not session.get("admin"):
        return redirect("/admin_login")
    conn = get_db()
    cursor = conn.cursor()
    if request.method == "POST":
        company_name = (request.form.get("company_name") or "").strip()
        drive_date = (request.form.get("drive_date") or "").strip()
        venue = (request.form.get("venue") or "").strip()
        if company_name and drive_date and venue:
            cursor.execute(
                "UPDATE placement_calendar SET company_name=%s, drive_date=%s, venue=%s WHERE id=%s",
                (company_name, drive_date, venue, event_id)
            )
            conn.commit()
        conn.close()
        return redirect("/admin/calendar")
    cursor.execute(
        "SELECT id, company_name, drive_date, venue FROM placement_calendar WHERE id=%s",
        (event_id,)
    )
    event = cursor.fetchone()
    conn.close()
    return render_template("admin_calendar.html", event=event)
@app.route("/admin/calendar/delete/<int:event_id>")
def admin_delete_calendar_event(event_id):
    if not session.get("admin"):
        return redirect("/admin_login")
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute("DELETE FROM placement_calendar WHERE id=%s", (event_id,))
    conn.commit()
    conn.close()
    return redirect("/admin/calendar")
# HOME
@app.route("/")
def home():
    return render_template("index.html")
# REGISTER
@app.route("/register", methods=["GET", "POST"])
def register():
    if request.method == "POST":
        conn = get_db()
        cursor = conn.cursor()
        cursor.execute("""
        INSERT INTO students (name,email,branch,cgpa,password)
        VALUES (%s,%s,%s,%s,%s)
        """, (
            request.form["name"],
            request.form["email"],
            request.form["branch"],
            request.form["cgpa"],
            request.form["password"]
        ))
        conn.commit()
        conn.close()
        return redirect("/login")
    return render_template("register.html")
# LOGIN
@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        conn = get_db()
        cursor = conn.cursor()
        cursor.execute("""
        SELECT email FROM students
        WHERE email=%s AND password=%s
        """, (request.form["email"], request.form["password"]))
        user = cursor.fetchone()
        conn.close()
        if user:
            session["user"] = user[0]
            return redirect("/dashboard")
        return "❌ Invalid Login"
    return render_template("login.html")
# DASHBOARD
@app.route("/dashboard")
def dashboard():
    if "user" not in session:
        return redirect("/login")
    return render_template("dashboard.html")
# COMPANIES
@app.route("/companies")
def companies():
    if "user" not in session:
        return redirect("/login")
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM companies")
    companies = cursor.fetchall()
    conn.close()
    return render_template("companies.html", companies=companies)
# Admin: manage companies
@app.route("/admin/companies")
def admin_companies():
    if not session.get("admin"):
        return redirect("/admin_login")
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM companies")
    companies = cursor.fetchall()
    conn.close()
    return render_template("admin_companies.html", companies=companies)
@app.route("/admin/companies/add", methods=["GET", "POST"])
def admin_add_company():
    if not session.get("admin"):
        return redirect("/admin_login")
    if request.method == "POST":
        conn = get_db()
        cursor = conn.cursor()
        cursor.execute(
            "INSERT INTO companies (name, role, package) VALUES (%s,%s,%s)",
            (request.form.get("name"), request.form.get("role"), request.form.get("package"))
        )
        conn.commit()
        conn.close()
        return redirect("/admin/companies")
    return render_template("add_company.html")
@app.route("/admin/companies/edit/<int:id>", methods=["GET", "POST"])
def admin_edit_company(id):
    if not session.get("admin"):
        return redirect("/admin_login")
    conn = get_db()
    cursor = conn.cursor()
    if request.method == "POST":
        cursor.execute(
            "UPDATE companies SET name=%s, role=%s, package=%s WHERE id=%s",
            (request.form.get("name"), request.form.get("role"), request.form.get("package"), id)
        )
        conn.commit()
        conn.close()
        return redirect("/admin/companies")
    cursor.execute("SELECT name, role, package FROM companies WHERE id=%s", (id,))
    company = cursor.fetchone()
    conn.close()
    return render_template("add_company.html", company=company)
@app.route("/admin/companies/delete/<int:id>")
def admin_delete_company(id):
    if not session.get("admin"):
        return redirect("/admin_login")
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute("DELETE FROM companies WHERE id=%s", (id,))
    conn.commit()
    conn.close()
    return redirect("/admin/companies")
@app.route("/admin/applications")
def admin_applications():
    if not session.get("admin"):
        return redirect("/admin_login")
    try:
        conn = get_db()
        cursor = conn.cursor()
        cursor.execute(
            """
            SELECT a.id, a.student_email, c.name, c.role, a.status, s.resume
            FROM applications a
            LEFT JOIN companies c ON a.company_id = c.id
            LEFT JOIN students s ON a.student_email = s.email
            ORDER BY a.id DESC
            """
        )
        applications = cursor.fetchall()
        conn.close()
        return render_template("admin_applications.html", applications=applications)
    except Exception as e:
        return f"❌ Error loading applications: {str(e)}"
@app.route("/admin/applications/delete/<int:id>")
def admin_delete_application(id):
    if not session.get("admin"):
        return redirect("/admin_login")
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute("DELETE FROM applications WHERE id=%s", (id,))
    conn.commit()
    conn.close()
    return redirect("/admin/applications")
# APPLY
@app.route("/apply/<int:company_id>")
def apply(company_id):
    if "user" not in session:
        return redirect("/login")
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute("""
    SELECT id FROM applications
    WHERE student_email=%s AND company_id=%s
    """, (session["user"], company_id))
    if cursor.fetchone():
        conn.close()
        return "❌ Already Applied"
    cursor.execute("""
    INSERT INTO applications (student_email, company_id, status)
    VALUES (%s,%s,'pending')
    """, (session["user"], company_id))
    conn.commit()
    conn.close()
    return redirect("/my_applications")
# MY APPLICATIONS
@app.route("/my_applications")
def my_applications():
    if "user" not in session:
        return redirect("/login")
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute("""
        SELECT 
            c.name,
            c.role,
            c.package,
            a.status
        FROM applications a
        JOIN companies c ON a.company_id = c.id
        WHERE a.student_email = %s
    """, (session["user"],))
    applications = cursor.fetchall()
    conn.close()
    return render_template("my_applications.html", applications=applications)
# PROFILE
@app.route("/profile")
def profile():
    if "user" not in session:
        return redirect("/login")
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute("""
    SELECT name,email,branch,cgpa,resume
    FROM students
    WHERE email=%s
    """, (session["user"],))
    student = cursor.fetchone()
    conn.close()
    return render_template("profile.html", student=student)
# VIEW RESUME
@app.route("/resume/<filename>")
def view_resume(filename):
    if "user" not in session and not session.get("admin"):
        return redirect("/login")
    return send_from_directory(app.config["UPLOAD_FOLDER"], filename, as_attachment=False)
@app.route("/admin/view_resume/<int:application_id>")
def admin_view_resume(application_id):
    if not session.get("admin"):
        return redirect("/admin_login")
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute(
        """
        SELECT s.resume
        FROM applications a
        JOIN students s ON a.student_email = s.email
        WHERE a.id = %s
        """,
        (application_id,)
    )
    result = cursor.fetchone()
    conn.close()
    if not result or not result[0]:
        return "❌ No resume uploaded"
    return send_from_directory(
        app.config["UPLOAD_FOLDER"],
        result[0],
        as_attachment=False
    )
# EDIT PROFILE
@app.route("/edit_profile", methods=["GET", "POST"])
def edit_profile():
    if "user" not in session:
        return redirect("/login")
    conn = get_db()
    cursor = conn.cursor()
    if request.method == "POST":
        cursor.execute("""
        UPDATE students
        SET name=%s, branch=%s, cgpa=%s
        WHERE email=%s
        """, (
            request.form["name"],
            request.form["branch"],
            request.form["cgpa"],
            session["user"]
        ))
        conn.commit()
        conn.close()
        return redirect("/profile")
    cursor.execute("""
    SELECT name, branch, cgpa
    FROM students
    WHERE email=%s
    """, (session["user"],))
    student = cursor.fetchone()
    conn.close()
    return render_template("edit_profile.html", student=student)
# RESUME UPLOAD
@app.route("/update_resume", methods=["GET", "POST"])
def update_resume():
    if "user" not in session:
        return redirect("/login")
    if request.method == "POST":
        file = request.files["resume"]
        if file.filename != "":
            filename = secure_filename(file.filename)
            file.save(os.path.join(app.config["UPLOAD_FOLDER"], filename))
            conn = get_db()
            cursor = conn.cursor()
            cursor.execute("""
            UPDATE students
            SET resume=%s
            WHERE email=%s
            """, (filename, session["user"]))
            conn.commit()
            conn.close()
            return redirect("/profile")
    return render_template("update_resume.html")
# CALENDAR
@app.route("/calendar")
def calendar():
    if "user" not in session:
        return redirect("/login")
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute("""
    SELECT company_name, drive_date, venue
    FROM placement_calendar
    ORDER BY drive_date
    """)
    events = cursor.fetchall()
    conn.close()
    return render_template("calendar.html", events=events)
# UPDATE STATUS
@app.route("/update_status/<int:app_id>/<status>")
def update_status(app_id, status):
    if not session.get("admin"):
        return redirect("/admin_login")
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute("""
    UPDATE applications
    SET status=%s
    WHERE id=%s
    """, (status, app_id))
    conn.commit()
    conn.close()
    return redirect("/admin/applications")
@app.route("/admin/update_status/<int:app_id>/<status>", methods=["GET", "POST"])
def admin_update_status(app_id, status):
    if not session.get("admin"):
        return redirect("/admin_login")
    try:
        allowed = {"accepted", "rejected", "pending", "selected"}
        status = status.lower()
        if status not in allowed:
            return f"❌ Invalid status: {status}"
        conn = get_db()
        cursor = conn.cursor()
        cursor.execute("SELECT id FROM applications WHERE id=%s", (app_id,))
        if not cursor.fetchone():
            conn.close()
            return f"❌ Application ID {app_id} not found"
        cursor.execute("""
        UPDATE applications
        SET status=%s
        WHERE id=%s
        """, (status, app_id))
        conn.commit()
        rows_affected = cursor.rowcount
        conn.close()
        if rows_affected > 0:
            return redirect("/admin/applications")
        else:
            return f"❌ Failed to update application {app_id}"
    except Exception as e:
        return f"❌ Error: {str(e)}"
# DEBUG: Check database state
@app.route("/admin/debug")
def admin_debug():
    if not session.get("admin"):
        return redirect("/admin_login")
    try:
        conn = get_db()
        cursor = conn.cursor()
        # Check students
        cursor.execute("SELECT COUNT(*) FROM students")
        students_count = cursor.fetchone()[0]
        # Check companies
        cursor.execute("SELECT COUNT(*) FROM companies")
        companies_count = cursor.fetchone()[0]
        # Check applications
        cursor.execute("SELECT COUNT(*) FROM applications")
        applications_count = cursor.fetchone()[0]
        # Get all applications with company details
        cursor.execute("""
            SELECT a.id, a.student_email, a.company_id, a.status, c.name
            FROM applications a
            LEFT JOIN companies c ON a.company_id = c.id
        """)
        applications = cursor.fetchall()
        conn.close()
        debug_info = f"""
        <h1>Debug Info</h1>
        <p>Students: {students_count}</p>
        <p>Companies: {companies_count}</p>
        <p>Applications: {applications_count}</p>
        <h2>All Applications:</h2>
        <table border="1">
            <tr><th>ID</th><th>Email</th><th>Company ID</th><th>Status</th><th>Company Name</th></tr>
        """
        for app in applications:
            debug_info += f"<tr><td>{app[0]}</td><td>{app[1]}</td><td>{app[2]}</td><td>{app[3]}</td><td>{app[4]}</td></tr>"
        debug_info += "</table><a href='/admin/applications'>Back</a>"
        return debug_info
    except Exception as e:
        return f"❌ Debug Error: {str(e)}"
# LOGOUT
@app.route("/logout")
def logout():
    session.clear()
    return redirect("/")
# RUN
if __name__ == "__main__":
    app.run(debug=True)