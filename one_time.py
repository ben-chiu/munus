import sqlite3
import time
from datetime import date

database = sqlite3.connect('munus.db', isolation_level = None)
db = database.cursor()

a = input('what function do you want to do?')

if a == 'create':
    db.execute('CREATE TABLE orders(user_id INTEGER, product_id INTEGER, wtp INTEGER, expir TIME, id INTEGER PRIMARY KEY);')

if a == 'test':
    print(db.execute('SELECT * FROM orders').fetchall())

if a == 'unique':
    db.execute("DROP TABLE history")

if a == 'display':
    for i in range(1):print(db.execute('SELECT * FROM products ORDER BY id DESC').fetchall()[:10000][i])
    #print(db.execute("SELECT * FROM products WHERE store == 'animezakka';").fetchall()[:10])

if a=='dorm crew':
    db.execute("INSERT INTO products (store, name, price, id) VALUES ('dormcrew', 'Toilet Paper', 0, 19988);")

if a in ['&pizza', 'saloniki','swissbakers','animezakka','crimsoncorner']:
    f = open(a+'.txt', 'r')
    b = f.readline()
    b = f.readline()
    while b:
        print(b,'this is b')
        b = b.replace('\n','').split(', ')
        statement = "INSERT INTO products (store, name, price) VALUES (\"{0}\", \"{1}\", {2});".format(a, b[0], b[1])
        print(statement)
        try:
            db.execute(statement)
        except Exception as e:
            print(e)
        b = f.readline()

if a == 'a':
    print(db.execute("ALTER TABLE products ADD id INTEGER;"))

if a == 'x':
    for j in range(19988):
        statement1 = "SELECT name FROM products ORDER BY name LIMIT 1 OFFSET {0};".format(j)
        try:
            statement = "UPDATE products SET id = {0} WHERE name = \"{1}\";".format(j, db.execute(statement1).fetchone()[0])
            db.execute(statement)
        except:
            try:
                statement = "UPDATE products SET id = {0} WHERE name = '{1}';".format(j, db.execute(statement1).fetchone()[0])
                db.execute(statement)
            except Exception as e:
                print('error',e)
                time.sleep(4)
        if j%1000 == 0:
            print(j)

if a == "add":
    db.execute("UPDATE users SET money = 10000000 WHERE email = 'a@a.a';")

if a =='day':
    f = open('day.txt', 'w')
    print(date.today(), file = f)
    f.close()

if a == 'delete':
    db.execute("DELETE FROM orders WHERE expir = '';")
