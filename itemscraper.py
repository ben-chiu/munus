'''

This program opens output.txt, which contains the URLs to each item in the catalogue, and scrapes that URL for the price and name of the item. It then stores this in a database.

improvements: include in store availability? optimize?


'''

from bs4 import BeautifulSoup # , SoupStrainer
import requests
from time import sleep
import re
from multiprocessing import Pool
import random
import sqlite3

NUM_THREADS = 20

database = sqlite3.connect('munus.db', isolation_level = None)
db = database.cursor()

y = 0

def scrape(url):
    try:
        sleep(random.random() * 2 + 1)
        response = requests.get(url, timeout = 45, headers={'referer': 'https://www.google.com'})
        # response = requests.get('http://api.scraperapi.com', timeout = 45, params = {'api_key':'e7f8a201b10d57fd873c3cc984b694c0', 'url': url})
        content = BeautifulSoup(response.content, 'html.parser')

        global y
        #print(y)
        y += 1

        x = open('temp.txt', 'w')
        print(str(content), file = x)
        x.close()



        # tries to find the best title for an item
        title = str(content.find('title'))
        title = title.replace('&amp;', '&').replace('\n', '')
        if 'Online' in title:
            return(None)
        if '(with Photos' in title:
            title = title[:title.index('(with Photos')-1]
        if ':' in title:
            title = title[:title.index(':')-1]
        if ' - ' in title:
            title = title[:title.index(' - ')-1]
        if '<' in title[1:]:
            title = title[:title[1:].index('<')-1]
        title = title[title.index('>')+1:]



        # uses regex to find the price of an item
        html = str(content)
        price = re.search('var productData (.{0,5000})\"price\":{\"value\":\"(.{1,6})\"\,\"currencyCode\":\"USD\"}', html).group(2)

        prodid = url[url.find('-prodid-')+8:]

        return([title, price])
    except Exception as e:
        print('error', e, url)


f = open('output.txt', 'r')

if f.readline() != "completed\n":
    print("The catalogue is not completely scraped")
    quit()

a = f.readline()
urls = []

p = Pool(NUM_THREADS)

while a:
    urls.append('https://www.cvs.com' + a[:-1])
    a = f.readline()

x = []

try:
    x = p.map(scrape, urls)
except Exception as e:
    print('error',e)
except KeyboardInterrupt:
    f.close()
    p.terminate()
    p.join()
    quit()

print(x)

for i in x:
    if i:
        '''query = 'INSERT INTO products (store, name, price) VALUES (%s,%s,%s);'
        val = ('CVS', i[0], i[1])
        db.execute(query, val)'''
        i[0] = i[0].replace('\'', '\\\'').replace('\"', '\\\"')
        try:
            statement = "INSERT INTO products (store, name, price) VALUES ('{0}', \'{1}\', '{2}')".format('CVS', i[0], i[1])
            db.execute(statement)
        except Exception as e:
            try:
                statement = "INSERT INTO products (store, name, price) VALUES ('{0}', \"{1}\", '{2}')".format('CVS', i[0], i[1])
                db.execute(statement)
            except Exception as e:
                print('failure',e)
#database.commit()

db.close()
database.close()
