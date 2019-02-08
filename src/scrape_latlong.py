from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from bs4 import BeautifulSoup
import pandas as pd
import re

# if __name__ == '__main__':

options=Options()
options.add_argument('--headless')
driver = webdriver.Chrome(chrome_options=options)

trail_dat=pd.read_pickle('../data/alltrails_ontario_curated.pkl')
trail_names = trail_dat['name']
# for n in trail_names:
#     n1 = re.sub(r'[^A-Za-z ]','', n)
#     n1 = n1.lower()
#     n1 = n1.replace('closed', '')
#     n1 = n1.replace('private property', '')
#     n1 = n1.replace(' +', ' ')
#     n1 = (n1.strip()).replace(' ', '-')
#     print (n1)

with open ('trail_names_curated_url', 'r') as f:
    lines =[line for line in f]

# print (len(lines), lines[0])
gps_coords=[]

for l in lines:
#     tn=(n.strip()).replace(" +", '-')
#     print (tn,'\t', n)

    l1= str('https://www.alltrails.com/explore/trail/canada/ontario/')
    # tname = str('centennial-ridges-trail')
    flink = l1 + str(l)
    # print (flink)

    driver.get(flink)
    soup = BeautifulSoup(driver.page_source, 'lxml')
    header = soup.find('div', id='main')

    latitude = soup.find('meta', property = 'place:location:latitude')
    longitude = soup.find('meta', property = 'place:location:longitude')
    if (latitude != '' or latitude != None):
        print (l.strip(), [float(latitude['content']), float(longitude['content'])])
    else:
        print (l.strip(), "***CHECK TRAIL NAME***")
    # print ([latitude, longitude])

    # gps_coords.append([latitude, longitude])

    # lat.append(latitude)
    # lng.append(longitude)
    #
    # print (latitude['content'], longitude['content'])

# print (gps_coords)
driver.quit()
