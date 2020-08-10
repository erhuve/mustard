import pyrebase
import threading
from selenium import webdriver
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
from selenium.common.exceptions import TimeoutException
import requests
import time
import json
import os
import numpy as np

config = {
        "apiKey": "AIzaSyAiBxG429FT-kZj9tjpAjHlcIo6CDXed7s",
        "authDomain": "mustard-cba34.firebaseapp.com",
        "databaseURL": "https://mustard-cba34.firebaseio.com",
        "projectId": "mustard-cba34",
        "storageBucket": "mustard-cba34.appspot.com",
        "messagingSenderId": "445402188887",
        "appId": "1:445402188887:web:55ea85d4e7ab506a036712",
        "measurementId": "G-S34T7N2NN7"
}

firebase = pyrebase.initialize_app(config)

db = firebase.database()

def read_data(link, driver):   
    driver.get(link)
    time.sleep(3)
    expand = driver.find_element_by_xpath('//*[@id="school"]/div[2]/div/button[1]/span')
    expand.click()
    time.sleep(2)
    college = {}
    college['name'] = driver.find_element_by_xpath('//*[@id="school"]/div[1]/div[2]/div[1]/h1').text

    college['degree'] = driver.find_element_by_xpath('//*[@id="school"]/div[1]/div[2]/div[1]/div/ul/li[1]/span').text
    college['public'] = driver.find_element_by_xpath('//*[@id="school"]/div[1]/div[2]/div[1]/div/ul/li[2]/span').text
    college['location_type'] = driver.find_element_by_xpath('//*[@id="school"]/div[1]/div[2]/div[1]/div/ul/li[3]/span').text
    college['size'] = driver.find_element_by_xpath('//*[@id="school"]/div[1]/div[2]/div[1]/div/ul/li[4]/span').text
    low_salary = driver.find_elements_by_xpath('//*[@id="school-salary-after-complete"]/div/div/div/div/span[4]/span')
    high_salary = driver.find_elements_by_xpath('//*[@id="school-salary-after-complete"]/div/div/div/div/span[6]/span')
    salary = 0
    hits = 0

    if len(low_salary) != 0:
        low_salary_ = low_salary[0].text
        low_salary_ = low_salary_.replace('$','')
        low_salary_ = low_salary_.replace(',','')
        salary += int(low_salary_)
        hits += 1

    if len(high_salary) != 0:
        high_salary_ = high_salary[0].text
        high_salary_ = high_salary_.replace('$','')
        high_salary_ = high_salary_.replace(',','')
        salary += int(high_salary_)
        hits += 1

    if salary > 0:
        salary /= hits

    college['salary'] = salary

    cost = driver.find_elements_by_xpath('//*[@id="school-avg-cost"]/h2[2]')
    if len(cost) > 0:
        cost[0] = cost[0].text
        cost[0] = cost[0].replace('$','')
        cost[0] = cost[0].replace(',','')
        college['avg_cost'] = int(cost[0])
    else:
        college['avg_cost'] = cost
    college['fields'] = driver.find_elements_by_class_name('pa-2')
    for i, field in enumerate(college['fields']):
        college['fields'][i] = field.text

    # 1-9 percentages for diversity
    diversity = []
    for i in range(1, 10):
        xpath = '//*[@id="demographics-content"]/div/div[2]/div[2]/div[' + str(i) + ']'
        percentage = driver.find_element_by_xpath(xpath).text
        real_percentage = ''
        for char in percentage:
            if char == '%':
                break
            real_percentage += char
        diversity.append(int(real_percentage))
    #driver.close()
    college['diversity'] = diversity
    if not db.child("colleges").child(college['name']).shallow().get().val():
        db.child("colleges").child(college['name']).push(college)
    #return college

#q = Queue()



def scrapeCollegeData(links, DRIVER_PATH = "chromedriver"):
    chrome_options = webdriver.ChromeOptions()
    chrome_options.binary_location = os.environ.get("GOOGLE_CHROME_BIN")
    chrome_options.add_argument("--headless")
    chrome_options.add_argument("--disable-dev-shm-usage")
    chrome_options.add_argument("--no-sandbox")
    driver = webdriver.Chrome(executable_path = DRIVER_PATH)
    for link in links:
        try:
            read_data(link, driver)
        except:
            continue


listLinks = []
with open('links.json') as json_file:
    links = json.load(json_file)
names = links.keys()
for name in names:
    listLinks.append(links[name])

listLinks = np.array(listLinks)

splitLinks = np.array_split(listLinks, 8)
print(f"Length of splitLinks is {len(splitLinks)}")
start = time.time()
for linksList in splitLinks:
    t = threading.Thread(target = scrapeCollegeData, args = [linksList])
    t.start()
elapsedTime = time.time() - start
print(f"This took {elapsedTime} seconds")
#print(f"First element is {listLinks[0]} and length of list is {len(listLinks)} and its type is {type(str(listLinks[0]))} and the list type is {type(listLinks)}")
