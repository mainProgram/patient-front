import time

from selenium import webdriver
from selenium.webdriver import ActionChains
from selenium.webdriver.common.by import By

# Initialisation du navigateur
driver = webdriver.Chrome()
driver.get("https://www.amazon.fr/")
driver.maximize_window()

# Attendre que la page se charge
time.sleep(5)

#
accept = driver.find_element(By.ID, 'sp-cc-accept')
accept.click()
time.sleep(3)

search = driver.find_element(By.ID, "twotabsearchtextbox")
search.send_keys("tele")
time.sleep(5)

fourth_choice= driver.find_element(By.XPATH, '//*[@id="nav-flyout-searchAjax"]/div[2]/div[1]/div[1]/div[4]')
fourth_choice.click()
time.sleep(2)

driver.execute_script("window.scrollTo(0, 1130);")
time.sleep( 5)

starts_link = driver.find_element(By.XPATH, '//*[@id="search"]/div[1]/div[1]/div/span[1]/div[1]/div[7]/div/div/span/div/div/div[3]/div[2]/div[1]/span/a')
actions = ActionChains(driver)
actions.move_to_element(starts_link)
actions.perform()
time.sleep(0.5)
starts_link.click()
time.sleep(5)

article_image=driver.find_element(By.XPATH, "/html/body/div[1]/div[1]/div[1]/div[1]/div/span[1]/div[1]/div[4]/div/div/div/div/span/div/div/div[2]/span/a/div/img")
article_image.click()
time.sleep(5)

driver.execute_script("window.scrollTo(0, 500);")
time.sleep( 5)

article_image=driver.find_element(By.XPATH, '//*[@id="poToggleButton"]/a/span')
article_image.click()
time.sleep(5)

driver.quit()