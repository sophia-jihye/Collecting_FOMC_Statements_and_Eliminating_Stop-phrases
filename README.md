# Scrape and Parse FOMC Statements

* Reference
    - https://github.com/tengtengtengteng/Webscraping-FOMC-Statements
    
### main_scrape_FOMC_statements.py
* input
    - `selenium_filepath` (ex. 'C:\GIT\SELENIUM_DRIVERS\chromedriver_win32\chromedriver.exe')
    - `start_yyyymmdd` (ex. '01/01/2020')
    - `save_filepath` (ex. '/media/dmlab/My Passport/DATA/fomc/FOMC_statements.csv')
    
* output
    - Records of `['Date', 'Statement']`
        - Refer to `Check scraped FOMC Statements`
```
# output of main_scrape_SEC.py
Date: 2021-12-15
Statement: The Federal Reserve is committed to..
```