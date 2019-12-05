import os
import stripe

import sqlite3
from flask import Flask, flash, jsonify, redirect, render_template, request, session, url_for
from flask_session import Session
from tempfile import mkdtemp
from werkzeug.exceptions import default_exceptions, HTTPException, InternalServerError
from werkzeug.security import check_password_hash, generate_password_hash
from datetime import datetime
from helpers import apology, login_required, usd
from flask import send_from_directory
from datetime import datetime


# Configure application
app = Flask(__name__)

# Set Stripe API keys
pub_key = "pk_test_aw8Q7dyf81YYvJSmX7dfFofO0041RjcEyL"
secret_key = "sk_test_M67xEbjFWyt6I8TMlkI5t4R300QIwHpNvE"
stripe.api_key = secret_key

# Ensure templates are auto-reloaded
app.config["TEMPLATES_AUTO_RELOAD"] = True

# Ensure responses aren't cached
@app.after_request
def after_request(response):
    response.headers["Cache-Control"] = "no-cache, no-store, must-revalidate"
    response.headers["Expires"] = 0
    response.headers["Pragma"] = "no-cache"
    return response


# Custom filter
app.jinja_env.filters["usd"] = usd

# Configure session to use filesystem (instead of signed cookies)
app.config["SESSION_PERMANENT"] = False
app.config["SESSION_FILE_DIR"] = mkdtemp()
app.config["SESSION_TYPE"] = "filesystem"
Session(app)

database = sqlite3.connect('munus.db', isolation_level = None, check_same_thread = False)
db = database.cursor()

@app.route("/")
@login_required
def index():
    return render_template("index.html", balance = session["balance"])

@app.route("/history")
@login_required
def history():
    statement = "SELECT type, product_id, amount, timestamp FROM history WHERE user_id={0}".format(session["user_id"])
    rows = db.execute(statement).fetchall()
    print("****************")
    print(rows)

    returns = []
    for row in rows:
        ret = [] # type, amt, store, productname
        ret.append(row[0].upper())
        ret.append('$'+format(row[2], ',.2f'))
        if row[0] not in ['deposit', 'withdrawal']:
            statement = "SELECT store FROM products WHERE id = {0}".format(row[1])
            ret.append(db.execute(statement).fetchone()[0])
            statement = "SELECT name FROM products WHERE id = {0}".format(row[1])
            ret.append(db.execute(statement).fetchone()[0])
        else:
            ret.append('')
            ret.append('')
        ret.append(row[3])
        returns.append(ret)
    print(len(returns))
    if len(returns) == 0:
        return render_template("history.html", rows = 0, balance = session['balance'])
    return render_template("history.html", rows=returns, balance=session['balance'])


@app.route("/login", methods=["GET", "POST"])
def login():
    """Log user in"""

    # Forget any user_id
    session.clear()

    # User reached route via POST (as by submitting a form via POST)
    if request.method == "POST":

        # Ensure email was submitted
        if not request.form.get("email"):
            return apology("must provide email", 403)

        # Ensure password was submitted
        elif not request.form.get("password"):
            return apology("must provide password", 403)

        # Query database for email
        statement = "SELECT * FROM users WHERE email = '{0}'".format(request.form.get("email"))
        rows = db.execute(statement).fetchall()

        # Ensure email exists and password is correct
        if len(rows) != 1 or not check_password_hash(rows[0][2], request.form.get("password")):
            return apology("invalid email and/or password", 403)

        # Remember which user has logged in
        session["user_id"] = rows[0][0]
        session["stripe_id"] = rows[0][6]
        statement = "SELECT money FROM users WHERE id = {0}".format(session["user_id"])
        balance = db.execute(statement).fetchone()
        session["balance"] = usd(balance[0])

        # Redirect user to home page
        return redirect("/")

    # User reached route via GET (as by clicking a link or via redirect)
    else:
        return render_template("login.html")


@app.route("/logout")
def logout():
    """Log user out"""

    # Forget any user_id
    session.clear()

    # Redirect user to login form
    return redirect("/")


@app.route("/register", methods=["GET", "POST"])
def register():
    if request.method == "GET":
        return render_template("register.html")
    else:
        e = request.form.get("email")
        if not e:
            return apology("Must provide email", 403)
        emails = db.execute("SELECT email FROM users").fetchall()  # list of dictionaries containing emails
        for d in emails:  # for a given dictionary
            if e == d[0]:  # check to see if already in use
                return apology("Email already in use", 403)
        password = request.form.get("password")
        confirmation = request.form.get("confirmation")
        building = request.form.get("building")
        room = request.form.get("room")
        if not password:
            return apology("Must provide password", 403)
        if not confirmation:
            return apology("Must confirm password", 403)
        if not password == confirmation:
            return apology("Passwords do not match", 403)
        if not building:
            return apology("Must provide building", 403)
        if not room:
            return apology("Must provide room number", 403)
        cust = stripe.Customer.create(email=e)
        stripeid = cust["id"]
        hashval = generate_password_hash(password)
        statement = "INSERT INTO users (email, hash, building, room, stripeID) VALUES ('{0}', '{1}', '{2}', '{3}', '{4}')".format(e, hashval, building, room, stripeid)
        db.execute(statement)
        flash('Registered!')

        # log the user in automatically after registration
        statement = "SELECT id FROM users WHERE email='{0}'".format(e)
        session["user_id"] = db.execute(statement).fetchone()[0]
        session["stripe_id"] = stripeid
        session["balance"] = usd(0)
        return render_template('add.html')

        return redirect("/add", balance=session["balance"])


@app.route("/add")
@login_required
def add():
    if request.method == "GET":
        return render_template("add.html", balance=session["balance"])


@app.route("/payment")
@login_required
def payment():
    if not request.args.get("amount"):
        return apology("Invalid access to page", 403)
    else:
        a = int(float(request.args.get("amount")) * 100)
        session["add"] = a
        return render_template("payment.html", pub_key=pub_key, amount=a, dollars=usd(a/100), balance=session["balance"])


@app.route("/charge", methods=["POST"])
@login_required
def charge():
    ''' might be incorrect with adding to history '''
    if request.method == "POST":
        a = session["add"]
        stripe.Customer.modify(session["stripe_id"], source=request.form["stripeToken"])
        print(session["stripe_id"])
        print(request.form["stripeToken"])
        charge = stripe.Charge.create(customer = session["stripe_id"], amount = a, currency = "usd", description="Munus deposit")
        statement = "SELECT money FROM users WHERE id = {0}".format(session['user_id'])
        current = db.execute(statement).fetchone()[0]
        balance = current + a/100
        session["balance"] = usd(balance)
        statement = "UPDATE users SET money = {0} WHERE id = {1}".format(balance, session['user_id'])
        db.execute(statement)
        flash("money added succesfully")
        statement = "INSERT INTO history (user_id, type, product_id, amount, timestamp) VALUES ({0}, 'deposit', -1, {1}, '{2}')".format(session['user_id'], a/100, datetime.now())
        print(statement)
        db.execute(statement)

        return render_template("success.html", amount=usd(a/100), balance=session["balance"])
    else:
        return apology("Invalid access to page", 403)

@app.route("/success")
@login_required
def success():
    return render_template("success.html")


@app.route("/change", methods=["GET", "POST"])
@login_required
def change():
    if request.method == "GET":
        return render_template("change.html", balance=session["balance"])
    else:
        opassword = request.form.get("opassword")
        if not opassword:
            return apology("Must provide old password", 403)

        statement = "SELECT hash FROM users WHERE id = {0}".format(session["user_id"])
        h = db.execute(statement).fetchone()
        if not check_password_hash(h[0], opassword):
            return apology("Incorrect old password", 403)
        npassword = request.form.get("npassword")
        confirmation = request.form.get("confirmation")
        if not npassword:
            return apology("Must provide new password", 403)
        if not confirmation:
            return apology("Must confirm new password", 403)
        if not npassword == confirmation:
            return apology("Passwords do not match", 403)
        hashval = generate_password_hash(npassword)
        statement = "UPDATE users SET hash= '{0}' WHERE id= {1}".format(hashval, session["user_id"])
        print(statement)
        db.execute(statement)
        flash('Password Changed!')
        return redirect("/")

@app.route("/catalogue", methods=["GET", "POST"])
@login_required
def catalogue():
    if request.method == "GET":
        stores = db.execute("SELECT DISTINCT store FROM products")
        render_template("catalogue.html")
        '''add more'''


def errorhandler(e):
    """Handle error"""
    if not isinstance(e, HTTPException):
        e = InternalServerError()
    return apology(e.name, e.code)

# Listen for errors
for code in default_exceptions:
    app.errorhandler(code)(errorhandler)

# db.close()
# database.close()
