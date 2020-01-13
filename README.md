# Grade Crawler for DHGE Selfservice 

Simple Grade Crawler for DHGE SelfService

## Setup:
  
1. Extract script and Firefoxdriver (geckodriver) in the same diretory
        
   >Firefox-Driver: <https://github.com/mozilla/geckodriver/releases>
2. Install selenium 

       pip install selenium
            
## How to use:
1. Configurate the script at section CONFIG or use the init wizard
         (activate use_wizard in section WIZARDs)
2. Start the script 

       py GradeCrawler.py
           
   :information_source:To exit close terminal/cmd or press `strg+c`

   :information_source: Script create data at first run, check grades in terminal! Later the
     script sends notification mails if new grades detected

:warning: This crawler use Firefox as Seleniumdriver, but Chrome can be
used too.
- **Chromedriver download:**
      <https://chromedriver.chromium.org/downloads>
- **Config:**
      Search for line `driver = webdriver.Firefox()` and edit it to
      `driver = webdriver.Chrome()`
