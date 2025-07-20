from selenium import webdriver
import time
# driver = webdriver.Edge()
driver = webdriver.Chrome()
driver.get("https://www.youtube.com/")
time.sleep(5)
print(driver.title)

driver.quit()
