"""

Script to routinely run to maintain the data being scrapped.

Author: Pranav Sekhar
Date: 7th September,2022
"""
import math
import os

import pandas as pd
from collections import  defaultdict
import regex as re
from datetime import datetime
from matplotlib.colors import is_color_like

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
    x = []
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
            x.append(spec.strip().lower())
    article_dict[counter]["Meta data"] = ','.join(x)
    article_dict[counter]['Price'] = price
    hours = datetime.strptime(time, "%H:%M:%S")
    rounded_tm = f"{hours.hour}:30:00"
    article_dict[counter]["Date"] = date
    article_dict[counter]["Time"] = rounded_tm


def clean_processors(dirty_proc_df: pd.DataFrame):
    """

    :param dirty_proc_df: dirty dataframe having different values for processor, cleaning to introduce a structure
    :return: structure dataframe along processor column [Intel, Amd, None]
    """
    dirty_proc_df['Processor Name'] = 'None'
    dirty_proc_df['Processor Chip'] = 'None'
    dirty_proc_df['Processor Chip Detail'] = "None"
    dirty_proc_df['Processor'].fillna("None", inplace= True)
    for processor in list(dirty_proc_df['Processor'].unique()):
        if re.search('(intel)|(i[3,5,7,9])', processor):
            dirty_proc_df.loc[dirty_proc_df['Processor'] == processor, 'Processor Name'] = "Intel"
            if re.search('(i[3,5,7,9])|(celeron)', processor):
                x = re.search('(i[3,5,7,9])|(celeron)', processor)
                i = processor[x.start():x.end()]
                chip = processor.replace('intel', '')
                chip = chip.replace('core', '')
                chip = chip.replace('16gb', '')
                chip = chip.replace('ddr4', '')
                chip = chip.replace('ddr5', '')
                chip = chip.replace('8gb', '')
                chip = chip.replace('memory', '')
                chip = " ".join(chip.split())
                dirty_proc_df.loc[dirty_proc_df['Processor'] == processor, 'Processor Chip'] = i
                dirty_proc_df.loc[dirty_proc_df['Processor'] == processor, 'Processor Chip Detail'] = chip.strip()
        elif re.search('(amd)|(r[3,5,7,9])|(ryzen)', processor.lower()):
            if re.search('(r[3,5,7,9])|(ryzen [1,2,3,4,5,6,7,8,9,10])', processor.lower()):
                dirty_proc_df.loc[dirty_proc_df['Processor'] == processor, 'Processor Name'] = "AMD"
                x = re.search('(r[3,5,7,9])|(ryzen [1,2,3,4,5,6,7,8,9,10])', processor.lower())
                a = processor[x.start():x.end()]
                a = a.replace("r7", "ryzen 7")
                a = a.replace("r9", "ryzen 9")
                chip = processor.lower().replace('amd', '')
                chip = chip.replace('core', '')
                chip = chip.replace('16gb', '')
                chip = chip.replace('ddr4', '')
                chip = chip.replace('ddr5', '')
                chip = chip.replace('8gb', '')
                chip = chip.replace('memory', '')
                chip = chip.replace('r', '')
                chip = chip.replace('yzen', 'ryzen')
                chip = " ".join(chip.split())
                dirty_proc_df.loc[dirty_proc_df['Processor'] == processor, 'Processor Chip'] = a
                dirty_proc_df.loc[dirty_proc_df['Processor'] == processor, 'Processor Chip Detail'] = chip.strip()
    dirty_proc_df.drop('Processor', axis=1, inplace= True)
    return dirty_proc_df


def clean_ram(dirty_ram_df: pd.DataFrame):
    """

    :param dirty_df: Initial ram dataframe that needs to be cleaned to introduce structure to the RAM column
    :return: clean RAM column with
    """
    dirty_ram_df['RAM storage'] = 'None'
    dirty_ram_df['RAM detail'] = 'None'
    dirty_ram_df['RAM'].fillna("None", inplace=True)
    for ram in list(dirty_ram_df['RAM'].unique()):
        if re.search('(4gb)|(8gb)|(16gb)|(32gb)|(64gb)', ram.lower()):
            x = re.search('(4gb)|(8gb)|(16gb)|(32gb)|(64gb)', ram.lower())
            storage = ram[x.start():x.end()]
            dirty_ram_df.loc[dirty_ram_df['RAM'] == ram, 'RAM storage'] = storage
        if re.search('ddr', ram.lower()):
            result = list(filter(lambda x: re.search('ddr', x), ram.split(' ')))
            dirty_ram_df.loc[dirty_ram_df['RAM'] == ram, 'RAM detail'] = " ".join(result)
    dirty_ram_df.drop('RAM', axis=1, inplace=True)
    return dirty_ram_df


def clean_graphic_card(dirty_graphic_df: pd.DataFrame):
    """

    :param dirty_graphic_df:
    :return: structured graphic card dataframe column
    """
    dirty_graphic_df['GPU card'] = 'None'
    dirty_graphic_df['GPU card detail'] = 'None'
    dirty_graphic_df['Graphic card'].fillna("None", inplace=True)
    for card in list(dirty_graphic_df['Graphic card'].unique()):
        if re.search('(nvidia)|(geforce)', card):
            dirty_graphic_df.loc[dirty_graphic_df['Graphic card'] == card, 'GPU card'] = 'Nvidia'
            card_cl = card.replace('geforce', '')
            card_cl = card_cl.replace('nvidia', '')
            card_cl = card_cl.replace('graphics', '')
            card_cl = card_cl.replace('gpu', '')
            card_cl = card_cl.replace('laptop', '')
            dirty_graphic_df.loc[dirty_graphic_df['Graphic card'] == card, 'GPU card detail'] = card_cl.strip()
    dirty_graphic_df.drop('Graphic card', axis=1, inplace=True)
    return dirty_graphic_df


def return_string( string_tc: str, subst: str):
    str_list = string_tc.split(' ')
    for string in str_list:
        if re.search(subst, string):
            return string
        if subst == '"':
            if re.search('[0-9]\'\'', string):
                return string.replace("\'\'", '"')
    return False


def check_color( str_tc: str):
    str_list = str_tc.split(' ')
    for string in str_list:
        if is_color_like(string):
            if string != "1":
                return str_tc
    return False


def clean_metadata(dirty_meta_df: pd.DataFrame):
    dirty_meta_df['Color'] = 'NA'
    dirty_meta_df['Model name'] = 'None'
    dirty_meta_df['Screen size'] = 'None'
    dirty_meta_df['Screen Refresh rate'] = 'None'
    for met in list(dirty_meta_df['Meta data'].unique()):
        model = []
        split_met = met.split(',')
        for part in split_met:
            part_ref = part.replace('laptop', '')
            part_ref = part_ref.replace('gaming', '')
            part_ref = part_ref.replace('touchscreen', '')
            part_ref = part_ref.replace('multifunctional', '')
            if re.search('|'.join(companies), part_ref.strip().lower()):
                x = re.search('|'.join(companies), part_ref.strip().lower())
                part_ref = part_ref.replace(part_ref[x.start(): x.end()], '')
            ssize = return_string(part_ref, '"')
            if ssize:
                dirty_meta_df.loc[dirty_meta_df['Meta data'] == met, 'Screen size'] = ssize.strip()
                part_ref = part_ref.replace(ssize, '')
            sfreq = return_string(part_ref, 'hz')
            if sfreq:
                dirty_meta_df.loc[dirty_meta_df['Meta data'] == met, 'Screen Refresh rate'] = sfreq.strip()
                part_ref = part_ref.replace(sfreq, '')
            scolor = check_color(part_ref)
            if scolor:
                dirty_meta_df.loc[dirty_meta_df['Meta data'] == met, 'Color'] = scolor.strip()
                part_ref = part_ref.replace(scolor, '')
            model.append(part_ref)
        model_str = ''.join(model)
        if len(model_str) > 1:
            dirty_meta_df.loc[dirty_meta_df['Meta data'] == met, 'Model name'] = model_str.strip()

    return  dirty_meta_df




df = pd.DataFrame.from_dict(article_dict, orient="index")
df['Date'] = pd.to_datetime(df['Date'], format='%d/%m/%Y').dt.strftime('%m/%d/%Y')
df.drop_duplicates(subset=['Company Name', 'Processor', 'RAM', 'Graphic card','Hard disk', 'Price', 'Date', 'Time'], inplace=True)
cleaned_df = clean_processors(df.copy())
cleaned_df = clean_ram(cleaned_df.copy())
cleaned_df = clean_graphic_card(cleaned_df.copy())
cleaned_df = clean_metadata(cleaned_df.copy())
cleaned_df.to_csv(f"{os.getcwd()}/maintenance.csv")




