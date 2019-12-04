import sqlite3

database = sqlite3.connect('munus.db', isolation_level = None)
db = database.cursor()

a = input('what function do you want to do?')

if a == 'create':
    db.execute('CREATE TABLE history(user_id INTEGER UNIQUE, type TEXT, product_id INTEGER, amount INTEGER, timestamp TIME);')

if a == 'test':
    print(len(db.execute('SELECT * FROM products').fetchall()))

if a == 'delete':
    db.execute('DROP TABLE users')

if a == 'display':
    for i in range(100):print(db.execute('SELECT * FROM products').fetchall()[:100][i])
    #print(db.execute("SELECT * FROM products WHERE store == 'animezakka';").fetchall()[:10])

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
    print(db.execute("ALTER TABLE history ADD timestamp TIME;"))

'''if a == 'x':
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
                print('error')
                sleep(4)
        if j%1000 == 0:
            print(j)'''
