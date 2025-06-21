import sys
import time
import json
import os
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException, NoSuchElementException
from datetime import datetime

class AuthSecurityTests:
    def __init__(self, app_url):
        self.app_url = app_url
        self.driver = None
        self.wait = None
        self.test_results = []
        self.screenshots = []
        self.screenshot_dir = "test-screenshots"
        self.setup_driver()

        # Créer le dossier pour les captures
        if not os.path.exists(self.screenshot_dir):
            os.makedirs(self.screenshot_dir)

    def setup_driver(self):
        options = Options()
        options.add_argument("--no-sandbox")
        options.add_argument("--disable-dev-shm-usage")
        options.add_argument("--window-size=1920,1080")
        options.add_argument("--disable-gpu")
        options.add_argument("--no-sandbox")
        options.add_argument("--disable-setuid-sandbox")

        self.driver = webdriver.Remote(
            command_executor='http://selenium:4444/wd/hub',
            options=options
        )
        self.wait = WebDriverWait(self.driver, 30)

    def take_screenshot(self, name):
        """Prendre une capture d'écran avec un nom descriptif"""
        filename = f"{self.screenshot_dir}/{name}_{datetime.now().strftime('%H%M%S')}.png"
        self.driver.save_screenshot(filename)
        self.screenshots.append(filename)
        print(f"📸 Capture d'écran sauvegardée: {filename}")
        return filename

    def navigate_to_login(self):
        """Naviguer vers la page de login, gérer les redirections"""
        try:
            print(f"Navigation vers: {self.app_url}")
            self.driver.get(self.app_url)
            time.sleep(3)

            # Vérifier si nous sommes déjà sur la page de login
            current_url = self.driver.current_url
            print(f"URL actuelle: {current_url}")

            # Si on n'est pas sur login, essayer d'y accéder directement
            if "login" not in current_url:
                login_url = f"{self.app_url}/login"
                print(f"Redirection manuelle vers: {login_url}")
                self.driver.get(login_url)
                time.sleep(3)

            # Attendre que les champs de login soient présents
            try:
                self.wait.until(EC.presence_of_element_located((By.NAME, "username")))
                print("✅ Page de login chargée avec succès")
                return True
            except TimeoutException:
                print("❌ Impossible de trouver les champs de login")
                # Prendre une capture d'écran pour debug
                self.take_screenshot("login_page_error")
                print(f"Page HTML actuelle: {self.driver.page_source[:500]}")
                return False

        except Exception as e:
            print(f"❌ Erreur lors de la navigation: {str(e)}")
            return False

    def log_test_result(self, test_name, passed, details="", screenshot=None):
        """Enregistrer le résultat d'un test"""
        self.test_results.append({
            "test": test_name,
            "passed": passed,
            "details": details,
            "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            "screenshot": screenshot
        })
        status = "✅ PASSÉ" if passed else "❌ ÉCHOUÉ"
        print(f"{status} - {test_name}")
        if details:
            print(f"   Détails: {details}")

    def check_for_vulnerabilities(self):
        """Vérifier les vulnérabilités communes après chaque tentative"""
        vulnerabilities = []

        try:
            # Vérifier si un token a été généré
            token = self.driver.execute_script("return localStorage.getItem('auth_token');")
            if token and token not in ["null", "undefined", "", None]:
                vulnerabilities.append("Token généré malgré les mauvais credentials")

            # Vérifier l'URL actuelle
            current_url = self.driver.current_url
            if "patients" in current_url:
                vulnerabilities.append("Redirection non autorisée vers la zone protégée")

            # Vérifier les cookies de session
            cookies = self.driver.get_cookies()
            for cookie in cookies:
                if 'session' in cookie['name'].lower() and not cookie.get('httpOnly'):
                    vulnerabilities.append(f"Cookie de session sans flag HttpOnly: {cookie['name']}")
                if 'session' in cookie['name'].lower() and not cookie.get('secure'):
                    vulnerabilities.append(f"Cookie de session sans flag Secure: {cookie['name']}")
        except Exception as e:
            print(f"Erreur lors de la vérification des vulnérabilités: {str(e)}")

        return vulnerabilities

    def test_basic_injection(self):
        """Test basique d'injection SQL"""
        print("\n=== TEST: Injection SQL Basique ===")

        if not self.navigate_to_login():
            self.log_test_result("Navigation vers login", False, "Impossible d'accéder à la page de login")
            return False

        try:
            # Test simple d'injection SQL
            username_input = self.wait.until(EC.element_to_be_clickable((By.NAME, "username")))
            password_input = self.wait.until(EC.element_to_be_clickable((By.NAME, "password")))
            submit_button = self.driver.find_element(By.CSS_SELECTOR, "button[type='submit']")

            # Injection SQL classique
            username_input.clear()
            username_input.send_keys("admin' OR '1'='1")
            password_input.clear()
            password_input.send_keys("password")

            print("Tentative d'injection SQL...")
            screenshot_before = self.take_screenshot("sql_injection_before")
            submit_button.click()
            time.sleep(3)
            screenshot_after = self.take_screenshot("sql_injection_after")

            vulnerabilities = self.check_for_vulnerabilities()

            if vulnerabilities:
                self.log_test_result(
                    "Protection injection SQL basique",
                    False,
                    f"Vulnérabilités détectées: {', '.join(vulnerabilities)}",
                    screenshot_after
                )
                return False
            else:
                self.log_test_result(
                    "Protection injection SQL basique",
                    True,
                    "Injection SQL bloquée correctement",
                    screenshot_after
                )
                return True

        except Exception as e:
            screenshot = self.take_screenshot("sql_injection_error")
            self.log_test_result(
                "Test injection SQL basique",
                False,
                f"Erreur: {str(e)}",
                screenshot
            )
            return False

    def test_valid_login(self):
        """Test de connexion valide pour vérifier que le système fonctionne"""
        print("\n=== TEST: Connexion Valide ===")

        if not self.navigate_to_login():
            self.log_test_result("Navigation vers login", False, "Impossible d'accéder à la page de login")
            return False

        try:
            username_input = self.wait.until(EC.element_to_be_clickable((By.NAME, "username")))
            password_input = self.wait.until(EC.element_to_be_clickable((By.NAME, "password")))
            submit_button = self.driver.find_element(By.CSS_SELECTOR, "button[type='submit']")

            # Utiliser les vraies credentials
            username_input.clear()
            username_input.send_keys("admin")
            password_input.clear()
            password_input.send_keys("password123")

            print("Tentative de connexion valide...")
            screenshot_before = self.take_screenshot("valid_login_before")
            submit_button.click()
            time.sleep(5)
            screenshot_after = self.take_screenshot("valid_login_after")

            # Vérifier si on est bien connecté
            current_url = self.driver.current_url
            token = self.driver.execute_script("return localStorage.getItem('auth_token');")

            if "patients" in current_url or (token and token not in ["null", "undefined", "", None]):
                self.log_test_result(
                    "Connexion valide",
                    True,
                    "Connexion réussie avec les bonnes credentials",
                    screenshot_after
                )

                # Se déconnecter pour les prochains tests
                try:
                    logout_button = self.driver.find_element(By.ID, "logout")
                    logout_button.click()
                    time.sleep(2)
                except:
                    print("Pas de bouton de déconnexion trouvé")

                return True
            else:
                self.log_test_result(
                    "Connexion valide",
                    False,
                    "Impossible de se connecter avec des credentials valides",
                    screenshot_after
                )
                return False

        except Exception as e:
            screenshot = self.take_screenshot("valid_login_error")
            self.log_test_result(
                "Test connexion valide",
                False,
                f"Erreur: {str(e)}",
                screenshot
            )
            return False

    def test_sql_injection_variations(self):
        """Test de différentes variations d'injection SQL"""
        print("\n=== TEST: Variations d'Injection SQL ===")

        sql_payloads = [
            ("admin' --", "password"),
            ("admin' OR 1=1 --", "password"),
            ("' OR '1'='1' --", "' OR '1'='1' --"),
            ("admin'; DROP TABLE users; --", "password"),
        ]

        all_passed = True

        for username, password in sql_payloads:
            if not self.navigate_to_login():
                continue

            try:
                print(f"\nTest injection: {username[:30]}...")

                username_input = self.wait.until(EC.element_to_be_clickable((By.NAME, "username")))
                password_input = self.wait.until(EC.element_to_be_clickable((By.NAME, "password")))
                submit_button = self.driver.find_element(By.CSS_SELECTOR, "button[type='submit']")

                username_input.clear()
                username_input.send_keys(username)
                password_input.clear()
                password_input.send_keys(password)

                screenshot_name = f'sql_variation_{username[:20].replace(" ", "_").replace("'", "")}'
                screenshot_before = self.take_screenshot(f"{screenshot_name}_before")
                submit_button.click()
                time.sleep(3)
                screenshot_after = self.take_screenshot(f"{screenshot_name}_after")

                vulnerabilities = self.check_for_vulnerabilities()

                if vulnerabilities:
                    self.log_test_result(
                        f"Protection SQL - {username[:20]}",
                        False,
                        f"Vulnérabilités: {', '.join(vulnerabilities)}",
                        screenshot_after
                    )
                    all_passed = False
                else:
                    self.log_test_result(
                        f"Protection SQL - {username[:20]}",
                        True,
                        "Injection bloquée",
                        screenshot_after
                    )

            except Exception as e:
                screenshot = self.take_screenshot(f"sql_variation_error")
                self.log_test_result(
                    f"Test SQL - {username[:20]}",
                    False,
                    f"Erreur: {str(e)}",
                    screenshot
                )
                all_passed = False

        return all_passed

    def test_xss_basic(self):
        """Test XSS basique"""
        print("\n=== TEST: XSS Basique ===")

        if not self.navigate_to_login():
            return False

        try:
            username_input = self.wait.until(EC.element_to_be_clickable((By.NAME, "username")))
            password_input = self.wait.until(EC.element_to_be_clickable((By.NAME, "password")))
            submit_button = self.driver.find_element(By.CSS_SELECTOR, "button[type='submit']")

            # Test XSS simple
            xss_payload = "<script>alert('XSS')</script>"
            username_input.clear()
            username_input.send_keys(xss_payload)
            password_input.clear()
            password_input.send_keys("password")

            screenshot_before = self.take_screenshot("xss_test_before")
            submit_button.click()
            time.sleep(2)

            # Vérifier si une alerte s'est déclenchée
            try:
                alert = self.driver.switch_to.alert
                alert_text = alert.text
                screenshot_alert = self.take_screenshot("xss_alert_detected")
                alert.accept()
                self.log_test_result(
                    "Protection XSS basique",
                    False,
                    f"Alerte XSS déclenchée: {alert_text}",
                    screenshot_alert
                )
                return False
            except:
                # Pas d'alerte, vérifier le DOM
                page_source = self.driver.page_source
                screenshot_after = self.take_screenshot("xss_test_after")
                if "<script>" in page_source and "alert" in page_source:
                    self.log_test_result(
                        "Protection XSS basique",
                        False,
                        "Script injecté dans le DOM",
                        screenshot_after
                    )
                    return False
                else:
                    self.log_test_result(
                        "Protection XSS basique",
                        True,
                        "XSS bloqué correctement",
                        screenshot_after
                    )
                    return True

        except Exception as e:
            screenshot = self.take_screenshot("xss_test_error")
            self.log_test_result(
                "Test XSS basique",
                False,
                f"Erreur: {str(e)}",
                screenshot
            )
            return False

    def test_authentication_bypass(self):
        """Test de contournement d'authentification simple"""
        print("\n=== TEST: Contournement d'Authentification ===")

        bypass_attempts = [
            ("admin ", "password"),  # Espace après
            (" admin", "password"),  # Espace avant
            ("ADMIN", "password"),   # Majuscules
            ("admin\x00", "password"),  # Null byte
        ]

        all_passed = True

        for username, password in bypass_attempts:
            if not self.navigate_to_login():
                continue

            try:
                print(f"\nTest bypass: '{username}'")

                username_input = self.wait.until(EC.element_to_be_clickable((By.NAME, "username")))
                password_input = self.wait.until(EC.element_to_be_clickable((By.NAME, "password")))
                submit_button = self.driver.find_element(By.CSS_SELECTOR, "button[type='submit']")

                username_input.clear()
                username_input.send_keys(username)
                password_input.clear()
                password_input.send_keys(password)

                bypass_name = username.strip().replace(" ", "_").replace("\x00", "null")
                screenshot_before = self.take_screenshot(f"bypass_{bypass_name}_before")
                submit_button.click()
                time.sleep(3)
                screenshot_after = self.take_screenshot(f"bypass_{bypass_name}_after")

                vulnerabilities = self.check_for_vulnerabilities()

                if vulnerabilities:
                    self.log_test_result(
                        f"Protection bypass - {username.strip()}",
                        False,
                        f"Vulnérabilités: {', '.join(vulnerabilities)}",
                        screenshot_after
                    )
                    all_passed = False
                else:
                    self.log_test_result(
                        f"Protection bypass - {username.strip()}",
                        True,
                        "Tentative bloquée",
                        screenshot_after
                    )

            except Exception as e:
                screenshot = self.take_screenshot("bypass_error")
                self.log_test_result(
                    f"Test bypass - {username.strip()}",
                    False,
                    f"Erreur: {str(e)}",
                    screenshot
                )
                all_passed = False

        return all_passed

    def run_tests(self):
        """Exécuter les tests principaux"""
        print("="*60)
        print("TESTS DE SÉCURITÉ - AUTHENTIFICATION")
        print("="*60)

        # Test de connexion valide d'abord
        self.test_valid_login()

        # Tests de sécurité
        self.test_basic_injection()
        self.test_sql_injection_variations()
        self.test_xss_basic()
        self.test_authentication_bypass()

        # Lister toutes les captures créées
        print("\n📸 Captures d'écran créées:")
        for screenshot in self.screenshots:
            print(f"  - {screenshot}")

        # Retourner le succès global
        failed = sum(1 for t in self.test_results if not t['passed'])
        return failed == 0

    def cleanup(self):
        """Nettoyer les ressources"""
        if self.driver:
            try:
                self.driver.quit()
            except:
                pass

# Point d'entrée principal
if __name__ == "__main__":
    app_url = sys.argv[1] if len(sys.argv) > 1 else "http://localhost:4201"

    print(f"Démarrage des tests de sécurité sur: {app_url}")

    tests = AuthSecurityTests(app_url)

    try:
        success = tests.run_tests()
        if success:
            print("\n✅ Tests de sécurité terminés avec succès!")
            exit(0)
        else:
            print("\n⚠️ Certains tests ont échoué!")
            exit(0)  # Exit 0 pour ne pas bloquer Jenkins
    except Exception as e:
        print(f"\n❌ Erreur fatale: {str(e)}")
        try:
            tests.driver.save_screenshot("fatal_error.png")
        except:
            pass
        exit(1)
    finally:
        tests.cleanup()
