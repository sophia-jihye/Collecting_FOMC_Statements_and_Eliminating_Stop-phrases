# Collect FOMC Statements

* Reference
    - Scraping: https://github.com/tengtengtengteng/Webscraping-FOMC-Statements
    - Data source: https://www.federalreserve.gov/monetarypolicy/materials/

* Tips
    - Regular expression online tester: https://pythex.org/

## Command line
```
python main_scrape_and_remove_stop_phrases.py --start_mmddyyyy "09/01/2022" --end_mmddyyyy "11/09/2022"
```

### Input
| Variable           | Type | Example                                                             |
| :----------------- | :--- | :------------------------------------------------------------------ |
| start\_mmddyyyy    | str  | "01/01/1990"                                                        |
| end\_mmddyyyy      | str  | "11/17/2022"                                                        |
| selenium\_filepath | str  | "C:\\GIT\\SELENIUM\_DRIVERS\\chromedriver\_win32\\chromedriver.exe" |
| save\_root\_dir    | str  | "./Statements"                                                      |

### Output 
* One text file contains information regarding a meeting date, document date, and document.
* The following shows the directory structure where the scraped and processed documents are stored.
```
├── main_scrape_and_remove_stop_phrases.py
├── Statements
│   ├── raw
│        ├── 1994
│             ├── 19940204.txt  # The filename indicates the date that the statements was uploaded on the website. `document_date`
│             │					# The first line of the file indicates the date the meeting was held. `meeting_date`
│             │					# The remainder of the file is the FOMC statement. `document`
│             ├── 19940322.txt
│             ├── ...
│        ├── 1995
│             ├── 19950201.txt
│             ├── ...
│        ├── ...
│   ├── no_stop-phrases
│        ├── 1994
│             ├── 19940204.txt
│             ├── 19940322.txt
│             ├── ...
│        ├── 1995
│             ├── 19950201.txt
│             ├── ...
│        ├── ...
```

* Example of raw documents (raw/2022/20221102.txt)
```
MEETING_DATE: November 1-2, 2022
Recent...and Christopher J. Waller. For media inquiries, please email [email protected] or call 202-452-2955. Implementation Note issued November 2, 2022
```

* Example of processed documents (no-stop_phrases/2022/20221102.txt)
```
MEETING_DATE: November 1-2, 2022
Recent...and Christopher J. Waller. 
```

## Full list of stop-phrases
| Regular expression                                             | Stop-phrase example                                                                                                                                               |
| :--------------------------------------------------------------- | :---------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| `Release Date: [A-z][a-z]{2,8} \d{1,2}, \d{4}` | Release Date: February 4, 1994 |
| `For immediate release`                          | For immediate release  |
| `Home \|.*`                                     | Home | Press releases Accessibility | Contact Us Last update: April 20, 2007, Home | News and events Accessibility Last update: December 11, 2001          |
| `\d{4} Monetary policy`                         | 2005 Monetary policy |
| `Implementation Note issued.*`                  | Implementation Note issued January 27, 2016 |
| `Frequently Asked Questions.*`                  | Frequently Asked Questions for…<br>[Refer to <a href="https://www.federalreserve.gov/newsevents/pressreleases/monetary20191011a.htm">this page</a>] |
| `For media inquiries.*`                         | For media inquiries, call 202-452-2955. |
| `\(\d{1,3} KB PDF\)`                          | (61 KB PDF) |
