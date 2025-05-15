from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import time

options = Options()
options.add_argument("--headless")
options.add_argument("--no-sandbox")
options.add_argument("--disable-dev-shm-usage")

# Se connecter au standalone Chrome
driver = webdriver.Remote(
    command_executor='http://selenium:4444/wd/hub',
    options=options
)

wait = WebDriverWait(driver, 15)
try:
    # Utiliser localhost car c'est exécuté depuis Jenkins qui a accès à l'app HTTP servie
    print("🚀 Ouverture de la page")
    driver.get("http://localhost:4201/")
    time.sleep(5)

    print("🚀 Getting username text field")
    username_input = wait.until(EC.element_to_be_clickable((By.NAME, "username")))

    print("🚀 Getting password text field")
    password_input = wait.until(EC.element_to_be_clickable((By.NAME, "password")))

    print("🚀 Getting submit button")
    submit_button = driver.find_element(By.CSS_SELECTOR, "button[type='submit']")

    print("🚀 Filling username field")
    username_input.send_keys("admin")

    print("🚀 Filling password field")
    password_input.send_keys("admin123")

    print("🚀 Submitting login form")
    submit_button.click()

    time.sleep(5)

    print("🚀 Finding and clicking logout button")
    logout_button = driver.find_element(By.ID, "logout")
    logout_button.click()

    print("✅ Test passed: Login successful or expected page loaded")
    exit(0)  # Succès

except Exception as e:
    print("❌ Test failed:", str(e))
    exit(1)  # Échec

finally:
    driver.quit()
