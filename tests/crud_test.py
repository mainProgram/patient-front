# tests/crud_test.py
import sys
import time
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import Select
from datetime import datetime

options = Options()
options.add_argument("--no-sandbox")
options.add_argument("--disable-dev-shm-usage")

# Se connecter au standalone Chrome
driver = webdriver.Remote(
    command_executor='http://selenium:4444/wd/hub',
    options=options
)

# Obtenir l'URL depuis les arguments de ligne de commande
app_url = sys.argv[1] if len(sys.argv) > 1 else "http://localhost:4201"

wait = WebDriverWait(driver, 30)
success = False

# Générer un nom unique pour éviter les conflits
timestamp = datetime.now().strftime("%Y%m%d%H%M%S")
test_patient_nom = f"Test{timestamp}"
test_patient_prenom = f"Patient{timestamp}"

try:
    print("=== DÉBUT DES TESTS CRUD ===")

    print(f"🚀 Ouverture de la page: {app_url}")
    driver.get(app_url)
    time.sleep(5)

    # CONNEXION
    print("=== TEST DE CONNEXION ===")
    username_input = wait.until(EC.element_to_be_clickable((By.NAME, "username")))
    password_input = wait.until(EC.element_to_be_clickable((By.NAME, "password")))
    submit_button = driver.find_element(By.CSS_SELECTOR, "button[type='submit']")

    username_input.send_keys("admin")
    password_input.send_keys("password123")
    submit_button.click()
    time.sleep(5)

    # Vérifier si on est bien connecté (redirection vers la liste des patients)
    wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, "mat-toolbar")))
    driver.save_screenshot("1_login_success.png")
    print("✅ Connexion réussie")

    # CRÉATION (CREATE)
    print("=== TEST DE CRÉATION ===")

    # Naviguer vers le formulaire d'ajout
    add_button = wait.until(EC.element_to_be_clickable((By.CSS_SELECTOR, "button[routerlink='/patients/add']")))
    add_button.click()
    time.sleep(3)

    # Remplir le formulaire
    nom_input = wait.until(EC.element_to_be_clickable((By.CSS_SELECTOR, "input[formcontrolname='nom']")))
    prenom_input = driver.find_element(By.CSS_SELECTOR, "input[formcontrolname='prenom']")
    sexe_select = driver.find_element(By.CSS_SELECTOR, "mat-select[formcontrolname='sexe']")

    nom_input.send_keys(test_patient_nom)
    prenom_input.send_keys(test_patient_prenom)

    # Sélectionner le sexe
    sexe_select.click()
    time.sleep(1)
    sexe_option = wait.until(EC.element_to_be_clickable((By.XPATH, "//mat-option[@value='HOMME']")))
    sexe_option.click()
    time.sleep(1)

    # Date de naissance
    date_input = driver.find_element(By.CSS_SELECTOR, "input[formcontrolname='dateNaissance']")
    driver.execute_script("arguments[0].value = '2000-01-01'", date_input)

    # Taille et poids
    taille_input = driver.find_element(By.CSS_SELECTOR, "input[formcontrolname='taille']")
    poids_input = driver.find_element(By.CSS_SELECTOR, "input[formcontrolname='poids']")

    taille_input.send_keys("175")
    poids_input.send_keys("70")

    # Remplir un contact
    type_contact_select = driver.find_element(By.CSS_SELECTOR, "mat-select[formcontrolname='type']")
    type_contact_select.click()
    time.sleep(1)

    email_option = wait.until(EC.element_to_be_clickable((By.XPATH, "//mat-option[@value='EMAIL']")))
    email_option.click()
    time.sleep(1)

    contact_input = driver.find_element(By.CSS_SELECTOR, "input[formcontrolname='contact']")
    contact_input.send_keys("test@example.com")

    # Soumettre le formulaire
    submit_form_button = driver.find_element(By.CSS_SELECTOR, "button[type='submit']")
    driver.save_screenshot("2_create_form_filled.png")
    submit_form_button.click()

    # Attendre la redirection vers la page de détails
    time.sleep(5)
    wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, "mat-card-title")))
    driver.save_screenshot("3_create_success.png")

    # Vérifier que les données ont été créées correctement
    card_title = driver.find_element(By.CSS_SELECTOR, "mat-card-title").text
    if test_patient_prenom in card_title and test_patient_nom in card_title:
        print(f"✅ Création réussie du patient: {test_patient_prenom} {test_patient_nom}")
    else:
        print("❌ Échec de la création du patient")
        raise Exception("Les données du patient ne correspondent pas")

    # Obtenir l'ID du patient depuis l'URL
    current_url = driver.current_url
    patient_id = current_url.split("/")[-1]
    print(f"ID du patient créé: {patient_id}")

    # LECTURE (READ)
    print("=== TEST DE LECTURE ===")

    # Vérifier que les informations sont correctement affichées
    patient_details = driver.find_element(By.CSS_SELECTOR, "mat-card-content").text

    if "Taille : 175" in patient_details and "Poids : 70" in patient_details:
        print("✅ Lecture réussie des détails du patient")
    else:
        print("❌ Échec de la lecture des détails du patient")
        raise Exception("Les détails du patient ne sont pas correctement affichés")

    # MISE À JOUR (UPDATE)
    print("=== TEST DE MISE À JOUR ===")

    # Cliquer sur le bouton de modification
    edit_button = driver.find_element(By.XPATH, "//button[contains(text(), 'Modifier')]")
    edit_button.click()
    time.sleep(3)

    # Modifier la taille
    taille_input = wait.until(EC.element_to_be_clickable((By.CSS_SELECTOR, "input[formcontrolname='taille']")))
    taille_input.clear()
    taille_input.send_keys("180")

    # Enregistrer la modification
    submit_form_button = driver.find_element(By.CSS_SELECTOR, "button[type='submit']")
    driver.save_screenshot("4_update_form_filled.png")
    submit_form_button.click()

    # Attendre la redirection vers la page de détails
    time.sleep(5)
    wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, "mat-card-title")))
    driver.save_screenshot("5_update_success.png")

    # Vérifier que les modifications ont été enregistrées
    patient_details = driver.find_element(By.CSS_SELECTOR, "mat-card-content").text

    if "Taille : 180" in patient_details:
        print("✅ Mise à jour réussie du patient")
    else:
        print("❌ Échec de la mise à jour du patient")
        raise Exception("Les modifications n'ont pas été enregistrées")

    # Naviguer vers la liste des patients
    list_button = driver.find_element(By.CSS_SELECTOR, "button[routerlink='/patients']")
    list_button.click()
    time.sleep(3)

    # SUPPRESSION (DELETE)
    print("=== TEST DE SUPPRESSION ===")

    # Trouver et cliquer sur le bouton de suppression du patient récemment créé
    patient_items = driver.find_elements(By.CSS_SELECTOR, "mat-list-item")

    for item in patient_items:
        if test_patient_nom in item.text and test_patient_prenom in item.text:
            delete_button = item.find_element(By.CSS_SELECTOR, "button[matlistitemmeta]")
            delete_button.click()
            break
    else:
        print("❌ Patient non trouvé dans la liste")
        raise Exception("Patient non trouvé dans la liste")

    # Confirmer la suppression (dans SweetAlert)
    time.sleep(1)
    driver.save_screenshot("6_delete_confirmation.png")

    confirm_button = wait.until(EC.element_to_be_clickable((By.CSS_SELECTOR, ".swal2-confirm")))
    confirm_button.click()
    time.sleep(1)

    ok_button = wait.until(EC.element_to_be_clickable((By.CSS_SELECTOR, ".swal2-confirm")))
    ok_button.click()
    time.sleep(5)

    driver.save_screenshot("7_delete_success.png")

    # Vérifier que le patient a été supprimé
    patient_items = driver.find_elements(By.CSS_SELECTOR, "mat-list-item")
    deleted = True

    for item in patient_items:
        if test_patient_nom in item.text and test_patient_prenom in item.text:
            deleted = False
            break

    if deleted:
        print("✅ Suppression réussie du patient")
    else:
        print("❌ Échec de la suppression du patient")
        raise Exception("Le patient n'a pas été supprimé")

    # Déconnexion
    print("=== TEST DE DÉCONNEXION ===")
    logout_button = driver.find_element(By.ID, "logout")
    logout_button.click()
    time.sleep(3)

    # Vérifier qu'on est bien déconnecté (redirection vers la page de connexion)
    if "login" in driver.current_url:
        print("✅ Déconnexion réussie")
    else:
        print("❌ Échec de la déconnexion")
        raise Exception("La déconnexion a échoué")

    driver.save_screenshot("8_logout_success.png")

    success = True
    print("=== TESTS CRUD TERMINÉS AVEC SUCCÈS ===")

except Exception as e:
    print(f"❌ Erreur lors des tests CRUD: {str(e)}")
    driver.save_screenshot("error_screenshot.png")

finally:
    time.sleep(2)
    driver.quit()

    if success:
        print("✅ Tests CRUD globaux réussis!")
        exit(0)
    else:
        print("❌ Tests CRUD globaux échoués")
        exit(1)
