# -*- coding: utf-8 -*-
"""
Created on Sun Mar  2 23:28:09 2025

@author: Artik

News Scraper
"""


import requests
from bs4 import BeautifulSoup
import pandas as pd
import json
import os
import re

#function to create a url for websearch having search query and date filters
def create_google_news_url(query, start_date, end_date):
    base_url = "https://www.google.com/search"
    params = {
        "q": query.replace(" ", "+"),  # Replace spaces with '+' for the query
        "tbm": "nws", # News tab
        "tbs": f"cdr:1,cd_min:{start_date},cd_max:{end_date}", # Date range
        "num": 20       
    }
    query_string = "&".join([f"{key}={value}" for key, value in params.items()])
    return f"{base_url}?{query_string}"


#function to fetch news headlines and their url
def fetch_news_headlines_and_urls(query, start_date, end_date):
    # Headers to mimic a browser
    headers = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
                  "(KHTML, like Gecko) Chrome/114.0.0.0 Safari/537.36 Edg/114.0.1823.67",
    "Accept-Language": "en-US,en;q=0.9",
    "Accept-Encoding": "gzip, deflate, br",
    "Connection": "keep-alive",
    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8"
    }

    # Send GET request
    response = requests.get(create_google_news_url(query, start_date, end_date), headers=headers)
    # Check if request is successful
    if response.status_code == 200:
        soup = BeautifulSoup(response.text, "html.parser")
 
        # Extract headlines and URLs
        data = []
        articles = soup.find_all("div", class_="SoaBEf")
        for article in articles:
            headline = article.find("div", class_="n0jPhd ynAwRc MBeuO nDgy9d")
            date = article.find("div", class_="OSrXXb rbYSKb LfVVr")
            link_tag = article.find("a")
            site_name =  article.find("div", class_="MgUUmf NUnG9d")
  
            #adding data to a list
            data.append({
                "Headline": headline.text if headline else "Not found",
                "Publication Date": date.text if date else "Not found",
                "Link": link_tag.get("href") if link_tag else "Not found",
                "News Site Name": site_name.text if site_name else "Not found"})

        # Create DataFrame
        news_data = pd.DataFrame(data)
        return news_data
    else:
        print(f"Failed to fetch page, status code: {response.status_code}")
        return []
    

def article_preprocessing(article_text):
    def remove_short_sentences(text, min_words=3):
        reg = r'(?<=[.!?])\s+|\n'
        sentences = re.split(reg, text)  # Split based on punctuation
        filtered_sentences = [sentence for sentence in sentences if len(sentence.split()) >= min_words][:15]
        snt  = ' '.join(filtered_sentences)
        final = re.sub(r'\\u', r'', snt )
        return final
    return remove_short_sentences(article_text)


def article_scraper(link): #scrape articles from web
    try:
        # Send a request to fetch the webpage content
        # Headers to mimic a browser
        headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
                      "(KHTML, like Gecko) Chrome/114.0.0.0 Safari/537.36 Edg/114.0.1823.67",
        "Accept-Language": "en-US,en;q=0.9",
        "Accept-Encoding": "gzip, deflate, br",
        "Connection": "keep-alive",
        "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8"
        }
        
        response = requests.get(link, headers=headers)
        response.raise_for_status()  # Raise error for bad responses
        
        # Parse the HTML content
        soup = BeautifulSoup(response.text, "html.parser")
        
        # Extract the text from paragraphs
        paragraphs = soup.find_all("p")
        article_text = "\n".join([p.get_text() for p in paragraphs if p.get_text().strip()])
        
        article_text_cleaned = article_preprocessing(article_text)
        
        return article_text_cleaned if article_text_cleaned else "No article content found."
    
    except requests.exceptions.RequestException as e:
        return f"Error fetching the article: {e}"



def article_saver(news_results_dated): #save artilces in json files
    path = r"D:\Codes\Algo Trade\News Headline"  # Path to save files
    filename = os.path.join(path, f"{news_results_dated.iloc[0]['Publication Date']}.json")  # Use first row's date for filename
    print(filename)
    articles = [] 
    
    # Delete existing file if the file exists
    if os.path.exists(filename):
        os.remove(filename)
    
    # Iterate through DataFrame rows
    for _, row in news_results_dated.iterrows():
        article = {
            "headline": row['Headline'],
            "date": row['Publication Date'],
            "link": row['Link'],
            "site_name": row['News Site Name']
            #"text": article_scraper(row['Link'])
            }
        articles.append(article)  
    
    # Write data to JSON file
    with open(filename, "w", encoding="utf-8") as file:
        json.dump(articles, file, indent=4)
    
    print(f"All articles saved successfully in {filename}.")

    
      
    
def article_fetcher(news_query, start_date, end_date): #filters and  fetch articles
    print("###Finding news result")
    news_results = fetch_news_headlines_and_urls(news_query, start_date, end_date)
    print("####News Result Found")
    
    #save for each date seperatly
    for date in news_results['Publication Date'].drop_duplicates().tolist():
        print("Saving article")
        article_saver(news_results.loc[news_results['Publication Date'] == date])
    

#INPUTS
news_query = "Adani Green"
start_date = "01/01/2022"



new_date = start_date

while True:
    try:
        article_fetcher(news_query, new_date, new_date)
        new_date = (pd.to_datetime(new_date, format="%m/%d/%Y") + pd.Timedelta(days=1)).strftime("%m/%d/%Y")
        
    except:
        print(new_date, "No article found or some error occurs")
        new_date = (pd.to_datetime(new_date, format="%m/%d/%Y") + pd.Timedelta(days=1)).strftime("%m/%d/%Y")
        continue
    







    
