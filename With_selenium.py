# Code creator: tengtengtengteng
# https://github.com/tengtengtengteng/Webscraping-FOMC-Statements

from bs4 import BeautifulSoup
import requests
import pandas as pd
from selenium import webdriver
import time

selenium_filepath = "C:\GIT\SELENIUM_DRIVERS\chromedriver_win32\chromedriver.exe"

url = "https://www.federalreserve.gov/monetarypolicy/materials/"
start_yyyymmdd = "01/01/2020"

driver = webdriver.Chrome(selenium_filepath)
driver.get(url)

# wait a while for page to load
time.sleep(10)
# set start date
start_date = driver.find_element_by_name("startmodel")
start_date.clear()
start_date.send_keys(start_yyyymmdd)
# select policy statements
statement_checkbox = driver.find_element_by_xpath("//label/input[contains(..,'Policy Statements')]")
statement_checkbox.click()
# apply filter
submit = driver.find_element_by_css_selector(".btn.btn-primary")
submit.click()


statement_url_list = []
# I can get for a page already. Now need to loop through all pages to get for each page.
# get the page control row
pagination = driver.find_element_by_class_name('pagination')
# go to the last page to find the largest page number
last_page = pagination.find_element_by_link_text('Last')
last_page.click()
pages = pagination.text.split('\n')
largest_page = int(pages[-3])
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
    

# go to each url and save the date and article
date_list = []
statement_list = []
for statement_url in statement_url_list:
    statement_resp = requests.get(statement_url)
    statement_soup = BeautifulSoup(statement_resp.content, 'lxml')
    # get the article and date
    article = statement_soup.find('div', class_ = 'col-xs-12 col-sm-8 col-md-8').text
    date = statement_url[-13:-5]
    statement_list.append(article.strip())
    date_list.append(date)
# save as df
df_statements = pd.DataFrame(list(zip(date_list, statement_list)), 
                             columns =['Date', 'Statement'])
# convert date to date format
df_statements['Date'] = pd.to_datetime(df_statements['Date'], format='%Y%m%d')
# sort by date
df_statements.sort_values(by='Date', ascending=False, inplace=True)
# output to csv
df_statements.to_csv('FOMC_statements.csv', index=False, encoding='utf-8-sig')