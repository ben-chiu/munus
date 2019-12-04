import os
import stripe

from cs50 import SQL
from flask import Flask, flash, jsonify, redirect, render_template, request, session, url_for
from flask_session import Session
from tempfile import mkdtemp
from werkzeug.exceptions import default_exceptions, HTTPException, InternalServerError
from werkzeug.security import check_password_hash, generate_password_hash
from datetime import datetime

from helpers import apology, login_required, lookup, usd

# Configure application
app = Flask(__name__)

pub_key = "pk_test_aw8Q7dyf81YYvJSmX7dfFofO0041RjcEyL"
secret_key = "sk_test_M67xEbjFWyt6I8TMlkI5t4R300QIwHpNvE"

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
app.config["SESSION_FILE_DIR"] = mkdtemp()
app.config["SESSION_PERMANENT"] = False
app.config["SESSION_TYPE"] = "filesystem"
Session(app)

# Configure CS50 Library to use SQLite database
db = SQL("sqlite:///finance.db")

# Make sure API key is set
if not os.environ.get("API_KEY"):
    raise RuntimeError("API_KEY not set")


@app.route("/")
@login_required
def index():
    # where I'll store all final data
    rows = []
    totalValue = 0
    # gets list of all distinct stocks from transactions summing up shares
    stocks = db.execute("SELECT symbol, SUM(shares) FROM transactions WHERE user_id=:user_id GROUP BY symbol",
                        user_id=session["user_id"])
    # goes through each stock, gathers info and puts it into rows
    for stock in stocks:
        if not stock["SUM(shares)"] == 0:
            info = lookup(stock["symbol"])
            currentValue = info["price"] * stock["SUM(shares)"]
            totalValue += currentValue
            # adding to rows
            rows.append({"Symbol": stock["symbol"], "Name": info["name"], "Shares": stock["SUM(shares)"],
                         "Price": usd(info["price"]), "TOTAL": usd(currentValue)})
    # gets cash
    cash = db.execute("SELECT cash FROM users WHERE id =:user_id", user_id=session["user_id"])[0]['cash']
    totalValue += cash
    return render_template("index.html", rows=rows, cashBalance=usd(cash), currentTotal=usd(totalValue))


@app.route("/buy", methods=["GET", "POST"])
@login_required
def buy():
    if request.method == "GET":
        return render_template("buy.html")
    else:
        symbol = request.form.get("symbol")
        shares = request.form.get("shares")
        if not symbol:
            return apology("Missing symbol")
        info = lookup(symbol)
        if not info:
            return apology("Invalid Symbol", 403)
        if not shares or int(shares) < 1:
            return apology("Must buy 1 or more shares", 403)
        cash = db.execute("SELECT cash FROM users WHERE id =:user_id", user_id=session["user_id"])[0]['cash']
        if cash < (int(shares) * info["price"]):
            return apology("Insufficient funds", 403)
        if not db.execute("INSERT INTO transactions (user_id, symbol, shares, price, timestamp) VALUES (:user_id, :symbol, :shares, :price, :timestamp)", user_id=session["user_id"], symbol=info["symbol"], shares=shares, price=info["price"], timestamp=datetime.now()):
            return apology("Transaction failed", 403)
        cashBalance = cash - (int(shares) * info["price"])
        db.execute("UPDATE users SET cash = :value WHERE id=:user_id", value=cashBalance, user_id=session["user_id"])
        flash('Bought!')
        return redirect("/")


@app.route("/history")
@login_required
def history():
    rows = db.execute("SELECT symbol, shares, price, timestamp FROM transactions WHERE user_id=:user_id",
                      user_id=session["user_id"])
    for row in rows:
        row["price"] = usd(row["price"])
        if row["shares"] > 0:
            row["type"] = "Buy"
        else:
            row["type"] = "Sell"
    return render_template("history.html", rows=rows)


@app.route("/login", methods=["GET", "POST"])
def login():
    """Log user in"""

    # Forget any user_id
    session.clear()

    # User reached route via POST (as by submitting a form via POST)
    if request.method == "POST":

        # Ensure username was submitted
        if not request.form.get("username"):
            return apology("must provide username", 403)

        # Ensure password was submitted
        elif not request.form.get("password"):
            return apology("must provide password", 403)

        # Query database for username
        rows = db.execute("SELECT * FROM users WHERE username = :username",
                          username=request.form.get("username"))

        # Ensure username exists and password is correct
        if len(rows) != 1 or not check_password_hash(rows[0]["hash"], request.form.get("password")):
            return apology("invalid username and/or password", 403)

        # Remember which user has logged in
        session["user_id"] = rows[0]["id"]

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


@app.route("/quote", methods=["GET", "POST"])
@login_required
def quote():
    if request.method == "GET":
        return render_template("quote.html")
    else:
        symbol = request.form.get("symbol")
        if not symbol:
            return apology("Missing symbol")
        info = lookup(symbol)
        if not info:
            return apology("Invalid Symbol", 403)
        return render_template("quoted.html", name=info["name"], price=usd(info["price"]), symbol=info["symbol"])


@app.route("/register", methods=["GET", "POST"])
def register():
    if request.method == "GET":
        return render_template("register.html")
    else:
        username = request.form.get("username")
        if not username:
            return apology("Must provide username", 403)
        usernames = db.execute("SELECT username FROM users")  # list of dictionaries containing usernames
        for d in usernames:  # for a given dictionary
            if username == d['username']:  # check to see if already in use
                return apology("Username is not available", 403)

        password = request.form.get("password")
        confirmation = request.form.get("confirmation")
        if not password:
            return apology("Must provide password", 403)
        if not confirmation:
            return apology("Must confirm password", 403)
        if not password == confirmation:
            return apology("Passwords do not match", 403)
        hashval = generate_password_hash(password)
        db.execute("INSERT INTO users (username, hash) VALUES (:username, :hashval)", username=username, hashval=hashval)
        session["user_id"] = db.execute("SELECT id FROM users WHERE username=:username", username=username)[0]["id"]
        print(session["user_id"])
        flash('Registered!')
        return redirect("/")


@app.route("/sell", methods=["GET", "POST"])
@login_required
def sell():
    if request.method == "GET":
        rows = []
        stocks = db.execute("SELECT symbol, SUM(shares) FROM transactions WHERE user_id=:user_id GROUP BY symbol",
                            user_id=session["user_id"])
        for stock in stocks:
            if not stock["SUM(shares)"] == 0:
                rows.append({"Symbol": stock["symbol"]})
        return render_template("sell.html", rows=rows)
    else:
        symbol = request.form.get("symbol")
        sellShares = request.form.get("shares")
        if not symbol:
            return apology("Missing symbol", 403)
        if not sellShares or int(sellShares) < 1:
            return apology("Sell min. 1 share", 403)
        shareDict = db.execute("SELECT SUM(shares) FROM transactions WHERE user_id=:user_id AND symbol=:symbol GROUP BY symbol",
                               user_id=session["user_id"], symbol=symbol)
        shareNum = shareDict[0]["SUM(shares)"]
        if shareNum == 0:
            return apology("No Shares Owned", 403)
        if int(sellShares) > shareNum:
            return apology("Insufficient Shares", 403)
        info = lookup(symbol)
        db.execute("INSERT INTO transactions (user_id, symbol, shares, price, timestamp) VALUES (:user_id, :symbol, :shares, :price, :timestamp)",
                   user_id=session["user_id"], symbol=symbol, shares=(-1*int(sellShares)), price=info["price"], timestamp=datetime.now())
        cash = db.execute("SELECT cash FROM users WHERE id =:user_id", user_id=session["user_id"])[0]['cash']
        cashBalance = cash + (int(sellShares) * info["price"])
        db.execute("UPDATE users SET cash = :value WHERE id=:user_id", value=cashBalance, user_id=session["user_id"])
        flash('Sold!')
        return redirect("/")


@app.route("/change", methods=["GET", "POST"])
@login_required
def change():
    if request.method == "GET":
        return render_template("change.html")
    else:
        opassword = request.form.get("opassword")
        if not opassword:
            return apology("Must provide old password", 403)
        h = db.execute("SELECT hash FROM users WHERE id=:user_id", user_id=session["user_id"])
        print(h)
        if not check_password_hash(h[0]["hash"], opassword):
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
        db.execute("UPDATE users SET hash=:hashval WHERE id=:user_id", hashval=hashval, user_id=session["user_id"])
        flash('Password Changed!')
        return redirect("/")

@app.route("/payment", methods=["GET", "POST"])
@login_required
def change():
    if request.method == "GET":
        return render_template("payment.html", pub_key=pub_key)

def errorhandler(e):
    """Handle error"""
    if not isinstance(e, HTTPException):
        e = InternalServerError()
    return apology(e.name, e.code)

# Listen for errors
for code in default_exceptions:
    app.errorhandler(code)(errorhandler)
