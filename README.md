# Collect FOMC Statements

* Reference
    - Scraping: https://github.com/tengtengtengteng/Webscraping-FOMC-Statements
    - Data source: https://www.federalreserve.gov/monetarypolicy/fomccalendars.htm

### Scrape, clean, and save statements
```
python main_scrape_ane_clean_statements.py --start_mmddyyyy "09/01/2022" --end_mmddyyyy "11/09/2022"
```

### Noise detection model 
* 학습 데이터: 1990-01-01 ~ 2022-08-01 
    - 문서 수: 213개
    - Phrases 수: 3,372개
* Cluster 수: 50
