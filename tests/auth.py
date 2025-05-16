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

# Se connecter au standalone Chrome
driver = webdriver.Remote(
    command_executor='http://selenium:4444/wd/hub',
    options=options
)

# Obtenir l'URL depuis les arguments de ligne de commande ou utiliser une valeur par défaut
app_url = sys.argv[1] if len(sys.argv) > 1 else "http://localhost:4201"

wait = WebDriverWait(driver, 30)  # Augmenté à 30 secondes
try:
    print(f"🚀 Ouverture de la page: {app_url}")
    driver.get(app_url)
    time.sleep(10)  # Augmenté à 10 secondes pour avoir le temps de voir la page se charger

    print("🚀 Getting username text field")
    username_input = wait.until(EC.element_to_be_clickable((By.NAME, "username")))
    time.sleep(3)  # Pause après avoir trouvé l'élément

    print("🚀 Getting password text field")
    password_input = wait.until(EC.element_to_be_clickable((By.NAME, "password")))
    time.sleep(3)  # Pause après avoir trouvé l'élément

    print("🚀 Getting submit button")
    submit_button = driver.find_element(By.CSS_SELECTOR, "button[type='submit']")
    time.sleep(3)  # Pause après avoir trouvé l'élément

    print("🚀 Filling username field")
    username_input.send_keys("admin")
    time.sleep(3)  # Pause après avoir rempli le champ

    print("🚀 Filling password field")
    password_input.send_keys("password123")
    time.sleep(3)  # Pause après avoir rempli le champ

    print("🚀 Submitting login form")
    submit_button.click()
    time.sleep(10)  # Augmenté à 10 secondes pour voir la redirection après login

    print("🚀 Finding and clicking logout button")
    logout_button = driver.find_element(By.ID, "logout")
    time.sleep(3)  # Pause avant de cliquer sur le bouton de déconnexion

    logout_button.click()
    time.sleep(5)  # Pause pour voir l'action de déconnexion

    print("✅ Test passed: Login successful or expected page loaded")
    exit(0)  # Succès

except Exception as e:
    print("❌ Test failed:", str(e))
    driver.save_screenshot("error_screenshot.png")  # Capture d'écran en cas d'erreur
    exit(1)  # Échec

finally:
    time.sleep(5)  # Pause avant de fermer le navigateur
    driver.quit()
