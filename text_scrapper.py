import pandas as pd
import numpy as np 
import re
import requests

from bs4 import BeautifulSoup
import bs4
from bs4 import BeautifulSoup, element, Tag

from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager


### WEBSCRAPING ###
### THE FOLLOWING TWO CLASSES ARE ESSENTIALLY A TOOLKIT TO SCRAPE THE EDGAR REPORTS ###
### AND DOWNLOAD AND STORE THE TEXT, THE SOURCE HTML AND TABLES PRESENT IN THE DOCUMENT ###


# class TextDownload


# ATRIBUTTES:
# 1. url: the URL for the specific document we want to scrape
# 2. agent_email: the SEC website blocks bots which are not identified, so an agent name and email are required to scrape the document



# METHODS AND THEIR ARGUMENTS:
# 1. extractText: scrapes the text in the file and saves it as a txt file. 
# - text_file_name: the file name we want to give to the downloaded text
# - sep: the in between lines separation used in the file, usually \n
# Note: in the main.py script we use extractText in a separate function where we specifcy a full folder path, not just file name


# 2. extractHTML: downloads the html source of the page
# - html_file_name: the file name we want to give to the downloaded html
# Note: in the main.py script we use extractText in a separate function where we specifcy a full folder path, not just file name


# 3. find_word_in_website: finds specific keywords we want to search inside the document
# - url: the URL for the specific document we want to scrape
# - word: the word we are looking for
# Note: in the main.py script we use extractText in a separate function where we specifcy a full folder path, not just file name


class TextDownload:


    def __init__(self, url=None, agent_email=None):
        self.url = url
        self.agent_email = agent_email



    def extractText(self, text_file_name: str, sep = None) -> None:

        headers = {
            "User-Agent": "My User Agent",
            "From": f"{self.agent_email}" 
        }

        response = requests.get(self.url,  headers = headers)
        html_content = response.content

        soup = BeautifulSoup(html_content, "html.parser")

        if sep:
            text = soup.get_text(separator = sep)
        
        else:
            text = soup.get_text() 

        with open(f"{text_file_name}", "w", encoding='utf-8') as file:
            file.write(text)
            print(f"txt content saved to {text_file_name}")
    


    def extractHTML(self, html_file_name: str) -> None:
        service = Service(ChromeDriverManager().install())
        driver = webdriver.Chrome(service=service)
        
        driver.get(self.url)
        html = driver.page_source
        driver.quit()

        with open(f"{html_file_name}", "w", encoding="utf-8") as file:
            file.write(html)
            print(f"HTML content saved to {html_file_name}")
    


    def find_word_in_website(self, url: str, word:str) -> list[str]:
        headers = {
            "User-Agent": "My User Agent",
            "From": f"{self.agent_email}"}
        response = requests.get(url, headers = headers)
        if response.status_code == 200:
            soup = BeautifulSoup(response.content, 'html.parser')
            occurrences = soup.body.find_all(string=lambda text: word.lower() in text.lower())
            return occurrences
        else:
            print("Failed to fetch the website:", response.status_code)
            return []
        


# class TableDownload

# ATTRIBUTES:
# 1. url: the URL for the specific document we want to scrape
# 2. agent_email: the SEC website blocks bots which are not identified, so an agent name and email are required to scrape the document


# METHODS AND THEIR ARGUMENTS:
# 1. getTableSource: obtains the source html code for the tables found in the document
# - only takes self
        

# 2. tableCleaner: cleans the table from special characters 
# - table_source: input must be the html code of the tables we want to clean
# Note: use getTableSource to return the source code, which returns an iterable of tables, and use elements of that iterable as an input for tableCleaner
        

# 3. getTables: uses the source html code for the tables and the helper function tableCleaner to return a list of clean pd.DataFrame with the content of the tables
# - html_tables: the aforementioned source code for the html tables (the output of getTableSource)
# Returns a list of pd.DataFrame
       
        
# 4. findTOC: searches through a list of dataframes and finds the one which is the Table of Contents
# - tables: a list of pd.DataFrame. Usually would be the output of getTables, which is a cleaned list of the tables in the document


class TableDownload:

    def __init__(self, url=None, agent_email=None):
        self.url = url
        self.agent_email = agent_email

    
    def getTableSource(self) -> bs4.element.ResultSet:
        headers = {
            "User-Agent": "My User Agent",
            "From": f"{self.agent_email}" 
        }

        response = requests.get(self.url,  headers = headers)
        soup = BeautifulSoup(response.text, "xml")
        tables = soup.find_all("table")

        return tables



    def tableCleaner(self, table_source: bs4.element.Tag) -> pd.DataFrame:
        
        rows = []
        for i in range(2, len(table_source.find_all("tr"))):

            row = []
            for j in range(0, len(table_source.find_all("tr")[i].find_all("td"))):

                string = table_source.find_all("tr")[i].find_all("td")[j].text.strip()
                cleaned_string = re.sub(r'[^a-zA-Z0-9]', '', string).lower()

                if cleaned_string:
                    row.append(table_source.find_all("tr")[i].find_all("td")[j].text.strip())
                
            rows.append(row)
        
        return pd.DataFrame(rows)
    

    def getTables(self, html_tables : bs4.element.ResultSet) -> list[pd.DataFrame]:
        dfs: list[pd.DataFrame] = []
        for df in html_tables:
            data: pd.DataFrame = self.tableCleaner(df)
            dfs.append(data)
        
        return [df for df in dfs if not df.empty]
    
    
    def findTOC(self, tables: list[pd.DataFrame]) -> pd.DataFrame:
        for df in tables:
            keywords = df.apply(lambda row: row.astype(str).str.contains("Item 1").any() and row.astype(str).str.contains("Risk Factors").any(), axis = 1)
            if not df[keywords].empty:
                df.columns = ["item", "section", "page"]
                return df
            else:
                print("Table of Contents not found")
                return pd.DataFrame()