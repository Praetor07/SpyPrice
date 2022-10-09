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
import logging
logging.basicConfig(format='%(asctime)s - %(levelname)s.%(funcName)s:%(message)s', level=logging.INFO)

def getting_data(soup):
    logging.info("Making soup")
    time_ = datetime.now()
    df1 = pd.DataFrame(columns = ['Product Title', 'Price', 'Date', 'Time'])
    for section in soup.find_all('li', class_='sku-item'):
        product_title = section.find('div', class_='information').find('h4', class_='sku-title').a.text
        product_price = section.find('div', class_='price-block').find('div',
                                                                       class_='priceView-hero-price priceView-customer-price').find(
            'span').text
        temp_df = pd.DataFrame([[product_title, float(product_price[1:].replace(',', '')), f"{time_.day}/{time_.month}/{time_.year}", f"{time_.hour}:{time_.minute}:{time_.second}"]], columns=['Product Title', 'Price', 'Date','Time'])
        df1 = pd.concat([df1, temp_df], ignore_index=True, axis=0)
    logging.info("Soup made!! Returning dataframe after concatenating data")
    return df1

def get_next_link(soup):
    logging.info("Making the next link")
    next_link = soup.find('div', class_='footer-pagination').find('a', class_='sku-list-page-next')['href']
    next_url = "https://www.bestbuy.com" + next_link
    logging.info("Returning the next link")
    return next_url

if __name__ == '__main__':
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/78.0.3904.108 Safari/537.36",
        "Accept-Encoding": "gzip, deflate", "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
        "DNT": "1", "Connection": "close", "Upgrade-Insecure-Requests": "1"}
    logging.info("Sending request to the site")
    page = requests.get(
        'https://www.bestbuy.com/site/searchpage.jsp?st=laptop&_dyncharset=UTF-8&_dynSessConf=&id=pcat17071&type=page&sc=Global&cp=1&nrp=&sp=&qp=category_facet%3DSAAS%7EGaming+Laptops%7Epcmcat287600050003&list=n&af=true&iht=y&usc=All+Categories&ks=960&keys=keys',
        headers={
            "User-Agent": "Mozilla/5.0 (X11; CrOS x86_64 12871.102.0) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/81.0.4044.141 Safari/537.36"})
    logging.info("received data, time to make soup...")
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
        logging.info("received data, time to make soup...")
        soup = BeautifulSoup(page.content, 'lxml')
    #aggregated_df.drop(aggregated_df.columns.difference(['Product Title', 'Price', 'Date', 'Time']), inplace=True, axis=1)
    aggregated_df.reset_index(inplace=True)
    aggregated_df.drop(aggregated_df.columns.difference(['Product Title', 'Price', 'Date', 'Time']), inplace=True, axis=1)
    aggregated_df.to_csv(f'/Users/pranavsekhar/PycharmProjects/Chipper/output.csv')
    logging.info('Written the output file - ./Chipper/output.csv')

