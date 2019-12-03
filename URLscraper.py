from bs4 import BeautifulSoup # , SoupStrainer
import requests
from time import sleep

def scrape(url, realItems, pages = False):
    mpages = 0
    response = requests.get(url, timeout = 45)
    content = BeautifulSoup(response.content, 'html.parser')

    items = content.findAll('a', href = True)

    for link in items:
        if 'prodid' in link['href'] and not 'reviews' in link['href'] and not 'https' in link['href']:
            realItems.append(link['href'])

        if pages:
            if '?page=' in link['href']:
                mpages = max(mpages, int(link['href'][link['href'].find('?page=') + 6:]))
    print(realItems[-1])
    if pages:
        return(realItems, mpages)
    else:
        return(realItems)

categories = ['vitamins', 'home-health-care', 'health-medicine', 'personal-care',
'diet-nutrition', 'beauty', 'baby-child', 'household-grocery']

products = []
f = open('output.txt', 'r')
firstLine = f.readline()
startCat = ''
if firstLine == 'completed\n':
    '''item = f.readline()
    while item:
        products.append(item[:-1])
        item = f.readline()
    a = list(set(products))
    temp = open('temp.txt', 'w')
    for i in a:
        print(i, file = temp)
    temp.close()
    f.close()
    f = open('output.txt', 'w')
    temp = open('temp.txt', 'r')
    print('completed', file = f)
    item = temp.readline()
    while item:
        print(item[:-1], file = f)
        item = temp.readline()
    temp.close()'''
    f.close()
    quit()


# if output is not empty, we have a list of URLs. We should take note of where to start scanning and copy over the URLs we already scraped
if firstLine:
    startCat, startPage = firstLine.split()
    startPage = int(startPage)

    item = f.readline()
    while item:
        products.append(item[:-1])
        item = f.readline()
f.close()

# run scraping algorithm as a try so we can store what we've completed if there's a keyboard int
try:
    i = 1 # dummy variable so we can store in tempoutput if keyboardinterrupt
    if not startCat:
        for cat in categories:
            pages = 0

            # scraping the first page of a category
            products, pages = scrape("https://www.cvs.com/shop/" + cat + "?page=2", products, True)


            # scraping all other pages
            for i in range(2, pages + 1):
                products = scrape('https://www.cvs.com/shop/' + cat + '?page=' + str(i), products)
                print(i, len(products))

    else:
        firstPage = True # we need to check if the first page after we restart is duplicated
        for cat in categories[categories.index(startCat):]:
            if startCat == cat and startPage != 1:
                dummyVar, pages = scrape("https://www.cvs.com/shop/" + cat + "?page=1", products, True)
                for i in range(startPage, pages + 1):
                    products = scrape('https://www.cvs.com/shop/' + cat + '?page=' + str(i), products)

                    # if we already counted these, we need to remove duplicates
                    if firstPage and products[-40:] == products[-20:] + products[-20:]:
                        products = products[:-20]
                    firstPage = False

                    print(i, len(products))

            else:
                pages = 0

                # scraping the first page of a category
                products, pages = scrape("https://www.cvs.com/shop/" + cat + "?page=1", products, True)
                # if we already counted these, we need to remove duplicates
                if firstPage and products[-40:] == products[-20:] + products[-20:]:
                    products = products[:-20]
                firstPage = False

                # scraping all other pages
                for i in range(2, pages + 1):
                    products = scrape('https://www.cvs.com/shop/' + cat + '?page=' + str(i), products)
                    print(i, len(products))


    # store all the URLs when completed
    f = open('output.txt', 'w')
    print('completed', file = f)
    for item in list(set(products)):
        print(item, file = f)

except:
    # mark what place we quit at and store all URLs in output
    f = open('output.txt', 'w')
    print(cat, i-1, file = f)
    for item in products:
        print(item, file = f)
    f.close()
    quit()
