from selenium import webdriver
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support import expected_conditions as EC
from bs4 import BeautifulSoup
from pymongo import MongoClient
import time
import pickle
import pandas as pd
import urllib
import requests
import lxml

def login(driver):
    driver.get('https://www.alltrails.com/login?ref=header#')
    driver.find_element_by_id('user_email').send_keys('coolavidhiker@gmail.com')
    driver.find_element_by_id('user_password').send_keys('live<3hike')
    login=driver.find_element_by_class_name('login')
    login.click()

def get_all_hikes(driver):
    login(driver)
    driver.get('https://www.alltrails.com/canada/ontario?ref=search')
    while True:
        try:
            load_more_hikes = WebDriverWait(driver, 20).until(EC.visibility_of_element_located((By.XPATH,"//div[@id='load_more'] [@class='feed-item load-more trail-load'][//a]")))
            load_more_hikes.click()
            time.sleep(7)
        except:
            break
    soup = BeautifulSoup(driver.page_source, 'lxml')
    return soup

if __name__ == '__main__':

    driver = webdriver.Chrome()
    # login(driver)
    driver.get('https://www.alltrails.com/explore/trail/canada/ontario/centennial-ridges-trail?ref=sidebar-static-map')
    soup = BeautifulSoup(driver.page_source, 'lxml')
    header = soup.find('div', id='main')

    latitude = soup.find(itemprop='latitude').get_text()
    longitude = soup.find(itemprop='longitude').get_text()
    print (latitude, longitude)

    # trail_img = driver.save_screenshot('../img/trail_img.png')
    driver.quit()
