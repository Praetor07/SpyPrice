"""

Script to routinely run to maintain the data being scrapped.

Author: Pranav Sekhar
Date: 7th September,2022
"""
import os

import pandas as pd
from collections import  defaultdict
import regex as re
from datetime import datetime

pd.set_option('display.max_columns', None)

l = 'MSI - Delta 15.6" FHD 240hz Gaming Laptop - Ryzen R7-5800 - Radeon RX6700M - 1TB SSD - 16GB Memory - Black'
search = re.search(r'[0-9]-[0-9]', l)
l = l[:int(search.start())+1] + " " + l[int(search.start())+2:]



dirty_df_init = pd.read_csv("/Users/pranavsekhar/PycharmProjects/Chipper/output.csv")
dirty_df = dirty_df_init[['Product Title', 'Price', 'Date', 'Time']]

processor_terms = ["i7", "intel", "amd", "i5", "i9", "ryzen"]
companies = ["dell", "hp", "asus", "razer", "gigabyte", "acer", "msi" ,"lenovo", "alienware","corsair","adata"]
counter = 0
#print(dirty_df.columns)
article_dict = defaultdict(dict)
tst_counter = 0
#print(dirty_df.loc[dirty_df['Product Title'] == 'GIGABYTE AORUS 17.3"" FHD Laptop -Intel i9-12900H - 32GB DDR5 - NVIDIA Geforce RTX 3080 Ti - 1TB SSD'])
for index, row in dirty_df.iterrows():
    laptop = row[0]
    price = row[1]
    date = row[2]
    time = row[3]
    counter += 1
    search = re.search(r'[0-9]-[0-9]', laptop)
    laptop_ind = laptop[:int(search.start())+1] + " " + laptop[int(search.start())+2:] if search else laptop
    laptop_ind = laptop_ind.replace("2-in-1", "multifunctional")
    detail_list = re.split("-|–", laptop_ind)
    for spec in detail_list:
        if re.search('|'.join(companies), spec.strip().lower()):
            index = re.search('|'.join(companies), spec.strip().lower())
            article_dict[counter]['Company Name'] = spec.strip().lower()[int(index.start()):int(index.end()+1)]
            article_dict[counter]["Meta data"] = article_dict.get(counter, {}).get('Meta data', []) + [spec.strip().lower()]
        elif re.search(r"(ryzen)|(intel)|(i5)|(i7)|(i9)|(i3)",spec.strip().lower()):
            article_dict[counter]['Processor'] = spec.strip().lower()
        elif re.search(r"(memory)|(ddr5)|(ddr4)", spec.strip().lower()):
            article_dict[counter]["RAM"] = spec.strip().lower()
        elif re.search(r"(hdd)|(ssd)",spec.strip().lower()):
            article_dict[counter]['Hard disk'] = spec.strip().lower()
        elif re.search(r"(raedeon)|(rtx)|(gtx)", spec.strip().lower()):
            article_dict[counter]["Graphic card"] = spec.strip().lower()
        else:
            #print(article_dict[counter])
            article_dict[counter]["Meta data"] = article_dict.get(counter, {}).get('Meta data', []) + [spec.strip().lower()]
    article_dict[counter]['Price'] = price
    hours = datetime.strptime(time, "%H:%M:%S")
    rounded_tm = f"{hours.hour}:30:00"
    article_dict[counter]["Date"] = date
    article_dict[counter]["Time"] = rounded_tm

df = pd.DataFrame.from_dict(article_dict, orient="index")
df['Date'] = pd.to_datetime(df['Date'], format='%d/%m/%Y').dt.strftime('%m/%d/%Y')
df.drop_duplicates(subset=['Company Name', 'Processor', 'RAM', 'Graphic card','Hard disk', 'Price', 'Date', 'Time'], inplace=True)
df.to_csv(f"{os.getcwd()}/maintenance.csv")




