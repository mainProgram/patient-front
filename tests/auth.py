import sys
import os
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

# Configuration des credentials depuis les variables d'environnement
username = os.getenv('TEST_USERNAME', 'admin')
password = os.getenv('TEST_PASSWORD', 'password123')

wait = WebDriverWait(driver, 30)

try:
    print(f"Ouverture de la page: {app_url}")
    driver.get(app_url)
    time.sleep(8)

    print("Recherche du champ nom d'utilisateur")
    username_input = wait.until(EC.element_to_be_clickable((By.NAME, "username")))
    time.sleep(3)

    print("Recherche du champ mot de passe")
    password_input = wait.until(EC.element_to_be_clickable((By.NAME, "password")))
    time.sleep(3)

    print("Recherche du bouton de soumission")
    submit_button = driver.find_element(By.CSS_SELECTOR, "button[type='submit']")
    time.sleep(3)

    print("Saisie du nom d'utilisateur")
    username_input.send_keys(username)
    time.sleep(3)

    print("Saisie du mot de passe")
    password_input.send_keys(password)
    time.sleep(3)

    print("Soumission du formulaire de connexion")
    submit_button.click()

    try:
        wait.until(EC.url_contains("/patients"))
        print("Redirection vers la page patients détectée")
    except:
        error_msg = driver.find_elements(By.CLASS_NAME, "error-message")
        if error_msg:
            raise Exception("Message d'erreur trouvé sur la page: " + error_msg[0].text)
        print("Aucune redirection détectée, mais pas de message d'erreur")

    print("Recherche et clic sur le bouton de déconnexion")
    logout_button = driver.find_element(By.ID, "logout")
    time.sleep(3)

    logout_button.click()
    time.sleep(5)

    print("Test réussi: Connexion et déconnexion effectuées avec succès")
    exit(0)

except Exception as e:
    print("Échec du test:", str(e))
    driver.save_screenshot("error_screenshot.png")
    exit(1)

finally:
    time.sleep(5)
    driver.quit()
