from bs4 import BeautifulSoup # , SoupStrainer
import requests
from time import sleep
import re
from multiprocessing import Pool
import random

y = 0

def scrape(url):
    try:
        sleep(random.random())
        response = requests.get(url, timeout = 45)
        content = BeautifulSoup(response.content, 'html.parser')

        global y
        print(y)
        y += 1

        x = open('temp.txt', 'w')
        print(str(content), file = x)
        x.close()



        # tries to find the best title for an item
        title = str(content.find('title'))
        title = title.replace('&amp;', '&')
        if '(with Photos' in title:
            title = title[title.index('>')+1:title.index('(with Photos')-1]
        else:
            if ':' in title:
                title = title[title.index('>')+1:title.index(':')-1]
            else:
                title = title[title.index('>')+1:title.index('<')-1] # HAS ISSUE WITH NOT EXISTING STRING

        # uses regex to find the price of an item
        html = str(content)
        price = re.search('var productData (.{0,5000})\"price\":{\"value\":\"(.{1,6})\"\,\"currencyCode\":\"USD\"}', html).group(2)


        return([title, price])
    except:
        print('error', url)


f = open('output.txt', 'r')

if f.readline() != "completed\n":
    print("The catalogue is not completely scraped")
    quit()

a = f.readline()
urls = []

p = Pool(10)

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