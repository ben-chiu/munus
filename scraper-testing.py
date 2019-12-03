from bs4 import BeautifulSoup, SoupStrainer
import requests

categories = ['vitamins', 'home-health-care', 'health-medicine', 'personal-care',
'diet-nutrition', 'beauty', 'baby-child', 'household-grocery']

products = []

def scrape(url, realItems, pages = False):
    mpage = 0
    response = requests.get(url, timeout = 15)
    content = BeautifulSoup(response,.content, 'html.parser')

    items = content.findAll('a', href = True)

    for link in items:
        if 'prodid' in link['href'] and not 'reviews' in link['href']:
            realItems.append(link['href'])

        if pages:
            if '?page=' in link['href']:
                mpages = max(mpages, int(link['href'][link['href'].find('?page=') + 6:]))








for cat in categories:
    pages = 0

    # opening the page
    url = "https://www.cvs.com/shop/" + cat + "?page=1"
    response = requests.get(url, timeout = 5)
    content = BeautifulSoup(response.content, "html.parser")


    #finding all links to products in the first page, as well as the maximum page
    items = content.findAll('a', href=True)

    for link in items:

        #finding the links for all the products
        if 'prodid' in link['href'] and not 'reviews' in link['href']:
            products.append(link['href'])

        #finding the highest page number there is for this section
        if '?page=' in link['href']:
            pages = max(pages, int(link['href'][link['href'].find('?page=') + 6:]))

    for i in range(2, pages + 1):
        url = 'https://www.cvs.com/shop/' + cat + '?page=' + str(i)
        response = requests.get(url, timeout = 15)
        content = BeautifulSoup(response.content, 'html.parser')

        items = content.findAll('a', href=True)
        for link in items:
            if 'prodid' in link['href'] and not 'reviews' in link['href']:
                products.append(link['href'])

        print(i, len(products))

    print('\n'.join(products))



''' no longer necessary?
import urllib.request

resp = urllib.request.urlopen(url)

soup = BeautifulSoup(resp, from_encoding=resp.info().get_param('charset'), features='lxml')

products = []

for link in soup.find_all('a', href=True):
    if 'prodid' in link['href'] and not 'reviews' in link['href']:
        products.append(link['href'])
'''
