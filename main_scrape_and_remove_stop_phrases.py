import time, os, re, pickle, argparse
from bs4 import BeautifulSoup
from selenium import webdriver
from datetime import datetime
from glob import glob
from tqdm import tqdm
tqdm.pandas()
import pandas as pd
import requests

parser = argparse.ArgumentParser()
parser.add_argument('--start_mmddyyyy', type=str, default="01/01/1990")
parser.add_argument('--end_mmddyyyy', type=str, default="11/17/2022")
args = parser.parse_args()

start_mmddyyyy = args.start_mmddyyyy
end_mmddyyyy = args.end_mmddyyyy

selenium_filepath = "C:\GIT\SELENIUM_DRIVERS\chromedriver_win32\chromedriver.exe"
save_root_dir = './Statements'

url = "https://www.federalreserve.gov/monetarypolicy/materials/"

def prepare_resources_for_scraping(selenium_filepath, url, start_mmddyyyy, end_mmddyyyy):
    driver = webdriver.Chrome(selenium_filepath)
    driver.get(url)
    time.sleep(5)
    
    # set start date
    start_date = driver.find_element_by_name("startmodel")
    start_date.clear()
    start_date.send_keys(start_mmddyyyy)

    # set end date
    end_date = driver.find_element_by_name("endmodel")
    end_date.clear()
    end_date.send_keys(end_mmddyyyy)

    # select policy statements
    statement_checkbox = driver.find_element_by_xpath("//label/input[contains(..,'Policy Statements')]")
    statement_checkbox.click()

    # apply filter
    submit = driver.find_element_by_css_selector(".btn.btn-primary")
    submit.click()
    
    # get the page control row
    pagination = driver.find_element_by_class_name('pagination')

    # go to the last page to find the largest page number
    last_page = pagination.find_element_by_link_text('Last')
    last_page.click()
    pages = pagination.text.split('\n')
    largest_page = int(pages[-3])
    
    return driver, pagination, largest_page

def scrape_URLs_and_meeting_dates_and_document_dates(driver, pagination, largest_page):
    statement_url_list, meeting_date_list, document_date_list = [], [], []
    # go back to first page and start the loop
    first_page = pagination.find_element_by_link_text('First')
    first_page.click()
    next_page = pagination.find_element_by_link_text('Next')
    for i in range(largest_page):
        # now to get the items inside
        main = driver.find_element_by_css_selector(".panel.panel-default") # get the app panel
        material_types = main.find_elements_by_css_selector(".fomc-meeting__month.col-xs-5.col-sm-3.col-md-4") # get the 2nd col
        material_types = [element.text for element in material_types] # to get the words
        material_links = main.find_elements_by_css_selector(".fomc-meeting__month.col-xs-5.col-sm-3.col-md-2") # get the 3rd col
        html_elements = [element.find_element_by_link_text('HTML') for element in material_links] # get the html ones
        # add url to statement_url_list if it is a statement
        statement_url_list.extend([html_elements[i].get_attribute('href') for i, j in enumerate(material_types) if j=='Statement'])
        
        meeting_dates = main.find_elements_by_css_selector(".fomc-meeting__month.col-xs-5.col-sm-3.col-md-3 > strong")
        meeting_dates = [element.text for element in meeting_dates] # to get the words
        meeting_dates = meeting_dates[2:] # First two items correspond to table headings (i.e.,"Meeting date", "Document date")
        meeting_date_list.extend([meeting_dates[i] for i, j in enumerate(material_types) if j=='Statement'])
        
        document_dates = main.find_elements_by_css_selector(".fomc-meeting__month.col-xs-5.col-sm-3.col-md-3 > em")
        document_dates = [element.text for element in document_dates] # to get the words
        document_date_list.extend([document_dates[i] for i, j in enumerate(material_types) if j=='Statement'])
        
        next_page.click()
    print('Number of URLs: {}'.format(len(statement_url_list)))
    
    return statement_url_list, meeting_date_list, document_date_list

def get_text_for_a_statement_from_2006_to_2022(soup):
    return soup.find('div', class_ = 'col-xs-12 col-sm-8 col-md-8').text.strip()

def get_text_for_a_statement_from_1996_to_2005(soup):
    return '\n'.join([item.text.strip() for item in soup.select('table td')])

def get_text_for_a_statement_from_1994_to_1995(soup):
    return soup.find('div', id="content").text.strip()

doublespace_pattern = re.compile('\s+')
def remove_doublespaces(document):
    return doublespace_pattern.sub(' ', document).strip()

stop_phrase_patterns = [re.compile('Release Date: [A-z][a-z]{2,8} \d{1,2}, \d{4}')\
                       , re.compile('For immediate release')\
                       , re.compile('Home \|.*')\
                       , re.compile('\d{4} Monetary policy')\
                       , re.compile('Implementation Note issued.*')\
                       , re.compile('Frequently Asked Questions.*')\
                       , re.compile('For media inquiries.*')\
                       , re.compile('\(\d{1,3} KB PDF\)')]
def remove_stop_phrases(document):
    for stop_phrase_pattern in stop_phrase_patterns:
        document = stop_phrase_pattern.sub(' ', document)
        document = remove_doublespaces(document)
    return document

if __name__ == '__main__':
    
    driver, pagination, largest_page = prepare_resources_for_scraping(selenium_filepath, url, start_mmddyyyy, end_mmddyyyy)
    statement_url_list, meeting_date_list, document_date_list = scrape_URLs_and_meeting_dates_and_document_dates(driver, pagination, largest_page)
        
    doc_count = 0
    for statement_url, meeting_date, document_date in tqdm(zip(statement_url_list, meeting_date_list, document_date_list)):
        
        # Scrape statements
        statement_resp = requests.get(statement_url)
        statement_soup = BeautifulSoup(statement_resp.content, 'lxml')

        document_date_yyyymmdd = datetime.strftime(datetime.strptime(document_date, "%B %d, %Y"), "%Y%m%d")
        year = int(document_date_yyyymmdd[:4])
        if year >= 2006:
            doc = get_text_for_a_statement_from_2006_to_2022(statement_soup)
        elif year >=1996:
            doc = get_text_for_a_statement_from_1996_to_2005(statement_soup)
        else:
            doc = get_text_for_a_statement_from_1994_to_1995(statement_soup)
        
        # Clean
        doc = remove_doublespaces(doc)
        
        # Save data
        save_dir = os.path.join(save_root_dir, 'raw', document_date_yyyymmdd[:4])
        if not os.path.exists(save_dir): os.makedirs(save_dir)
        save_filepath = os.path.join(save_dir, '{}.txt'.format(document_date_yyyymmdd))
        with open(save_filepath, "w", encoding='utf-8-sig') as file:
            file.write("MEETING_DATE: {}\n".format(meeting_date))
            file.write(doc)
            doc_count += 1
            
        # Remove stop-phrases
        doc = remove_stop_phrases(doc)
        
        # Save data
        save_dir = os.path.join(save_root_dir, 'no_stop-phrases', document_date_yyyymmdd[:4])
        if not os.path.exists(save_dir): os.makedirs(save_dir)
        save_filepath = os.path.join(save_dir, '{}.txt'.format(document_date_yyyymmdd))
        with open(save_filepath, "w", encoding='utf-8-sig') as file:
            file.write("MEETING_DATE: {}\n".format(meeting_date))
            file.write(doc)
            doc_count += 1
            
    save_dir = '{}/{}'.format(save_root_dir, 'raw')
    print('Saved {} unique documents under {}'.format(len(glob('{}/*/*.txt'.format(save_dir))), save_dir)) 
    
    save_dir = '{}/{}'.format(save_root_dir, 'no_stop-phrases')
    print('Saved {} unique documents under {}'.format(len(glob('{}/*/*.txt'.format(save_dir))), save_dir)) 
    
    
