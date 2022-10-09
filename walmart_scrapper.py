"""

Trial code for a web scraper

Author: Pranav Sekhar
Date: 30th August 2022
"""
import os

import pandas as pd
import requests
from bs4 import BeautifulSoup
from datetime import datetime
from selenium import webdriver
from bs4 import BeautifulSoup
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.keys import Keys
import time

# --| Setup
options = webdriver.ChromeOptions()
#options.add_argument("headless")
browser = webdriver.Chrome(executable_path=r'/Users/pranavsekhar/Downloads/chromedriver', options=options)
# --| Parse or automation
browser.get('https://www.walmart.com/search?q=laptop&typeahead=laptop')
soup = BeautifulSoup(browser.page_source, 'lxml')
#print(soup.prettify())
browser.implicitly_wait(5)

for item in soup.find_all('div', class_='mb1 ph1 pa0-xl bb b--near-white w-25'):
    print(item.a.text)
exit()

def getting_data(soup):
    #print(soup.prettify())
    time_ = datetime.now()
    df1 = pd.DataFrame(columns = ['Product Title', 'Price', 'Date', 'Time'])
    print(soup.find('div'))
    exit()
    for section in soup.find_all('div', class_='mb1 ph1 pa0-xl bb b--near-white w-25'):
        print(section)
        exit()
        product_title = section.find('div', class_='information').find('h4', class_='sku-title').a.text
        product_price = section.find('div', class_='price-block').find('div',
                                                                       class_='priceView-hero-price priceView-customer-price').find(
            'span').text
        temp_df = pd.DataFrame([[product_title, float(product_price[1:].replace(',', '')), f"{time_.day}/{time_.month}/{time_.year}", f"{time_.hour}:{time_.minute}:{time_.second}"]], columns=['Product Title', 'Price', 'Date','Time'])
        df1 = pd.concat([df1, temp_df], ignore_index=True, axis=0)
    return df1

def get_next_link(soup):
    next_link = soup.find('div', class_='footer-pagination').find('a', class_='sku-list-page-next')['href']
    next_url = "https://www.bestbuy.com" + next_link
    return next_url

if __name__ == '__main__':
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/78.0.3904.108 Safari/537.36",
        "Accept-Encoding": "gzip, deflate", "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
        "DNT": "1", "Connection": "close", "Upgrade-Insecure-Requests": "1"}
    print("Sending request to site")
    page = requests.get(
        'https://www.walmart.com/search?q=laptop&typeahead=laptop',
        headers={
            "User-Agent": "Mozilla/5.0 (X11; CrOS x86_64 12871.102.0) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/81.0.4044.141 Safari/537.36"})
    print("received data, making soup...")
    print(page.status_code)
    soup = BeautifulSoup(page.content, 'lxml')
    counter = -1
    aggregated_df = pd.read_csv(f'/Users/pranavsekhar/PycharmProjects/Chipper/output.csv')
    while counter <4:
        counter +=1
        aggregated_df= pd.concat([aggregated_df,getting_data(soup)])
        next_url = get_next_link(soup)
        page = requests.get(
            next_url,
            headers={
                "User-Agent": "Mozilla/5.0 (X11; CrOS x86_64 12871.102.0) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/81.0.4044.141 Safari/537.36"})
        print("received data, making soup...")
        soup = BeautifulSoup(page.content, 'lxml')
    #aggregated_df.drop(aggregated_df.columns.difference(['Product Title', 'Price', 'Date', 'Time']), inplace=True, axis=1)
    aggregated_df.reset_index(inplace=True)
    aggregated_df.drop(aggregated_df.columns.difference(['Product Title', 'Price', 'Date', 'Time']), inplace=True, axis=1)
    aggregated_df.to_csv(f'/Users/pranavsekhar/PycharmProjects/Chipper/output.csv')

