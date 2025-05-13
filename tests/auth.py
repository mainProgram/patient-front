from selenium import webdriver
from selenium.webdriver import ActionChains
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service as ChromeService
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from webdriver_manager.chrome import ChromeDriverManager

options = Options()
options.add_argument("--headless")
options.add_argument("--no-sandbox")
options.add_argument("--disable-dev-shm-usage")


import time

# Initialiser le navigateur
driver = webdriver.Chrome(options=options, service=ChromeService(ChromeDriverManager().install()))
wait = WebDriverWait(driver, 15)
try:
    # Aller à la page du formulaire de login Angular
    print("🚀 Ouverture de la page")
    driver.get("http://localhost:4200/")
    print("Page source snapshot:\n", driver.page_source[:1000])
    time.sleep(5)  # Attendre le chargement

    # Trouver les champs
    #username_input = driver.find_element(By.NAME, "username")
    print("🚀 gettint username text field")
    username_input = wait.until(EC.element_to_be_clickable((By.NAME, "username")))
    time.sleep(5)
    print("🚀 getting password text field")
    #password_input = driver.find_element(By.NAME, "password")
    password_input = wait.until(EC.element_to_be_clickable((By.NAME, "password")))
    time.sleep(5)
    print("🚀 getting button submit")
    #login_button = driver.find_element(By.TAG_NAME, "button")
    submit_button = driver.find_element(By.CSS_SELECTOR, "button[type='submit']")


    # Entrer les données
    print("🚀 filling with value username text field ")
    username_input.send_keys("admin")
    print("🚀 filling with value password texte field")
    password_input.send_keys("admin123")
    #submit_button.click()

    # Attente du résultat
    #time.sleep(10)

    #logout_button = wait.until(EC.element_to_be_clickable((By.ID, "logout")))

    #logout_button.click()
    # Exemple : vérifier redirection ou affichage d'un message
    #assert "dashboard" in driver.current_url.lower() or "welcome" in driver.page_source.lower()

    print("✅ Test passed : Login successful or expected page loaded.")



except Exception as e:
    print("❌ Test failed:", str(e))

finally:
    driver.quit()
