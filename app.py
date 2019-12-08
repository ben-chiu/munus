import os
import stripe

import sqlite3
from flask import Flask, flash, jsonify, redirect, render_template, request, session, url_for
from flask_session import Session
from tempfile import mkdtemp
from werkzeug.exceptions import default_exceptions, HTTPException, InternalServerError
from werkzeug.security import check_password_hash, generate_password_hash
from datetime import date, datetime
from helpers import apology, login_required, usd
from flask import send_from_directory


# Configure application
app = Flask(__name__)

# Set Stripe API keys
pub_key = "pk_test_aw8Q7dyf81YYvJSmX7dfFofO0041RjcEyL"
secret_key = "sk_test_M67xEbjFWyt6I8TMlkI5t4R300QIwHpNvE"
stripe.api_key = secret_key

# Ensure templates are auto-reloaded
app.config["TEMPLATES_AUTO_RELOAD"] = True

def compareDays(d1, d2):
    '''function to compare days
        inputs: two days in format yyyy-mm-dd
        outputs True if d1 < d2, else false'''
    d1 = list(map(int, d1.split('-')))
    d2 = list(map(int, d2.split('-')))
    for i in range(3):
        if d1[i] < d2[i]:
            return(True)
    return(False)





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

# open the database as db with autocommit on
database = sqlite3.connect('munus.db', isolation_level = None, check_same_thread = False)
db = database.cursor()

#checking to see if the last stored day is the current day, if not, removing all the expired orders
f = open('day.txt', 'r')
lastDay = f.readline()
f.close()
currDay = str(date.today())
if lastDay[:-2] != currDay:
    orders = db.execute("SELECT expir, id FROM orders;").fetchall()
    badOrders = []
    for i in orders:
        if compareDays(i[0], currDay):
            badOrders.append(i[1])

    # for each bad order, going into the user id and adding the price * quantity + tip back to their money
    for i in badOrders:
        statement = "SELECT user_id, product_id, quantity, wtp FROM orders WHERE id = {0};".format(i)
        order = db.execute(statement).fetchone()
        statement = "SELECT price FROM products WHERE id = {0};".format(order[1])

        p = db.execute(statement).fetchone()[0]
        total = p * order[2] + order[3]
        statement = "UPDATE users SET money = money + {0} WHERE id = {1};".format(total, order[0])
        db.execute(statement)

        # delete the expired order
        statement = "DELETE FROM orders WHERE id = {0};".format(i)
        db.execute(statement)

# write into the file the current day
f = open('day.txt', 'w')
print(currDay, file = f)
f.close()

# the homepage
@app.route("/")
@login_required
def index():
    return render_template("index.html", balance = session["balance"])

# shows the user a list of their completed transactions, including deposits, withdrawals, orders, and pickups
@app.route("/history")
@login_required
def history():
    statement = "SELECT type, product_id, amount, timestamp FROM history WHERE user_id={0}".format(session["user_id"])
    rows = db.execute(statement).fetchall()

    # select each transaction, then return the type, store, product name, and amount
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
    # if their history is empty, we want a different page that says they have no history
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
        statement = "SELECT * FROM users WHERE email = '{0}'".format(request.form.get("email").lower())
        rows = db.execute(statement).fetchall()

        # Ensure email exists and password is correct
        if len(rows) != 1 or not check_password_hash(rows[0][2], request.form.get("password")):
            flash("invalid email and/or password")
            return render_template("login.html")

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
        e = request.form.get("email").lower()
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
        return redirect("/add")


# sends them to the add page when they try to add money
@app.route("/add")
@login_required
def add():
    if request.method == "GET":
        return render_template("add.html", balance=session["balance"])


# adds the amount to the payment
@app.route("/payment")
@login_required
def payment():
    if not request.args.get("amount") or int(request.args.get("amount"))<1:
        return render_template("add.html", balance=session["balance"])
    else:
        a = int(float(request.args.get("amount")) * 100)
        session["add"] = a
        return render_template("payment.html", pub_key=pub_key, amount=a, dollars=usd(a/100), balance=session["balance"])

# uses the stripe API to add the money to the user database. it also adds to history
@app.route("/charge", methods=["POST"])
@login_required
def charge():
    ''' might be incorrect with adding to history '''
    if request.method == "POST":
        a = session["add"]
        stripe.Customer.modify(session["stripe_id"], source=request.form["stripeToken"])
        charge = stripe.Charge.create(customer = session["stripe_id"], amount = a, currency = "usd", description="Munus deposit")
        statement = "SELECT money FROM users WHERE id = {0}".format(session['user_id'])
        current = db.execute(statement).fetchone()[0]
        balance = current + a/100
        session["balance"] = usd(balance)
        statement = "UPDATE users SET money = {0} WHERE id = {1}".format(balance, session['user_id'])
        db.execute(statement)
        flash("money added succesfully")
        statement = "INSERT INTO history (user_id, type, product_id, amount, timestamp) VALUES ({0}, 'deposit', -1, {1}, '{2}')".format(session['user_id'], a/100, datetime.now())
        db.execute(statement)

        return render_template("success.html", amount=usd(a/100), balance=session["balance"])
    else:
        return apology("Invalid access to page", 403)

@app.route("/success")
@login_required
def success():
    return render_template("success.html")

# allows for changing a password
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

        # updates the password to the new value using the user id
        statement = "UPDATE users SET hash= '{0}' WHERE id= {1}".format(hashval, session["user_id"])
        db.execute(statement)
        flash('Password Changed!')
        return redirect("/")

@app.route("/catalogue", methods=["GET", "POST"])
@login_required
def catalogue():
    '''
    if request.method == "GET":
        statement = "SELECT DISTINCT store FROM products"
        storelist = db.execute(statement).fetchall()
        stores = [i[0] for i in storelist]
        storeReplace = {'crimsoncorner': 'Crimson Corner',
                        'animezakka': 'Anime Zakka',
                        'swissbakers': 'Swissbakers',
                        'saloniki': 'Saloniki',
                        'any': 'Any store'}

        storeNames = [storeReplace.get(n,n) for n in stores]

        return render_template("catalogue.html", stores=stores, balance=session["balance"], prod = False, storeReplace = storeReplace)
    else:'''
    statement = "SELECT DISTINCT store FROM products"
    storelist = db.execute(statement).fetchall()
    stores = [i[0] for i in storelist]

    # the dictionary for replacing the database codes with more presentable text
    storeReplace = {'crimsoncorner': 'Crimson Corner',
                    'animezakka': 'Anime Zakka',
                    'swissbakers': 'Swissbakers',
                    'saloniki': 'Saloniki',
                    'any': 'Any store'}

    storeNames = [storeReplace.get(n,n) for n in stores]

    store = request.form.get("store") # can also be "any"

    # when the page is first opened, there won't be any store selected so automatically set it to any store
    if not store:
        store = 'any'

    if store == "any" :
        statement = "SELECT name, price, id FROM products"
        productlist = db.execute(statement).fetchall()
    else:
        statement = "SELECT name, price, id FROM products WHERE store='{0}';".format(store)
        productlist = db.execute(statement).fetchall()

    # separate the values from the SQL query into its individual components
    names =[j[0].replace('\\\'','').replace('\\\"','') for j in productlist] # strips the backslashes from the names of the products
    prices = [j[1] for j in productlist]
    product_ids = ['/order?id='+str(j[2]) for j in productlist]
    return render_template("catalogue.html", stores = stores, product_ids = product_ids, store = store, names=names, prod = True, prices = prices, balance=session["balance"], storeReplace = storeReplace)

@app.route("/order", methods = ["GET", "POST"])
@login_required
def order():
    if request.method == "GET":
        # redirects the person to the order page for the individual product using the url
        statement = "SELECT * FROM products WHERE id = {0};".format(request.args.get("id"))
        item = db.execute(statement).fetchone()
        url = '/order?id='+str(item[3])
        return render_template("order.html", item = item, url = url, nOrd = True, date=date.today(), balance=session["balance"])
    elif request.method == "POST":
        expir = request.form.get("datefield")
        wtp = request.form.get("wtp")

        statement = "SELECT * FROM products WHERE id = {0};".format(request.args.get("id"))
        item = db.execute(statement).fetchone()

        if (float(wtp.replace(',','')) + float(item[2])) > (float(session["balance"].strip("$").replace(',',''))):
            flash("Insufficient funds. Please add money.")
            return render_template("add.html", balance=session["balance"])

        statement = "INSERT INTO orders (user_id, product_id, wtp, expir) VALUES ({0}, {1}, {2}, '{3}');".format(session['user_id'], item[3], wtp, expir)
        db.execute(statement)

        statementAmt = "SELECT money FROM users WHERE id = {0}".format(session['user_id'])
        amt = db.execute(statementAmt).fetchone()[0]
        print(amt)
        statement = "UPDATE users SET money = money - {0} WHERE id = {1}".format(float(wtp.replace(',','')) + float(item[2]), session['user_id'])
        db.execute(statement)
        # this does work
        session["balance"] = usd(amt - float(wtp.replace(',','')) - float(item[2]))

        return render_template("ordered.html", item = item, balance=session["balance"])


@app.route("/pickup", methods=["GET", "POST"])
@login_required
def pickup():
    if request.method == "GET":
        statement = "SELECT store, name, price, wtp, building, room, expir FROM orders JOIN products ON product_id=products.id JOIN users ON orders.user_id=users.id"
        infoList = db.execute(statement).fetchall()
        current = date.today()
        expSoon = []
        for i in infoList:
            expirInfo = list(map(int, i[6].split('-')))
            exp = date(expirInfo[0], expirInfo[1], expirInfo[2])
            if (exp - current).days < 2:
                expSoon.append("Yes")
            else:
                expSoon.append("No")
        return render_template("pickup.html", infoList=infoList, expSoon=expSoon, balance=session["balance"])

@app.route("/userorders")
@login_required
def userorders():
    if (request.args.get("cancelId")):
        #find value of order refund
        statement = "SELECT price, wtp FROM orders JOIN products ON product_id=products.id WHERE orders.id='{0}'".format(request.args.get("cancelId"))
        vals = db.execute(statement).fetchone()
        refund = vals[0] + vals[1]

        #delete order
        statement = "DELETE FROM orders WHERE id='{0}';".format(request.args.get("cancelId"))
        db.execute(statement)

        #add refund back to balance
        balance = float(session["balance"].strip("$").replace(',',''))
        newBalance = balance + refund;
        statement = "UPDATE users SET money='{0}' WHERE id='{1}';".format(newBalance, session["user_id"])
        session["balance"] = usd(newBalance)
    statement = "SELECT orders.id, name, store, wtp, price, expir FROM orders JOIN products ON product_id=products.id WHERE user_id='{0}'".format(session["user_id"])
    rows = db.execute(statement).fetchall()
    return render_template("userorders.html", rows=rows, balance=session["balance"])

@app.route('/payout')
@login_required
def payout():

    payment_intent = stripe.PaymentIntent.create(
      payment_method_types: ['card'],
      amount=1000,
      currency='usd',
      transfer_data={
        'destination': '{{CONNECTED_STRIPE_ACCOUNT_ID}}',
      }
    )

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
