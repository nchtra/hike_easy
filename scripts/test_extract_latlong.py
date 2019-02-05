# Use the google maps API.

from urllib.request import urlopen,Request
from bs4 import BeautifulSoup

# use the google map api
import json

s1='https://maps.googleapis.com/maps/api/geocode/json?address='
s2=str('hilton-tail-falls').replace('-','+')

url=s1+s2
print (url)
# print (s2)
# print (s1+s2)

# url = 'https://maps.googleapis.com/maps/api/geocode/json?address=Braman+Municipal+Utilities'
jsonurl = urlopen(url)
#
text = json.loads(jsonurl.read())
print (text)
# print ( text['results'][0]["formatted_address"])
# print ( text['results'][0]["geometry"]['location']["lat"])
# print ( text['results'][0]["geometry"]['location']["lng"])
