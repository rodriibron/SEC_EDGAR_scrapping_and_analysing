# SEC_EDGAR_scrapping_and_analysing

This repository contains a series of tools for scraping, analysing and summarising EDGAR reports from the SEC.

In particular there are 4 python files and three folders where relevant downloaded documents were downloaded. This was developed locally, 
so the user should change some of the file paths to run this code in their laptop. This is a demo which only includes 3 EDGAR reports, which
are Tesla, Apple and IBM, although this can be applied to any other report.






## FILE OUTLINES

Each of the four files includes detailed comments explaining the usage of each of the classes and functions. An outline of the functionalities
of each of the files is the following:


1. text_scrapper.py

Essentially a toolkit for scraping the SEC website and saving the relevant documents. We have tried with the reports from Apple, Tesla and IBM, but this
same code can be used for any report, as long as we have the link. Note that the SEC website needs a user agent name and an user agent email to be scraped, 
as otherwise the website blocks all bots.
Here you can find code which allows you to extract the text and the tables from any EDGAR report


2. business_info.py

The code found in this file is used to firstly subset the document to just the relevant sections we want to analyse and sumarrise. Then, in the second helf of this
file we can find the code used to summarise the text using NLP techniques and the nltk library.


3. product_industry_entities.py 

Here we can find code used for entity recognition of the scraped text files. In particular, you can find functions to obtain industry themes and main products of the 
company whose EDGAR report we are analysing using again nltk.


4. main.py 

Wraps up the rest of the code in this repository. Takes care of scraping, downloading of text, tables and source html, filtering and summarisation and entity recognition.







## DEPENDENCIES NEEDED

This repository only contains open source public libraries. In particular, for the code to run we need:

- Python packages:
numpy
pandas
re

- Webscraping packages
requests

bs4 including:
from bs4 import BeautifulSoup, element, Tag

selenium including:
from selenium import webdriver, from selenium.webdriver.chrome.service import Service 

webdriver_manager.chrome including:
from webdriver_manager.chrome import ChromeDriverManager

- NLP packages
nltk including:
from nltk.corpus import stopwords
from nltk.stem import PorterStemmer
from nltk.tokenize import word_tokenize, sent_tokenize
from nltk.tag import pos_tag
from nltk.chunk import ne_chunk

- NLP pre trained models:
nltk.download('punkt')
nltk.download('averaged_perceptron_tagger')
nltk.download('maxent_ne_chunker')
nltk.download('words')
