from flask import Flask, render_template, session, request, redirect, url_for
import sqlite3
app = Flask(__name__)



def init_db():
    
    connection = sqlite3.connect("database.db")
    cursor = connection.cursor()
    
    cursor.execute("PRAGMA foreign_keys = ON;")

    cursor.execute("""
    CREATE TABLE IF NOT EXISTS users (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        email TEXT NOT NULL UNIQUE,
        passwordHash TEXT NOT NULL,
        role INTEGER NOT NULL
    )
    """)
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS userInfoCache (
    email TEXT NOT NULL UNIQUE CHECK (email like '%@%.%'),
    age INTEGER NOT NULL,
    approxSalary INTEGER NOT NULL,
    existMedCondition INTEGER NOT NULL,
    cacheCreatedAt TIMESTAMP NOT NULL,
    FOREIGN KEY (email) REFERENCES users(email)
    )
    """)
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS firms (
    name TEXT PRIMARY KEY NOT NULL,
    baseRate REAL NOT NULL,
    ageRate REAL NOT NULL,
    salaryRate REAL NOT NULL,
    existMedCondRate REAL NOT NULL,
    travelDurationRate REAL NOT NULL
    )
    """)
    connection.commit()
    connection.close()


init_db()
@app.route("/")
def login():
    return render_template("login.html", methods=["GET","POST"])

@app.route("/register", methods=["GET", "POST"])
def register():
    error = None
    if request.method == "POST":
        conn = sqlite3.connect("database.db")
        c = conn.cursor()
        email = request.form["email"]
        password = request.form["password"]
        try:
            c.execute("INSERT INTO users (email, passwordHash, role) VALUES (?, ?, ?)", (email, password, 1))
            conn.commit()
            conn.close()
            return redirect(url_for("login"))
        except sqlite3.IntegrityError:
            error = "bro hop off"
            conn.close()
    return render_template("register.html", error=error)

@app.route("/about")
def about():
    return render_template("about.html")
    
@app.route("/mainThing", methods=["GET","POST"])
def mainThing():
    if request.method == "POST":
        return render_template("mainThing.html")

@app.route("/resultsPage", methods=["GET", "POST"])
def resultsPage():
    conn = sqlite3.connect("database.db")
    c = conn.cursor()
    if request.method == "POST":
        name = request.form["name"]
        c.execute("INSERT INTO userInfoCache (name, ) VALUES (?,)", (name, ))
    return render_template("resultsPage.html")



if __name__ == "__main__":
    app.run(debug=True)