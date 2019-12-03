from bs4 import BeautifulSoup, SoupStrainer
import requests
import urllib.request


url = "https://www.cvs.com/shop/vitamins?page=1"
response = requests.get(url, timeout = 5)
# resp = urllib.request.urlopen(url)
content = BeautifulSoup(response.content, "html.parser")


items = []

items = content.findAll('a', href=True)
realItems = []
for i in items:
    if 'prodid' in i['href'] and not 'reviews' in i['href']:
        realItems.append(i['href'])
    print(i['href'])

print('\n'.join(realItems))
print(len(realItems))

'''soup = BeautifulSoup(resp, from_encoding=resp.info().get_param('charset'), features='lxml')

realItems = []

for link in soup.find_all('a', href=True):
    if 'prodid' in link['href'] and not 'reviews' in link['href']:
        realItems.append(link['href'])
'''
