import sqlite3

database = sqlite3.connect('munus.db', isolation_level = None)
db = database.cursor()

a = input('what function do you want to do?')

if a == 'create':
    db.execute('CREATE TABLE users(id INTEGER UNIQUE, email TEXT, hash TEXT, building TEXT, room TEXT, money DEFAULT 0, stripeID TEXT NOT NULL, PRIMARY KEY (id));')

if a == 'test':
    print(len(db.execute('SELECT * FROM products').fetchall()))

if a == 'delete':
    db.execute('DROP TABLE users')

if a == 'display':
    #for i in range(100):print(db.execute('SELECT * FROM products').fetchall()[:100][i])
    print(db.execute("SELECT price FROM products WHERE store == 'animezakka';").fetchall())

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
