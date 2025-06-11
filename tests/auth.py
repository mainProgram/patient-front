import sys
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import time

options = Options()
options.add_argument("--no-sandbox")
options.add_argument("--disable-dev-shm-usage")

driver = webdriver.Remote(
    command_executor='http://selenium:4444/wd/hub',
    options=options
)

app_url = sys.argv[1] if len(sys.argv) > 1 else "http://localhost:4201"

wait = WebDriverWait(driver, 30)
try:
    print(f" Ouverture de la page: {app_url}")
    driver.get(app_url)
    time.sleep(8)

    print(" Getting username text field")
    username_input = wait.until(EC.element_to_be_clickable((By.NAME, "username")))
    time.sleep(3)

    print(" Getting password text field")
    password_input = wait.until(EC.element_to_be_clickable((By.NAME, "password")))
    time.sleep(3)

    print(" Getting submit button")
    submit_button = driver.find_element(By.CSS_SELECTOR, "button[type='submit']")
    time.sleep(3)

    print(" Filling username field")
    username_input.send_keys("admin")
    time.sleep(3)

    print(" Filling password field")
    password_input.send_keys("password123")
    time.sleep(3)

    print(" Submitting login form")
    submit_button.click()
    try:
        wait.until(EC.url_contains("/patients"))
    except:
        error_msg = driver.find_elements(By.CLASS_NAME, "error-message")
        if error_msg:
            raise Exception("Error message found on page: " + error_msg[0].text)

    print(" Finding and clicking logout button")
    logout_button = driver.find_element(By.ID, "logout")
    time.sleep(3)

    logout_button.click()
    time.sleep(5)

    print("✅ Test passed: Login successful or expected page loaded")
    exit(0)

except Exception as e:
    print("Test failed:", str(e))
    driver.save_screenshot("error_screenshot.png")
    exit(1)

finally:
    time.sleep(5)
    driver.quit()
