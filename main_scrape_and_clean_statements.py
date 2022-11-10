from bs4 import BeautifulSoup
import requests
import pandas as pd
from selenium import webdriver
import time, os, re, pickle
import argparse
from transformers import pipeline
from glob import glob
from nltk import sent_tokenize
import pandas as pd
from tqdm import tqdm
tqdm.pandas()
import numpy as np
from sklearn.cluster import KMeans
from collections import defaultdict

parser = argparse.ArgumentParser()
parser.add_argument('--start_mmddyyyy', type=str, default="01/01/1990")
parser.add_argument('--end_mmddyyyy', type=str, default="08/01/2022")
args = parser.parse_args()

start_mmddyyyy = args.start_mmddyyyy
end_mmddyyyy = args.end_mmddyyyy

selenium_filepath = "C:\GIT\SELENIUM_DRIVERS\chromedriver_win32\chromedriver.exe"
noise_detection_model_filepath = "noise_detection_model.pkl"
save_root_dir = './Statements'

url = "https://www.federalreserve.gov/monetarypolicy/materials/"

def prepare_resources_for_scraping(selenium_filepath):
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

def scrape_URLs(driver, pagination, largest_page):
    statement_url_list = []
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
        next_page.click()
    print('Number of URLs: {}'.format(len(statement_url_list)))
    
    return statement_url_list

def get_text_for_a_statement_from_2006_to_2022(soup):
    return soup.find('div', class_ = 'col-xs-12 col-sm-8 col-md-8').text.strip()

def get_text_for_a_statement_from_1996_to_2005(soup):
    return '\n'.join([item.text.strip() for item in soup.select('table td')])

def get_text_for_a_statement_from_1994_to_1995(soup):
    return soup.find('div', id="content").text.strip()

def prepare_resources_for_cleaning(noise_detection_model_filepath):
    nlp_features = pipeline('feature-extraction', model="nlpaueb/sec-bert-base")
    
    with open(noise_detection_model_filepath, "rb") as f:
        noise_detection_model = pickle.load(f)
        
    return nlp_features, noise_detection_model

def extract_sentences(doc):
    sentences = []
    for temp_sentence in doc.split('\n'):
        sentences.extend(sent_tokenize(temp_sentence))
    sentences = [item.strip() for item in sentences]
    return sentences

def get_feature(sentence):
    return np.squeeze(nlp_features(sentence)).mean(0) # Get average values of the embedding layers

if __name__ == '__main__':
    
    driver, pagination, largest_page = prepare_resources_for_scraping(selenium_filepath)
    statement_url_list = scrape_URLs(driver, pagination, largest_page)
    nlp_features, noise_detection_model = prepare_resources_for_cleaning(noise_detection_model_filepath)
        
    doc_count = 0
    for statement_url in tqdm(statement_url_list):
        
        # Scrape statements
        statement_resp = requests.get(statement_url)
        statement_soup = BeautifulSoup(statement_resp.content, 'lxml')

        for item in re.findall('[0-9]+', statement_url):
            if len(item)==8:
                yyyymmdd = item

        year = int(yyyymmdd[:4])
        if year >= 2006:
            doc = get_text_for_a_statement_from_2006_to_2022(statement_soup)
        elif year >=1996:
            doc = get_text_for_a_statement_from_1996_to_2005(statement_soup)
        else:
            doc = get_text_for_a_statement_from_1994_to_1995(statement_soup)
        
        # Noise filtering
        sentences = extract_sentences(doc)
        one_doc_sentences_df = pd.DataFrame(sentences, columns=['sentence'])
        one_doc_sentences_df['meeting_date'] = '-'.join([yyyymmdd[:4], yyyymmdd[4:6], yyyymmdd[6:]])
        one_doc_sentences_df['feature'] = one_doc_sentences_df['sentence'].progress_apply(lambda x: get_feature(x))
        
        arr = np.vstack(one_doc_sentences_df['feature'].values)
        labels = noise_detection_model.predict(arr)
        one_doc_sentences_df['cluster_index'] = labels
        
        for cluster_index in [3, 4, 5, 9, 12, 13, 20, 26, 28]:
            print('Cluster index : {}'.format(cluster_index))
            print(one_doc_sentences_df[(one_doc_sentences_df['cluster_index']==cluster_index)]['sentence'].values)
            
        to_be_deleted_rows = one_doc_sentences_df[one_doc_sentences_df.cluster_index.isin([3, 4, 5, 9, 12, 13, 20, 26, 28])]
        print('Drop {} rows'.format(len(to_be_deleted_rows)))
        one_doc_sentences_df.drop(to_be_deleted_rows.index, inplace=True)
        
        doc = ' '.join(one_doc_sentences_df['sentence'].values)
        
        # Save
        save_dir = os.path.join(save_root_dir, yyyymmdd[:4])
        if not os.path.exists(save_dir): os.makedirs(save_dir)
        save_filepath = os.path.join(save_dir, '{}.txt'.format(yyyymmdd))
        with open(save_filepath, "w", encoding='utf-8-sig') as file:
            file.write(doc)
            doc_count += 1

    print('Number of documents: {}'.format(doc_count))
    
