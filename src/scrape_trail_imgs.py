from selenium import webdriver
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support import expected_conditions as EC
from bs4 import BeautifulSoup
from pymongo import MongoClient
import time
import pickle
import pandas as pd
import urllib
import requests
import lxml
import re

if __name__ == '__main__':

    options=Options()
    options.add_argument('--headless')
    driver = webdriver.Chrome(chrome_options=options)

    l1= str('https://www.alltrails.com/explore/trail/canada/ontario/')
    tname = str('centennial-ridges-trail')
    flink = l1+tname #+l2

    # driver.get('https://www.alltrails.com/explore/trail/canada/ontario/centennial-ridges-trail?ref=sidebar-static-map')
    driver.get(flink)
    soup = BeautifulSoup(driver.page_source, 'lxml')
    header = soup.find('div', id='main')
    # print (soup.encode("utf-8"))

    # latitude = re.search('meta content=\"(.+?)\" property=\"place:location:latitude\"/>', soup)
    # longitude = re.search('<meta content=\"(.+?)\" property=\"place:location:longitude\"', soup)

    latitude = soup.find('meta', property = 'place:location:latitude')
    longitude = soup.find('meta', property = 'place:location:longitude')

    print (latitude['content'], longitude['content'])

    # latitude = soup.find(itemprop='lat').get_text()
    # longitude = soup.find(itemprop='longitude').get_text()
    # print (latitude, longitude)

    # trail_img = driver.save_screenshot('../img/trail_img.png')
    driver.quit()
