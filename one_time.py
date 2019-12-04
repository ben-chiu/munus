import sqlite3

database = sqlite3.connect('munus.db')
db = database.cursor()

# db.execute('CREATE TABLE products(store varchar(255), name varchar(255), price int);')

print(db.execute('SELECT * FROM products').fetchall())
