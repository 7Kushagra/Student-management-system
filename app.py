from flask import Flask, render_template, request, redirect, url_for, session
import mysql.connector

app = Flask(__name__)
app.secret_key = "supersecretkey"   # will improve later

# ---------------- DATABASE CONNECTION ----------------
db = mysql.connector.connect(
    host="localhost",
    user="flaskuser",
    password="flask123",
    database="studentdb"
)
cursor = db.cursor()

# ---------------- LOGIN ----------------
@app.route("/", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        username = request.form["username"]
        password = request.form["password"]

        cursor.execute(
            "SELECT * FROM admin WHERE username=%s AND password=%s",
            (username, password)
        )
        admin = cursor.fetchone()

        if admin:
            session["user"] = username
            return redirect(url_for("dashboard"))
        else:
            return render_template("login.html", error="Invalid credentials")

    return render_template("login.html")


# ---------------- DASHBOARD ----------------
@app.route("/dashboard")
def dashboard():
    if "user" not in session:
        return redirect("/")

    cursor.execute("SELECT COUNT(*) FROM students")
    total_students = cursor.fetchone()[0]

    return render_template(
        "dashboard.html",
        total_students=total_students
    )


# ---------------- LOGOUT ----------------
@app.route("/logout")
def logout():
    session.clear()
    return redirect("/")


# ---------------- VIEW STUDENTS ----------------
@app.route("/students")
def students():
    if "user" not in session:
        return redirect("/")

    cursor.execute("SELECT * FROM students")
    students = cursor.fetchall()

    return render_template("view_students.html", students=students)


# ---------------- ADD STUDENT ----------------
@app.route("/add", methods=["GET", "POST"])
def add_student():
    if "user" not in session:
        return redirect("/")

    if request.method == "POST":
        name = request.form["name"]
        email = request.form["email"]
        course = request.form["course"]

        cursor.execute(
            "INSERT INTO students (name, email, course) VALUES (%s, %s, %s)",
            (name, email, course)
        )
        db.commit()
        return redirect("/students")

    return render_template("add_student.html")


# ---------------- EDIT STUDENT ----------------
@app.route("/edit/<int:id>", methods=["GET", "POST"])
def edit_student(id):
    if "user" not in session:
        return redirect("/")

    if request.method == "POST":
        name = request.form["name"]
        email = request.form["email"]
        course = request.form["course"]

        cursor.execute(
            "UPDATE students SET name=%s, email=%s, course=%s WHERE id=%s",
            (name, email, course, id)
        )
        db.commit()
        return redirect("/students")

    cursor.execute("SELECT * FROM students WHERE id=%s", (id,))
    student = cursor.fetchone()

    return render_template("edit.html", student=student)


# ---------------- DELETE STUDENT ----------------
@app.route("/delete/<int:id>")
def delete_student(id):
    if "user" not in session:
        return redirect("/")

    cursor.execute("DELETE FROM students WHERE id=%s", (id,))
    db.commit()
    return redirect("/students")


# ---------------- SEARCH STUDENT ----------------
@app.route("/search", methods=["GET", "POST"])
def search():
    if "user" not in session:
        return redirect("/")

    students = []

    if request.method == "POST":
        keyword = request.form["keyword"]
        cursor.execute(
            "SELECT * FROM students WHERE name LIKE %s OR email LIKE %s",
            (f"%{keyword}%", f"%{keyword}%")
        )
        students = cursor.fetchall()

    return render_template("search.html", students=students)


# ---------------- RUN APP ----------------
if __name__ == "__main__":
    app.run(debug=True)
