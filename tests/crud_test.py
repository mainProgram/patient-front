# tests/crud_test.py
import sys
import time
import random
from datetime import datetime
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.common.keys import Keys

options = Options()
options.add_argument("--no-sandbox")
options.add_argument("--disable-dev-shm-usage")
options.add_argument("--window-size=1920,1080")

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
random_num = random.randint(1000, 9999)
test_patient_nom = f"Test{timestamp}"
test_patient_prenom = f"Patient{random_num}"

try:
    print("=== DÉBUT DES TESTS CRUD ===")

    # CONNEXION
    print("=== TEST DE CONNEXION ===")
    print(f"🚀 Ouverture de la page: {app_url}")
    driver.get(app_url)
    time.sleep(5)

    # Faire une capture d'écran pour le débogage
    driver.save_screenshot("01_login_page.png")

    # Trouver les champs de formulaire et le bouton de connexion
    username_input = wait.until(EC.element_to_be_clickable((By.NAME, "username")))
    password_input = wait.until(EC.element_to_be_clickable((By.NAME, "password")))

    username_input.clear()
    username_input.send_keys("admin")
    time.sleep(1)

    password_input.clear()
    password_input.send_keys("password123")
    time.sleep(1)

    # Trouver et cliquer sur le bouton de connexion
    submit_button = wait.until(EC.element_to_be_clickable((By.CSS_SELECTOR, "button[type='submit']")))
    driver.save_screenshot("02_before_login.png")
    submit_button.click()
    time.sleep(5)

    # Vérifier si on est connecté (vérifier la présence de la barre d'outils)
    toolbar = wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, "mat-toolbar")))
    print("✅ Connexion réussie")
    driver.save_screenshot("03_after_login.png")

    # CRÉATION (CREATE)
    print("=== TEST DE CRÉATION ===")

    # Naviguer vers le formulaire d'ajout en cliquant sur l'icône d'ajout
    add_button = wait.until(EC.element_to_be_clickable((By.CSS_SELECTOR, "button[routerlink='/patients/add']")))
    add_button.click()
    time.sleep(3)

    # Attendre que le formulaire de création soit chargé
    wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, "form.patient-form")))
    driver.save_screenshot("04_create_form.png")

    # Remplir le formulaire
    nom_input = wait.until(EC.element_to_be_clickable((By.CSS_SELECTOR, "input[formcontrolname='nom']")))
    prenom_input = wait.until(EC.element_to_be_clickable((By.CSS_SELECTOR, "input[formcontrolname='prenom']")))

    nom_input.clear()
    nom_input.send_keys(test_patient_nom)
    time.sleep(1)

    prenom_input.clear()
    prenom_input.send_keys(test_patient_prenom)
    time.sleep(1)

    # Sélectionner le sexe
    sexe_select = wait.until(EC.element_to_be_clickable((By.CSS_SELECTOR, "mat-select[formcontrolname='sexe']")))
    sexe_select.click()
    time.sleep(1)

    sexe_option = wait.until(EC.element_to_be_clickable((By.XPATH, "//mat-option[@value='HOMME']")))
    sexe_option.click()
    time.sleep(1)

    # Remplir la date de naissance (en utilisant JavaScript pour éviter les problèmes avec le datepicker)
    date_input = driver.find_element(By.CSS_SELECTOR, "input[formcontrolname='dateNaissance']")
    driver.execute_script("arguments[0].value = '2000-01-01'; arguments[0].dispatchEvent(new Event('input')); arguments[0].dispatchEvent(new Event('change'));", date_input)

    # Remplir la taille et le poids
    taille_input = wait.until(EC.element_to_be_clickable((By.CSS_SELECTOR, "input[formcontrolname='taille']")))
    poids_input = wait.until(EC.element_to_be_clickable((By.CSS_SELECTOR, "input[formcontrolname='poids']")))

    taille_input.clear()
    taille_input.send_keys("175")
    time.sleep(1)

    poids_input.clear()
    poids_input.send_keys("70")
    time.sleep(1)

    # Remplir un contact
    type_contact_select = wait.until(EC.element_to_be_clickable((By.CSS_SELECTOR, "mat-select[formcontrolname='type']")))
    type_contact_select.click()
    time.sleep(1)

    email_option = wait.until(EC.element_to_be_clickable((By.XPATH, "//mat-option[@value='EMAIL']")))
    email_option.click()
    time.sleep(1)

    # Sortir du menu déroulant en cliquant ailleurs
    actions = ActionChains(driver)
    actions.send_keys(Keys.ESCAPE).perform()
    time.sleep(1)

    contact_input = wait.until(EC.element_to_be_clickable((By.CSS_SELECTOR, "input[formcontrolname='contact']")))
    contact_input.clear()
    contact_input.send_keys(f"test{random_num}@example.com")
    time.sleep(1)

    # Soumettre le formulaire
    driver.save_screenshot("05_filled_form.png")
    submit_form_button = wait.until(EC.element_to_be_clickable((By.CSS_SELECTOR, "button[type='submit']")))

    # Faire défiler jusqu'au bouton si nécessaire
    driver.execute_script("arguments[0].scrollIntoView(true);", submit_form_button)
    time.sleep(1)

    submit_form_button.click()
    time.sleep(5)

    # Attendre la redirection vers la page de détails
    try:
        wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, "mat-card-title")))
        driver.save_screenshot("06_create_success.png")

        # Vérifier que les données ont été créées correctement
        card_title = driver.find_element(By.CSS_SELECTOR, "mat-card-title").text
        print(f"Titre de la carte: {card_title}")

        if test_patient_prenom in card_title and test_patient_nom in card_title:
            print(f"✅ Création réussie du patient: {test_patient_prenom} {test_patient_nom}")
        else:
            print("❌ Échec de la création du patient - nom non trouvé dans les détails")

        # Obtenir l'ID du patient depuis l'URL
        current_url = driver.current_url
        patient_id = current_url.split("/")[-1]
        print(f"ID du patient créé: {patient_id}")

        # LECTURE (READ)
        print("=== TEST DE LECTURE ===")

        # Vérifier que les informations sont correctement affichées
        wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, "mat-card-content")))
        patient_details = driver.find_element(By.CSS_SELECTOR, "mat-card-content").text

        if "Taille : 175" in patient_details and "Poids : 70" in patient_details:
            print("✅ Lecture réussie des détails du patient")
        else:
            print("❌ Échec de la lecture des détails du patient")
            print(f"Contenu trouvé: {patient_details}")

        # MISE À JOUR (UPDATE)
        print("=== TEST DE MISE À JOUR ===")

        # Cliquer sur le bouton de modification
        edit_button = wait.until(EC.element_to_be_clickable((By.XPATH, "//button[contains(text(), 'Modifier')]")))
        edit_button.click()
        time.sleep(3)

        # Attendre que le formulaire de modification soit chargé
        wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, "form.patient-form")))
        driver.save_screenshot("07_update_form.png")

        # Modifier la taille
        taille_input = wait.until(EC.element_to_be_clickable((By.CSS_SELECTOR, "input[formcontrolname='taille']")))
        taille_input.clear()
        taille_input.send_keys("180")
        time.sleep(1)

        # Enregistrer la modification
        submit_form_button = wait.until(EC.element_to_be_clickable((By.CSS_SELECTOR, "button[type='submit']")))

        # Faire défiler jusqu'au bouton si nécessaire
        driver.execute_script("arguments[0].scrollIntoView(true);", submit_form_button)
        time.sleep(1)

        submit_form_button.click()
        time.sleep(5)

        # Attendre la redirection vers la page de détails
        wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, "mat-card-title")))
        driver.save_screenshot("08_update_success.png")

        # Vérifier que les modifications ont été enregistrées
        wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, "mat-card-content")))
        patient_details = driver.find_element(By.CSS_SELECTOR, "mat-card-content").text

        if "Taille : 180" in patient_details:
            print("✅ Mise à jour réussie du patient")
        else:
            print("❌ Échec de la mise à jour du patient")
            print(f"Contenu trouvé: {patient_details}")

        # SUPPRESSION (DELETE)
        print("=== TEST DE SUPPRESSION ===")

        # Naviguer vers la liste des patients
        list_button = wait.until(EC.element_to_be_clickable((By.CSS_SELECTOR, "button[routerlink='/patients']")))
        list_button.click()
        time.sleep(5)

        driver.save_screenshot("09_patient_list.png")

        # Trouver notre patient créé dans la liste
        patient_items = driver.find_elements(By.CSS_SELECTOR, "mat-list-item")
        patient_found = False

        for item in patient_items:
            item_text = item.text
            print(f"Patient dans la liste: {item_text}")

            if test_patient_nom in item_text and test_patient_prenom in item_text:
                patient_found = True
                # Trouver le bouton de suppression pour cet élément
                delete_button = item.find_element(By.CSS_SELECTOR, "button[matlistitemmeta]")

                # Faire défiler jusqu'au bouton si nécessaire
                driver.execute_script("arguments[0].scrollIntoView(true);", delete_button)
                time.sleep(1)

                driver.save_screenshot("10_before_delete.png")
                delete_button.click()
                break

        if not patient_found:
            print("❌ Patient non trouvé dans la liste")
            raise Exception("Patient non trouvé dans la liste")

        # Confirmer la suppression dans SweetAlert
        time.sleep(2)
        driver.save_screenshot("11_delete_confirmation.png")

        # Cliquer sur le bouton de confirmation
        confirm_button = wait.until(EC.element_to_be_clickable((By.CSS_SELECTOR, ".swal2-confirm")))
        confirm_button.click()
        time.sleep(2)

        # Cliquer sur le bouton OK du message de succès
        success_button = wait.until(EC.element_to_be_clickable((By.CSS_SELECTOR, ".swal2-confirm")))
        success_button.click()
        time.sleep(5)

        driver.save_screenshot("12_after_delete.png")

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

        # DÉCONNEXION
        print("=== TEST DE DÉCONNEXION ===")

        # Cliquer sur le bouton de déconnexion
        logout_button = wait.until(EC.element_to_be_clickable((By.ID, "logout")))
        logout_button.click()
        time.sleep(3)

        # Vérifier qu'on est bien déconnecté (redirection vers la page de connexion)
        wait.until(EC.presence_of_element_located((By.NAME, "username")))
        driver.save_screenshot("13_logout_success.png")

        print("✅ Déconnexion réussie")
        success = True

    except Exception as e:
        print(f"❌ Erreur lors des tests après la création: {str(e)}")
        driver.save_screenshot("error_details.png")

    print("=== TESTS CRUD TERMINÉS ===")

except Exception as e:
    print(f"❌ Erreur lors des tests CRUD: {str(e)}")
    driver.save_screenshot("error_global.png")

finally:
    time.sleep(2)
    driver.quit()

    if success:
        print("✅ Tests CRUD globaux réussis!")
        exit(0)
    else:
        print("❌ Tests CRUD globaux échoués")
        exit(1)
