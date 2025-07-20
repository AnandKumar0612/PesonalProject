from selenium import webdriver #To control web browser
import time
options = webdriver.EdgeOptions() #To create instnce of browser options for Edge
options.use_chromium = True #Chromium based edge is being used
options.add_argument("--lang=ell") #Set browser language to Greek
options.add_experimental_option('excludeSwitches', ['enable-logging']) #Exclude logging to improve performance
prefs = {
    "translate_whitelists": {'en': 'ell'}, #Specefies translation whitelits, indication English content to be translated to Greek
    "translate": {"enabled": "true"} #Enable the translation
}
options.add_experimental_option("prefs", prefs)
driver = webdriver.Edge(options=options) #Create instance of Edge browser with specified options
driver.get("https://www.youtube.com")
time.sleep(5)
driver.quit()
