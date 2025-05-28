# -*- coding: utf-8 -*-
"""
Created on Sat Apr 26 13:26:10 2025

@author: Artik
"""

import pandas as pd
import json
import os
from datetime import datetime


loc = r'D:\Codes\Algo Trade\News Headline'

import os
import json
import pandas as pd
import re

def clean_headline(text):
    text = text.lower()  # Convert to lowercase
    text = re.sub(r'[^\w\s]', '', text)  # Remove special characters
    text = re.sub(r'\s+', ' ', text).strip()  # Remove extra spaces
    return text

file_name = []
for file in os.listdir(loc):
    file_name.append(file)

articles = pd.DataFrame(columns=['Date', 'Headline', 'Site_Name'])

for file in file_name:
    with open(os.path.join(loc, file), "r", encoding="utf-8") as file:
        data = json.load(file)  # Parse the JSON content
        for i in data:
            cleaned_headline = clean_headline(i['headline'])
            articles.loc[len(articles)] = [i['date'], cleaned_headline, i['site_name']]

articles['Date'] = pd.to_datetime(articles['Date'], format='mixed')

articles = articles[articles['Headline'].str.contains('adani', case=False, na=False)]

articles.to_excel(r'D:\Codes\Algo Trade\Final Codes\news_headlines_2.xlsx', index=False)




