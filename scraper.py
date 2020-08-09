from selenium import webdriver
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
from selenium.common.exceptions import TimeoutException
import requests
import time
import json

def scrape_links(DRIVER_PATH):

    # Webdriver path (for Selenium)
    #DRIVER_PATH = '/Users/pastel/Downloads/chromedriverReal'

    # Set up Selenium usage
    driver = webdriver.Chrome(executable_path = DRIVER_PATH)

    # Gather links for every college
    links = {}
    for page in range(292): # There are 292 pages
        URL = 'https://collegescorecard.ed.gov/search/?page=' + str(page) + '&sort=avg_net_price:desc'
        driver.get(URL)
        # Page starts with a side panel taking the screen, this part is to click away from it and give time to load
        # v-select__selections

        el = driver.find_element_by_class_name('v-select__selections')

        action = webdriver.common.action_chains.ActionChains(driver)
        action.move_to_element_with_offset(el, 300, 300)
        action.click()
        action.perform()

        time.sleep(1)

        temp_links = driver.find_elements_by_class_name('nameLink')
        for link in temp_links:
            page = link.get_attribute('href')
            name = link.text
            links[name] = page

    with open('links.json', 'w') as fi:
        json.dump(links, fi)

    driver.close()
# The following would scrape individual college data but we are forgoing this right now because that's a lot lol

# Time to visit each link and scrape data
def read_data(name, DRIVER_PATH):   
    with open('links.json') as json_file:
        data = json.load(json_file)

    link = data[name]

    driver = webdriver.Chrome(executable_path = DRIVER_PATH)
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
    college['salary'] = driver.find_elements_by_xpath('//*[@id="school-salary-after-complete"]/div/div/div/div/span[4]/span')

    for val in range(len(college['salary'])):
        college['salary'][val] = college['salary'][val].text
    for val in range(len(college['salary'])):
        if college['salary'][val] is not None:
            value = college['salary'][val]
            value = value.replace('$','')
            value = value.replace(',','')
            college['salary'][val] = int(value)
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
    driver.close()
    college['diversity'] = diversity
    return college

# DRIVER_PATH = '/Users/pastel/Downloads/chromedriverReal'
# scrape_links(DRIVER_PATH)
# college = read_data('New York University', DRIVER_PATH)
# print(college)
'''
with open('links.json') as json_file:
    links = json.load(json_file)
data = []
Will be stored in dictionaries
{
    name: [string], //*[@id="school"]/div[1]/div[2]/div[1]/h1
    degree: [string], //*[@id="school"]/div[1]/div[2]/div[1]/div/ul/li[1]/span
    public: [string], //*[@id="school"]/div[1]/div[2]/div[1]/div/ul/li[2]/span
    location_type: [string], //*[@id="school"]/div[1]/div[2]/div[1]/div/ul/li[3]/span
    size: [string], //*[@id="school"]/div[1]/div[2]/div[1]/div/ul/li[4]/span
    salary: [int,int], 
    //*[@id="school-salary-after-complete"]/div/div/div/div/span[4]/span 
    //*[@id="school-salary-after-complete"]/div/div/div/div/span[4]/span
    avg_cost: [int], //*[@id="school-avg-cost"]/h2[2]
    fields: [string,], class="pa-2"
    diversity: [int,] 
    //*[@id="demographics-content"]/div/div[2]/div[2]/div[1]/strong
    //*[@id="demographics-content"]/div/div[2]/div[2]/div[2]/strong
    //*[@id="demographics-content"]/div/div[2]/div[2]/div[9]/strong
}
'''
"""
for i, link in enumerate(links):
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
    college['salary'] = driver.find_elements_by_xpath('//*[@id="school-salary-after-complete"]/div/div/div/div/span[4]/span')
    for val in range(len(college['salary'])):
        college['salary'][val] = college['salary'][val].text
    for val in range(len(college['salary'])):
        if college['salary'][val] is not None:
            value = college['salary'][val]
            value = value.replace('$','')
            value = value.replace(',','')
            college['salary'][val] = int(value)
    cost = driver.find_element_by_xpath('//*[@id="school-avg-cost"]/h2[2]').text
    cost = cost.replace('$','')
    cost = cost.replace(',','')
    college['avg_cost'] = int(cost)
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
    college['diversity'] = diversity
    data.append(college)
    # Only capture 1000
    # if i >= 999:
    #     break
with open('data.json', 'w') as f:
    json.dump(data, f)
driver.close()
"""