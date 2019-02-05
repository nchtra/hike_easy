from selenium import webdriver
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support import expected_conditions as EC
from bs4 import BeautifulSoup
from pymongo import MongoClient
import time

def login(driver):
    driver.get('https://www.alltrails.com/login?ref=header')
    driver.find_element_by_id('user_email').send_keys('coolavidhiker@gmail.com')
    driver.find_element_by_id('user_password').send_keys('live<3hike')
    login=driver.find_element_by_class_name('login')
    login.click()
    # driver.find_element_by_name("commit").click()
    # driver.find_element_by_id("search").send_keys('Milton')
    # driver.find_element_by_id("search").send_keys('Quebec')
    # driver.find_element_by_id("search").send_keys('Ontario')
    # soup, driver = get_all_hikes(driver)
    # return soup, driver

def get_all_hikes(driver):
    driver.get('https://www.alltrails.com/canada/ontario?ref=search')
    # driver.get('https://www.alltrails.com/canada/ontario/milton?ref=search')
    # driver.get('https://www.alltrails.com/canada/quebec?ref=search')
    while True:
        try:
            load_more_hikes = WebDriverWait(driver, 20).until(EC.visibility_of_element_located((By.XPATH,"//div[@id='load_more'] [@class='feed-item load-more trail-load'][//a]")))
            load_more_hikes.click()
            time.sleep(7)
        except:
            break
    soup = BeautifulSoup(driver.page_source, 'lxml')
    return soup

def get_all_ratings(driver, hike_url):
    driver.get(hike_url)
    while True:
        try:
            load_more_ratings = WebDriverWait(driver, 15).until(EC.visibility_of_element_located((By.XPATH,"//div[@id='load_more'] [@class='feed-item load-more'][//a]")))
            load_more_ratings.click()
            time.sleep(7)
        except:
            break
    soup = BeautifulSoup(driver.page_source, 'lxml')
    return soup

def parse_meta_data(hike_soup):
    header = hike_soup.find('div', id='title-and-menu-box')
    hike_name = header.findChild('h1').text
    difficulty = header.findChild('span').text
    stars = header.findChild('meta')['content']
    num_reviews = header.find('span', itemprop='reviewCount').text
    area = hike_soup.select('div.trail-rank')
    try:
        hike_region = area[0].findChild('span', itemprop='name').text
    except:
        hike_region = area[0].findChild('a').text
    # directions = header.select('li.bar-icon.trail-directions')
    try:
        distance = hike_soup.select('span.distance-icon')[0].text
    except:
        distance = None
    try:
        elevation_gain = hike_soup.select('span.elevation-icon')[0].text
    except:
        elevation_gain = None
    try:
        route_type = hike_soup.select('span.route-icon')[0].text
    except:
        route_type = None
    tags = hike_soup.select('section.tag-cloud')[0].findChildren('h3')
    hike_attributes = []
    for tag in tags:
        hike_attributes.append(tag.text)

    # map_img = hike_soup.find_element_by_id('sidebar-map')
    # print (map_img.get_attribute('src'))

    ## Get location information
    # location=hike_soup.find_element_by_id('')
    # latitude=hike_soup.

    user_ratings = []
    user_reviews=[]
    reviews_array=[]
    users = hike_soup.select('div.feed-user-content.rounded')
    for user in users:
        if user.find('span', itemprop='author') != None:
            user_name = user.find('span', itemprop='author').text
            user_name = user_name.replace('.', '')
            try:
                rating = user.find('span', itemprop="reviewRating").findChildren('meta')[0]['content']
                user_ratings.append({user_name: rating})
                # review = ((user.find('p', itemprop='reviewBody').text).encode('ascii').decode('ascii'))
                # review = (user.find('p', itemprop='reviewBody').text).encode('utf-8')
                review = user.find('p', itemprop='reviewBody').text
                if (review != None):
                    user_reviews.append({user_name: review})
                    reviews_ratings.append({user_name: review})
                else:
                    user_reviews.append({user_name: None})
                # print (">>", user_review)
            except:
                pass
    row_data = {}
    row_data['hike_name'] = hike_name
    row_data['hike_difficulty'] = difficulty
    row_data['stars'] = stars
    row_data['num_reviews'] = num_reviews
    row_data['hike_region'] = hike_region
    row_data['total_distance'] = distance
    row_data['elevation_gain'] = elevation_gain
    row_data['route_type'] = route_type
    row_data['hike_attributes'] = hike_attributes
    row_data['ratings'] = user_ratings
    row_data['reviews'] = user_reviews
    # print (row_data)
    return row_data

def create_db(soup, driver):
    hikes = soup.select('div.trail-result-card')
    for hike in hikes:
        h = hike.findChild('a')
        if h == None:
            continue
        hike_url = 'http://www.alltrails.com' + h['href']
        hike_soup = get_all_ratings(driver, hike_url)
        mongo_doc = parse_meta_data(hike_soup)
        table.insert_one(mongo_doc)


if __name__ == '__main__':
    client = MongoClient()
    # db = client['quebec_db']
    db = client['./data/Ontario_allreviews.db']
    # db = client['Milton_reviewsdb']
    # db = client['Quebec_reviewsdb']
    table = db['hikes']

    driver = webdriver.Chrome()
    login(driver)
    soup = get_all_hikes(driver)
    create_db(soup, driver)
