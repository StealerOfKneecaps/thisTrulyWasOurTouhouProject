from flask import Flask, render_template, session, request, redirect, url_for
from datetime import datetime, timedelta
from werkzeug.security import generate_password_hash, check_password_hash
import sqlite3
app = Flask(__name__)
app.secret_key = "Miwa from JJK THE GOAT"

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
    peopleTraveling INTEGER NOT NULL,
    tripDuration INTEGER NOT NULL,
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
    travelDurationRate REAL NOT NULL,
    peopleTravelRate REAL NOT NULL,
    coverage TEXT NOT NULL 
    )
    """)

    #Close connection objects
    connection.commit()
    connection.close() 
    
#Running database initializatoin
init_db() 
# Using flask. routes the homepage / to login, using the methods GET and POST.
# GET indicate the user is visiting the page, thus things are required to be gotten, while POST indicate the user submits a form.
@app.errorhandler(sqlite3.OperationalError)
def db_error(e):
    return render_template("error.html"), 500

@app.errorhandler(500)
def server_error(e):
    return render_template("error.html"), 500
    
def login_required(func):
    from functools import wraps
    @wraps(func)
    def wrapper(*args, **kwargs):
        if "id" not in session:
            return redirect(url_for("login"))
        return func(*args, **kwargs)
    return wrapper

@app.route("/", methods=["GET","POST"])
def login():
    error = None 
    if request.method == "POST":
        connection = sqlite3.connect("database.db")
        cursor = connection.cursor()


        email = request.form["email"]
        password = request.form["password"]
        


        cursor.execute("SELECT id, passwordHash FROM users WHERE email = ?", (email, ))
        user = cursor.fetchone()
        connection.close()

        if user:
            user_id=user[0]
            realPassword = user[1] #fuckin tuples bruh
            
            if check_password_hash(realPassword, password):
                session.clear()
                session["id"] = user_id
                session["email"] = email
                return redirect(url_for("mainThing"))
            else:
                error = "bro think he slick skull emoji you are NOT miwa kasumi from jjk"
        else:
            error = "bro does not exist wilted_rose emoji"

    return render_template("login.html", error = error)

@app.route("/about")
def about():
    return render_template("about.html")

@app.route("/register", methods=["GET", "POST"])
def register():
    error = None
    if request.method == "POST":
        email = request.form["email"]
        password = request.form["password"]
        password_conf = request.form["confirm_password"]
        
        if password_conf != password:
            error = "bro made a typo in the password"
            return render_template("register.html", error=error)

        connection = sqlite3.connect("database.db")
        cursor = connection.cursor()


        try:
            cursor.execute("INSERT INTO users (email, passwordHash) VALUES (?, ?)", (email, generate_password_hash(password)))
            connection.commit()
            return redirect(url_for("login"))
        except sqlite3.IntegrityError as e:
            msg = str(e)
            if "UNIQUE" in msg:
                error = "bro guess who's email exists already"
            elif "CHECK" in msg:
                error = "lmao nice try bro tried to input a bad email"
            else:
                error = "lwk something went wrong lmao I have on clue waht"
        finally:
            connection.close()

    return render_template("register.html", error=error)

@app.route("/mainThing", methods=["GET","POST"])
@login_required
def mainThing():
    connection = sqlite3.connect("database.db")
    cursor = connection.cursor()
    if request.method == "POST":
        email = session["email"]

# clear the expired cache (super duper important)
        
        exp_time = datetime.now() - timedelta(days=1) #exp_time is one day before current time
        cursor.execute("""
        DELETE FROM userInfoCache
        WHERE cacheCreatedAt < ?
        """, (exp_time,)) #delete anything created before a day earlier than today
        connection.commit()

        age = request.form["age"]
        salaryApprox = request.form["salary"]
        noPeopleTraveling = request.form["people"]
        durationTrip = request.form["duration"]
        if request.form["medical"] == "yes":
            existMed = 1
        else:
            existMed = 0

        cursor.execute("""INSERT OR REPLACE INTO userInfoCache (email, age, approxSalary, existMedCondition, peopleTraveling, tripDuration, cacheCreatedAt)
        VALUES (?, ?, ?, ?, ?, ?, ?)
        """, (session["email"], age, salaryApprox, existMed, noPeopleTraveling, durationTrip, datetime.now()))
        connection.commit()
        connection.close()
        return redirect(url_for("resultsPage"))

    cursor.execute("""
        SELECT age, approxSalary, existMedCondition, peopleTraveling, tripDuration
        FROM userInfoCache
        WHERE email = ?
    """, (session["email"],))
    cached = cursor.fetchone()
    
    connection.close()
    return render_template("mainThing.html", cached=cached)


@app.route("/resultsPage", methods=["GET"])
@login_required
def resultsPage():
    error = None
    connection = sqlite3.connect("database.db")
    cursor = connection.cursor()

    cursor.execute("""
    SELECT age, approxSalary, existMedCondition, peopleTraveling, tripDuration
    FROM userInfoCache 
    WHERE email = ? 
    """, (session["email"],)
    )
    sort = request.args.get("sort", "price")
        
    user = cursor.fetchone()
    if not user:
        connection.close()
        return render_template("resultsPage.html", error="Before viewing results, please enter information", results = [], id=session.get("id"))
    age, salApprox, medExist, people, duration = user

    cursor.execute("""
    SELECT name, baseRate, ageRate, salaryRate, existMedCondRate, travelDurationRate, peopleTravelRate, coverage
    FROM firms
    """)
    firms = cursor.fetchall()
    
    results = []

    for firm in firms:
        name, base, ageRate, salaryRate, medRate, durRate, peopleRate, coverage = firm
        price = base
        price += (ageRate * int(age)) + (salaryRate * int(salApprox)) + (durRate * int(duration)) + (peopleRate * int(people))
        if medExist == 1:
            price += medRate
        firmResult = {
            "name": name,
            "price": round(price, 2),
            "coverage": []
        }

        coverage = str(coverage)
        if len(coverage)<4: #for whatever reason
            while len(coverage)<4:
                coverage+="0"
        
        if coverage[0]=="1":
            firmResult["coverage"].append("A")
        if coverage[1]=="1":
            firmResult["coverage"].append("B")
        if coverage[2]=="1":
            firmResult["coverage"].append("C")
        if coverage[3]=="1":
            firmResult["coverage"].append("D")
        results.append(firmResult)

    resultsPrice = sorted(results, key=lambda x: x["price"])
    resultsAlpha = sorted(results, key=lambda x: x["name"])
    resultsCover = sorted(results, key=lambda x: len(x["coverage"]), reverse=True)
    
    sorts = {"price": resultsPrice, "alpha": resultsAlpha, "cover": resultsCover}
    display = sorts.get(sort, resultsPrice)
    
    connection.close()
    return render_template("resultsPage.html", results=display, sort=sort, id=session.get("id"))

@app.route("/logoutTemp")
def logoutTemp():
    session.clear()
    return redirect(url_for("login"))

@app.route("/clearCache")
@login_required
def clearCache():
    connection = sqlite3.connect("database.db")
    cursor = connection.cursor()
    cursor.execute("DELETE FROM userInfoCache WHERE email = ?",(session["email"],))
    connection.commit()
    connection.close()
    return redirect(url_for("mainThing"))

@app.route("/modify", methods=["GET", "POST"])
@login_required
def modify():
    if session["id"]!=1:
        return redirect(url_for("mainThing"))
    error = None
    success = None

    if request.method == "POST":
        action = request.form.get("action")
        connection = sqlite3.connect("database.db")
        cursor = connection.cursor()

        if action == "addFirm":
            try:
                name = request.form["name"]
                if not name:
                    raise ValueError("gng why input empty name skull emoji") #python error for invalid input

                baseRate = float(request.form["baseRate"])
                ageRate = float(request.form["ageRate"])
                salaryRate = float(request.form["salaryRate"])
                existMedCondRate = float(request.form["existMedCondRate"])
                travelDurationRate = float(request.form["travelDurationRate"])
                peopleTravelRate = float(request.form["peopleTravelRate"])

                coverage = (
                    request.form.get("coverageA", "0")[0] + #Get from coverageA, the first value (which is if it checked or not.) If it doesn't exist, return 0
                    request.form.get("coverageB", "0")[0] +
                    request.form.get("coverageC", "0")[0] +
                    request.form.get("coverageD", "0")[0]
                )
                
                if coverage == "0000":
                    raise ValueError("what u tryin to do")
                
                cursor.execute("""
                INSERT INTO firms (name, baseRate, ageRate, salaryRate, existMedCondRate, travelDurationRate, peopleTravelRate, coverage)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?)""", (name, baseRate, ageRate, salaryRate, existMedCondRate, travelDurationRate, peopleTravelRate, coverage))
                connection.commit()
                success = "added firm :D"
            
            except ValueError as valE:
                error = f"The value for {valE} was invalid."
            except sqlite3.IntegrityError:
                error = "The firm name already exists."
            finally:
                connection.close()
        elif action == "resetPassword":
            try:
                email = request.form["resetEmail"]
                new_password = request.form["newPassword"]
                cursor.execute("UPDATE users SET passwordHash=? WHERE email = ?", (generate_password_hash(new_password), email))

                if cursor.rowcount == 0: #if no rows matched email, then:
                    error = "no user exists with that email"
                else: 
                    connection.commit()
                    success = "Password reset successfully"
            except Exception as e:
                error = f"something went wrong somehow lol: {e}"
            finally:
                connection.close()
                
    return render_template("modify.html", error=error, success=success)

if __name__ == "__main__":
    app.run(debug=True)