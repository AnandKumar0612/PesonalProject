from selenium import webdriver
from selenium.webdriver.common.service import Service as ChromeService
from webdriver_manager.chrome import ChromeDriverManager
#No need to define chrome driver because ChromeDriverManager will take care itself
driver = webdriver.Chrome(service=ChromeService(ChromeDriverManager().install()))

driver.get('https://www.youtube.com/')
title = driver.title
print(title)
driver.close()
