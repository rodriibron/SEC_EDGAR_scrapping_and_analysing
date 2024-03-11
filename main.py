

import pandas as pd
import numpy as np 
import re

# Dependencies from other scripts
from text_scrapper import TextDownload, TableDownload
from business_info import BusinessInfo, BusinessSummary
from product_industry_entities import Entities, INDUSTRY_KEYWORDS

# Webscraping packages
import requests
from bs4 import BeautifulSoup
import bs4
from bs4 import BeautifulSoup, element, Tag
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager

# NLP packages
import nltk
from nltk.corpus import stopwords
from nltk.stem import PorterStemmer
from nltk.tokenize import word_tokenize, sent_tokenize
from nltk.tag import pos_tag
from nltk.chunk import ne_chunk

# Download pre-trained models from nltk
nltk.download('punkt')
nltk.download('averaged_perceptron_tagger')
nltk.download('maxent_ne_chunker')
nltk.download('words')





# Links for the reports to be analysed and the agent email to scrape the SEC website
reports_url = {"tesla": "https://www.sec.gov/Archives/edgar/data/1318605/000095017023001409/tsla-20221231.htm", # Tesla
               "apple": "https://www.sec.gov/Archives/edgar/data/320193/000032019322000108/aapl-20220924.htm", # Apple
               "ibm": "https://www.sec.gov/Archives/edgar/data/51143/000155837023002376/ibm-20221231x10k.htm"} # IBM

agent_email = "rlopeprieto@gmail.com"

# Paths to folders to save the text and html documents
txt_folder_path = "/Users/rodrigolopeprieto/Desktop/untitled_folder/theia_dev/reports_txt/"
html_folder_path = "/Users/rodrigolopeprieto/Desktop/untitled_folder/theia_dev/reports_html/"

# Paths for the business summaries and entity recognition results
summary_folder_path = "/Users/rodrigolopeprieto/Desktop/untitled_folder/theia_dev/summaries_txt/"
entity_folder_path = "/Users/rodrigolopeprieto/Desktop/untitled_folder/theia_dev/entities_txt/"




### DOWNLOAD AND STORE THE TEXT FILES AND THE HTML SOURCE ###


# Args: 
# 1. urls: the dictionary of names of the companies and links to their EDGAR reports
# 2. path: specify a folder path

# Returns: 
# A dictionary where keys are the names of the companies and values are the path to their saved text file

def save_text(urls: dict, path: str) -> dict:

    paths = {}
    for company in urls.keys():
        td = TextDownload(reports_url[company], agent_email=agent_email)
        td.extractText(f"{path}" + f"{company}.txt", sep="\n")
        paths[company] = f"{path}" + f"{company}.txt"

    return paths


def save_html(urls: dict, path: str) -> None:
    for url in urls.keys():
        hd = TextDownload(reports_url[url], agent_email=agent_email)
        hd.extractHTML(f"{path}" + f"{url}.html")
    return None



### GET BUSINESS SUMMARIES FOR THE EDGAR FILES ###

# Given that we have already saved the text from the EDGAR reports, we are now gonna examine it and provide a summary of the first section of the document
# which outlines the main information of the company.

# Args: 
# 1. filepath: the path to the saved text file with the EDGAR report
# 2. threshold_prop: the name proportion of the threshold for sentence scores we want in order to be included in the summary
#                    a lower threshold prop give a longer summary and vice versa. The default to 0.8 as it appears to be the most appropriate when tested.
# 3. summary_name: the name we want to give to the summary file

# Returns: 
# Saves the summary as a txt file and returns a string with the business information  summary if needed

def business_summary(filepath: str, summary_name: str, threshold_prop=0.8, return_summary= False) -> str:

    # Take the subset of the file (first section) with the business information
    b = BusinessInfo(filepath)
    indices = b.infoLines()
    business_info = b.businessInfo(indices)

    # Summarise the first section
    bs = BusinessSummary(filepath)
    sentences = sent_tokenize(business_info)
    sentence_scores = bs._calculate_sentence_scores(sentences)
    threshold = bs._calculate_average_score(sentence_scores) * threshold_prop
    business_summary = bs._get_edgar_summary(sentences, sentence_scores, threshold)

    # Save the summary
    with open(summary_name, "w") as a:
        a.write(business_summary)
    
    # Return the summary if needed
    if return_summary:
        return business_summary
    

    else:
        return None
    

### GET PRODUCT NAMES AND INDUSTRY ENTITIES ###

# Analyse the text to extract the names of the main products and classify the company by industry
# When classifying by industry the function returns the three closest matches 
    
# Args: 
# 1. business_info: a string containing the business information or the business summary of the company
# 2. company_name: needed to save the file in an identifyable way

# Returns: 
# None. Saves the files to the desired folder but does not return anything in the program
def get_entities(business_info: str, company_name: str) -> None:

    e = Entities()
    with open(f"{entity_folder_path}" + f"{company_name}" + "_entities.txt", "w") as f:
        f.write("Industry entities: ")
    
    for i, i_entity in enumerate(e.industryEntities(business_info)):
        f.write(f"{i + 1}" + " " + str(i_entity) + " ")
    
    f.write("\n")
    
    f.write("Product entities: ")
    for i, p_entity in enumerate(e.productEntities(business_info)):
        f.write(f"{i + 1}" + " " + str(p_entity) + " ")


### GRAB FINANCIAL REPORTS AND SAVE AS EXCEL SPREADSHEETS ###

# Helper function to remove special characters from excel sheet names
def replace_characters(input_string, characters_to_replace):
    output_string = ""
    for char in input_string:
        # Replace the character with '_' if it exists in the list of characters to be replaced
        if char in characters_to_replace:
            output_string += "_"
        else:
            output_string += char
    return output_string



# A function to download all financial report tables and download them as excel spreadsheets

# Args: 
# 1. url: the url of the report - this is needed to obtain the html source code, from which we identify the tables
# 2. company_name: needed to save the file in their respective folder

# Returns: 
# None. Saves the files to the desired folder but does not return anything in the program
def get_sheets(url:str, company_name: str) -> list[str]:
    
    excel_logs = []
    # Get the source html for the tables
    t = TableDownload(url)
    html_tables = t.getTableSource(f"{agent_email}")

    # Get them as pd.DataFrame
    tables = t.getTables(html_tables)

    for table in tables:
        table_name = str(table.iloc[0, 0])
        table_name = replace_characters(table_name, [" ", "  ", ",", ".", ":", ";", "(1)", "$", "(", ")"])
        try:
            table.to_excel(f"/Users/rodrigolopeprieto/Desktop/theia_insights/financial_sheets/{company_name}/{table_name}.xlsx")
        except Exception as e:
            excel_logs.append(e)
            continue

        print("Errors encountered in:")
        if excel_logs:
            return excel_logs
        else:
            return ["None"]


def main():


    # 1. Save the text and html
    text_paths = save_text(reports_url, txt_folder_path) 
    save_html(reports_url, html_folder_path) 



    # 2. Get the business summaries and save them in a separate folder
    summaries = {}
    for company in text_paths.keys():
        summary = business_summary(text_paths[company], company, return_summary = True)
        summaries[company] = summary
    


    # 3. Save the product and industry entities
    for company in summaries.keys():
        get_entities(summaries[company], company_name = company)



    # 4. Download the financial spreadsheets
    for company in reports_url.keys():
        get_sheets(reports_url[company], company)


    # 5. Get the financial summaries
    
    for company in reports_url.keys():

        try:
            b = BusinessInfo(f"/Users/rodrigolopeprieto/Desktop/theia_insights/reports_txt/{company}.txt")
            fin_indices = b.finLines()    
            fin_info = b.finInfo(fin_indices)
            
            with open(f"/Users/rodrigolopeprieto/Desktop/theia_insights/summaries_txt/{company}_financial_summary.txt", "w") as f:
                f.write(fin_info)
                
        except Exception:
            continue



