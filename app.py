from flask import Flask, render_template, session, request, redirect, url_for
import sqlite3
app = Flask(__name__)



def init_db(): #defining init_db() to initialize the database
    
    connection = sqlite3.connect("database.db") #Connection object from sqlite3.connect("...") is linked to variable connection. .connect() accesses the database.db or creates it if it doesn't exist.
    cursor = connection.cursor() #Cursor object, attached to variable cursor is created to run SQL commands.
    
    cursor.execute("PRAGMA foreign_keys = ON;") #letting foreign keys exist using cursor objects

#Creating tables with cursor object
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS users (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        email TEXT NOT NULL UNIQUE CHECK (email LIKE '%@%.%'),
        passwordHash TEXT NOT NULL
    )
    """)
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS userInfoCache (
    email TEXT NOT NULL UNIQUE CHECK (email LIKE '%@%.%'),
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
    #Close connection objects
    connection.commit()
    connection.close() 
    
#Running database initializatoin
init_db() 
# Using flask. routes the homepage / to login, using the methods GET and POST.
# GET indicate the user is visiting the page, thus things are required to be gotten, while POST indicate the user submits a form.
@app.route("/", methods=["GET","POST"])
def login():
    error = None 

    if request.method == "POST":
        connection = sqlite3.connect("database.db")
        cursor = connection.cursor()


        email = request.form["email"]
        password = request.form["password"]

        cursor.execute("SELECT passwordHash FROM users WHERE email = ?", (email,))
        user = cursor.fetchone()
        connection.close()

        if user:
            realPassword = user[0] #fuckin tuples bruh
            if realPassword == password:
                return redirect(url_for("mainThing"))
            else:
                error = "bro think he slick skull emoji you are NOT miwa kasumi from jjk"
        else:
            error = "bro does not exist wilted_rose emoji"

    return render_template("login.html", error = error)

@app.route("/register", methods=["GET", "POST"])
def register():
    error = None
    if request.method == "POST":
        connection = sqlite3.connect("database.db")
        cursor = connection.cursor()
        email = request.form["email"]
        password = request.form["password"]
        try:
            cursor.execute("INSERT INTO users (email, passwordHash) VALUES (?, ?)", (email, password))
            connection.commit()
            connection.close()
            return redirect(url_for("login"))
        except sqlite3.IntegrityError as e:
            msg = str(e)
            if "UNIQUE" in msg:
                error = "bro guess who's email exists already"
            elif "CHECK" in msg:
                error = "lmao nice try bro tried to input a bad email"
            else:
                error = "lwk something went wrong lmao I have on clue waht"
            connection.close()

    return render_template("register.html", error=error)

@app.route("/about")
def about():
    return render_template("about.html")
    
@app.route("/mainThing", methods=["GET","POST"])
def mainThing():
    return render_template("mainThing.html")

@app.route("/resultsPage", methods=["GET", "POST"])
def resultsPage():
    connection = sqlite3.connect("database.db")
    cursor = conn.cursor()
    if request.method == "POST":
        name = request.form["name"]
        cursor.execute("INSERT INTO userInfoCache (name, ) VALUES (?,)", (name, ))
        connection.commit()
        connection.close()
    return render_template("resultsPage.html")



if __name__ == "__main__":
    app.run(debug=True)