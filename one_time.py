import sqlite3

database = sqlite3.connect('munus.db')
db = database.cursor()

a = input('what function do you want to do?')

if a == 'create':
    db.execute('CREATE TABLE products(store varchar(255), name varchar(255), price int, UNIQUE (name));')

if a == 'test':
    print(len(db.execute('SELECT * FROM products').fetchall()))

if a == 'delete':
    db.execute('DROP TABLE products')

if a == 'display':
    for i in range(100):print(db.execute('SELECT * FROM products').fetchall()[:100][i])
