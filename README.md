# Collect FOMC Statements

* Reference
    - Scraping: https://github.com/tengtengtengteng/Webscraping-FOMC-Statements
    - Data source: https://www.federalreserve.gov/monetarypolicy/materials/

* Tips
    - Regular expression online tester: https://pythex.org/

### Command line
```
python main_scrape_and_remove_stop_phrases.py --start_mmddyyyy "09/01/2022" --end_mmddyyyy "11/09/2022"
```

### Stop-phrases
| Regular
  expression                                             | Stop-phrase example                                                                                                                                               |
| :--------------------------------------------------------------- | :---------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| `re.compile('Release Date: [A-z][a-z]{2,8} \d{1,2}, \d{4}')` | Release Date: February 4, 1994 |
| `re.compile('For immediate release')`                          | For immediate release  |
| `re.compile('Home \|.*')`                                     | Home | Press releases Accessibility | Contact Us Last update: April 20, 2007, Home | News and events Accessibility Last update: December 11, 2001          |
| `re.compile('\d{4} Monetary policy')`                         | 2005 Monetary policy |
| `re.compile('Implementation Note issued.*')`                  | Implementation Note issued January 27, 2016 |
| `re.compile('Frequently Asked Questions.*')`                  | Frequently Asked Questions for…<br>[Refer to <a href="https://www.federalreserve.gov/newsevents/pressreleases/monetary20191011a.htm">this page</a>] |
| `re.compile('For media inquiries.*')`                         | For media inquiries, call 202-452-2955. |
| `re.compile('\(\d{1,3} KB PDF\)`                          | (61 KB PDF) |
