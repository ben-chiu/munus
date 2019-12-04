import sqlite3

database = sqlite3.connect('munus.db')
db = database.cursor()

a = input('what function do you want to do?')

if a == 'create':
    db.execute('CREATE TABLE users(id INTEGER UNIQUE, email TEXT, hash TEXT, building TEXT, room TEXT, money DEFAULT 0, stripeID TEXT NOT NULL, PRIMARY KEY (id));')

if a == 'test':
    print(len(db.execute('SELECT * FROM products').fetchall()))

if a == 'delete':
    db.execute('DROP TABLE products')
