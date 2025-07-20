from selenium import webdriver
from selenium.webdriver.common.service import Service as ChromeServices
from webdriver_manager.chrome import ChromeDriverManager
#To test with any required version of the Chrome app
#No need to define chrome driver because ChromeDriverManager will take care itself
binaryPath = 'path of chrome testing app of any version eg 117'
options = webdriver.ChromeOptions()
options.binary_location = binaryPath

driver = webdriver.Chrome(service=ChromeServices(ChromeDriverManager(driver_version='117').install()), options=options)
driver.get("https://www.youtube.com/")
driver.close()