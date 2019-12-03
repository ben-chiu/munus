from bs4 import BeautifulSoup, SoupStrainer
import requests

categories = ['vitamins', 'home-health-care', 'health-medicine', 'personal-care',
'diet-nutrition', 'beauty', 'baby-child', 'household-grocery']

products = []

def scrape(url, realItems, pages = False):
    mpages = 0
    response = requests.get(url, timeout = 15)
    content = BeautifulSoup(response.content, 'html.parser')

    items = content.findAll('a', href = True)

    for link in items:
        if 'prodid' in link['href'] and not 'reviews' in link['href']:
            realItems.append(link['href'])

        if pages:
            if '?page=' in link['href']:
                mpages = max(mpages, int(link['href'][link['href'].find('?page=') + 6:]))

    if pages:
        return(realItems, mpages)
    else:
        return(realItems)




for cat in categories:
    pages = 0

    # opening the page
    products, pages = scrape("https://www.cvs.com/shop/" + cat + "?page=1", products, True)

    for i in range(2, pages + 1):

        products = scrape('https://www.cvs/com/shop/' + cat + '?pages=' + str(i), products)

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
