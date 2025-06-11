import sys
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import time

class AuthSecurityTests:
    def __init__(self, app_url):
        self.app_url = app_url
        self.driver = None
        self.wait = None
        self.setup_driver()

    def setup_driver(self):
        options = Options()
        options.add_argument("--no-sandbox")
        options.add_argument("--disable-dev-shm-usage")

        self.driver = webdriver.Remote(
            command_executor='http://selenium:4444/wd/hub',
            options=options
        )
        self.wait = WebDriverWait(self.driver, 30)

    def test_valid_login(self):
        """Test de connexion avec des credentials valides"""
        print("=== TEST: Connexion Valide ===")
        try:
            self.driver.get(self.app_url)
            time.sleep(8)

            print("Recherche du champ nom d'utilisateur")
            username_input = self.wait.until(EC.element_to_be_clickable((By.NAME, "username")))
            time.sleep(3)

            print("Recherche du champ mot de passe")
            password_input = self.wait.until(EC.element_to_be_clickable((By.NAME, "password")))
            time.sleep(3)

            print("Recherche du bouton de soumission")
            submit_button = self.driver.find_element(By.CSS_SELECTOR, "button[type='submit']")
            time.sleep(3)

            print("Saisie du nom d'utilisateur")
            username_input.send_keys("admin")
            time.sleep(3)

            print("Saisie du mot de passe")
            password_input.send_keys("password123")
            time.sleep(3)

            print("Soumission du formulaire de connexion")
            submit_button.click()

            try:
                self.wait.until(EC.url_contains("/patients"))
                print("Redirection vers la page patients détectée")

                print("Recherche et clic sur le bouton de déconnexion")
                logout_button = self.driver.find_element(By.ID, "logout")
                time.sleep(3)
                logout_button.click()
                time.sleep(5)

                print("Test de connexion valide réussi")
                return True

            except:
                error_msg = self.driver.find_elements(By.CLASS_NAME, "error-message")
                if error_msg:
                    print("Message d'erreur trouvé:", error_msg[0].text)
                    return False
                print("Aucune redirection détectée")
                return False

        except Exception as e:
            print("Erreur lors du test de connexion valide:", str(e))
            return False

    def test_invalid_credentials(self):
        """Test de sécurité: tentatives de connexion avec des credentials invalides"""
        print("=== TEST: Credentials Invalides ===")

        invalid_combinations = [
            ("admin", "wrongpassword"),
            ("wronguser", "password123"),
            ("", ""),
            ("admin' OR '1'='1", "password"),
        ]

        for username, password in invalid_combinations:
            try:
                print(f"Test credentials: '{username}' / '{password}'")

                self.driver.get(self.app_url)
                time.sleep(3)

                username_input = self.wait.until(EC.element_to_be_clickable((By.NAME, "username")))
                password_input = self.wait.until(EC.element_to_be_clickable((By.NAME, "password")))
                submit_button = self.driver.find_element(By.CSS_SELECTOR, "button[type='submit']")

                username_input.clear()
                username_input.send_keys(username)
                password_input.clear()
                password_input.send_keys(password)

                submit_button.click()
                time.sleep(5)  # Délai augmenté pour laisser l'API répondre

                # Vérification 1: URL - doit rester sur login
                current_url = self.driver.current_url

                # Vérification 2: Pas de token stocké
                token = self.driver.execute_script("return localStorage.getItem('auth_token');")

                # Vérification 3: Logs d'erreur dans le navigateur
                try:
                    logs = self.driver.get_log('browser')
                    for log in logs:
                        if 'error' in log['message'].lower():
                            print(f"Erreur JavaScript détectée: {log['message']}")
                except:
                    print("Impossible de récupérer les logs du navigateur")

                # Vérification 4: Message d'erreur visible
                error_elements = self.driver.find_elements(By.CLASS_NAME, "error-message")

                # Analyse des résultats
                if token:
                    print(f"SÉCURITÉ COMPROMISE: Token trouvé avec mauvais credentials: {token[:20]}...")
                    return False

                if "patients" in current_url:
                    print(f"SÉCURITÉ COMPROMISE: Redirection vers patients avec mauvais credentials!")
                    return False

                if "login" in current_url or current_url == self.app_url:
                    print(f"Bon comportement: Reste sur la page de login")

                    if error_elements:
                        print(f"Message d'erreur affiché: {error_elements[0].text}")
                    else:
                        print("Aucun message d'erreur visible à l'utilisateur")
                else:
                    print(f"Comportement inattendu: URL actuelle = {current_url}")
                    return False

            except Exception as e:
                print(f"Erreur lors du test credentials invalides: {str(e)}")
                return False

        print("Test des credentials invalides réussi")
        return True


    def run_all_tests(self):
        """Exécuter tous les tests de sécurité"""
        print("Début des tests de sécurité d'authentification")

        test_results = []

        # Test 1: Connexion valide
        valid_login_result = self.test_valid_login()
        test_results.append(("Connexion valide", valid_login_result))

        # Test 2: Credentials invalides
        invalid_creds_result = self.test_invalid_credentials()
        test_results.append(("Credentials invalides", invalid_creds_result))

        # Rapport final
        print("\n" + "="*50)
        print("RAPPORT DES TESTS DE SÉCURITÉ")
        print("="*50)

        passed = 0
        total = len(test_results)

        for test_name, result in test_results:
            status = "PASSÉ" if result else "ÉCHOUÉ"
            print(f"{test_name}: {status}")
            if result:
                passed += 1

        print(f"\nRésultats: {passed}/{total} tests passés")

        if passed == total:
            print("TOUS LES TESTS DE SÉCURITÉ SONT PASSÉS!")
            return True
        else:
            print("CERTAINS TESTS DE SÉCURITÉ ONT ÉCHOUÉ!")
            return False

    def cleanup(self):
        if self.driver:
            time.sleep(5)
            self.driver.quit()

# Point d'entrée principal
if __name__ == "__main__":
    app_url = sys.argv[1] if len(sys.argv) > 1 else "http://localhost:4201"

    security_tests = AuthSecurityTests(app_url)

    try:
        success = security_tests.run_all_tests()
        if success:
            print("Test réussi: Connexion et sécurité validées")
            exit(0)
        else:
            print("Échec des tests de sécurité")
            exit(1)
    except Exception as e:
        print("Échec du test:", str(e))
        security_tests.driver.save_screenshot("error_screenshot.png")
        exit(1)
    finally:
        security_tests.cleanup()
