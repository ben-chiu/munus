from bs4 import BeautifulSoup # , SoupStrainer
import requests
from time import sleep

def scrape(url):
    mpages = 0
    response = requests.get(url, timeout = 45)
    content = BeautifulSoup(response.content, 'html.parser')

    title = str(content.find('title'))
    if '(' in title:
        title = title[title.index('>')+1:title.index('(')]
    else:
        if ':' in title:
            title = title[title.index('>')+1:title.index(':')-1]
        title = title[title.index('>')+1:title.index('<')]

    html = str(content)
    

    return([title, price])


f = open('output.txt', 'r')

if f.readline() != "completed\n":
    print("The catalogue is not completely scraped")
    quit()

a = f.readline()


try:
    while a:
        print(scrape('https://www.cvs.com' + a))
        a = f.readline()
except:
    print('error')
