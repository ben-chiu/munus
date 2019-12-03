import re
from bs4 import BeautifulSoup # , SoupStrainer
import requests


url = 'https://www.cvs.com/shop/poise-ultra-thin-long-length-pads-light-absorbancy-24-ct-prodid-1730257'
response = requests.get(url, timeout = 45)
content = BeautifulSoup(response.content, 'html.parser')

y = str(content)

f = open('temp.txt', 'w')
print(y, file = f)
f.close()

find = re.search('var productData (.{0,5000})\"price\":{\"value\":\"(.{1,6})\"\,\"currencyCode\":\"USD\"}', y)

print(find.group(2))

# "price":{"value":"4.99","currencyCode":"USD"}
