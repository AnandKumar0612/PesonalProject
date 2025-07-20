from selenium import webdriver
from selenium.webdriver.chrome.service import Service as ChromeService
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
import time

driver = webdriver.Chrome(service=ChromeService(ChromeDriverManager().install()))
driver.get("https://witbe.app/home")
driver.maximize_window()
time.sleep(5)
LoginPage = driver.find_element(By.XPATH, '//*[text()="Log in to continue to:"]').is_displayed()
if LoginPage == True:
    print('On Login Page')
else:
    print('Not on login page')

userName = driver.find_element(By.XPATH, '//*[@id="username"]').send_keys('anand.kumar3@vodafone.com')
driver.find_element(By.XPATH, '//*[@value="Continue"]').click()
time.sleep(5)
pageTitle = driver.title
if pageTitle == "Sign in to your account":
    print("Required SSO login")
else:
    print("Login successfully done")

#driver.find_element(By.XPATH, '//*[@value="Send notification"]').click()
#time.sleep(30)
driver.close()
