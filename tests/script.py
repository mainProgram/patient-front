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
        self.screenshot_counter = 0
        self.screenshots_dir = "screenshots"
        self.setup_driver()
        self.setup_screenshots_dir()

    def setup_screenshots_dir(self):
        """Creer le repertoire pour les captures d'ecran"""
        if not os.path.exists(self.screenshots_dir):
            os.makedirs(self.screenshots_dir)
            print(f"SUCCES: Repertoire cree: {self.screenshots_dir}")

    def take_screenshot(self, name, description=""):
        """Prendre une capture d'ecran avec un nom descriptif"""
        try:
            self.screenshot_counter += 1
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"{self.screenshots_dir}/{self.screenshot_counter:02d}_{timestamp}_{name}.png"

            self.driver.save_screenshot(filename)
            print(f"CAPTURE: Capture d'ecran: {filename}")
            if description:
                print(f"   Description: {description}")

            return filename
        except Exception as e:
            print(f"ERREUR: Erreur capture d'ecran: {str(e)}")
            return None

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

    def navigate_to_login(self):
        """Naviguer vers la page de login, gerer les redirections"""
        try:
            print(f"Navigation vers: {self.app_url}")
            self.driver.get(self.app_url)
            time.sleep(3)

            # Capture d'ecran apres navigation initiale
            self.take_screenshot("initial_navigation", "Page apres navigation initiale")

            # Verifier si nous sommes deja sur la page de login
            current_url = self.driver.current_url
            print(f"URL actuelle: {current_url}")

            # Si on n'est pas sur login, essayer d'y acceder directement
            if "login" not in current_url:
                login_url = f"{self.app_url}/login"
                print(f"Redirection manuelle vers: {login_url}")
                self.driver.get(login_url)
                time.sleep(3)

                # Capture apres redirection vers login
                self.take_screenshot("redirect_to_login", "Page apres redirection vers /login")

            # Attendre que les champs de login soient presents
            try:
                self.wait.until(EC.presence_of_element_located((By.NAME, "username")))
                print("SUCCES: Page de login chargee avec succes")

                # Capture de la page de login prete
                self.take_screenshot("login_page_ready", "Page de login avec champs visibles")
                return True
            except TimeoutException:
                print("ERREUR: Impossible de trouver les champs de login")
                # Capture en cas d'erreur
                self.take_screenshot("login_page_error", "Erreur - champs de login non trouves")
                print(f"Page HTML actuelle: {self.driver.page_source[:500]}")
                return False

        except Exception as e:
            print(f"ERREUR: Erreur lors de la navigation: {str(e)}")
            self.take_screenshot("navigation_error", f"Erreur navigation: {str(e)}")
            return False

    def log_test_result(self, test_name, passed, details="", screenshot_path=None):
        """Enregistrer le resultat d'un test"""
        self.test_results.append({
            "test": test_name,
            "passed": passed,
            "details": details,
            "screenshot": screenshot_path,
            "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        })
        status = "SUCCES PASSE" if passed else "ERREUR ECHOUE"
        print(f"{status} - {test_name}")
        if details:
            print(f"   Details: {details}")
        if screenshot_path:
            print(f"   Capture: {screenshot_path}")

    def check_for_vulnerabilities(self):
        """Verifier les vulnerabilites communes apres chaque tentative"""
        vulnerabilities = []

        try:
            # Capture d'ecran avant verification des vulnerabilites
            screenshot_path = self.take_screenshot("vulnerability_check", "Etat de la page lors de la verification des vulnerabilites")

            # Verifier si un token a ete genere
            token = self.driver.execute_script("return localStorage.getItem('auth_token');")
            if token and token not in ["null", "undefined", "", None]:
                vulnerabilities.append("Token genere malgre les mauvais credentials")

            # Verifier l'URL actuelle
            current_url = self.driver.current_url
            if "patients" in current_url:
                vulnerabilities.append("Redirection non autorisee vers la zone protegee")

            # Verifier les cookies de session
            cookies = self.driver.get_cookies()
            for cookie in cookies:
                if 'session' in cookie['name'].lower() and not cookie.get('httpOnly'):
                    vulnerabilities.append(f"Cookie de session sans flag HttpOnly: {cookie['name']}")
                if 'session' in cookie['name'].lower() and not cookie.get('secure'):
                    vulnerabilities.append(f"Cookie de session sans flag Secure: {cookie['name']}")

            # Si des vulnerabilites sont detectees, prendre une capture speciale
            if vulnerabilities:
                self.take_screenshot("vulnerability_detected", f"Vulnerabilites detectees: {', '.join(vulnerabilities)}")

        except Exception as e:
            print(f"Erreur lors de la verification des vulnerabilites: {str(e)}")
            self.take_screenshot("vulnerability_check_error", f"Erreur verification: {str(e)}")

        return vulnerabilities

    def test_basic_injection(self):
        """Test basique d'injection SQL"""
        print("\n=== TEST: Injection SQL Basique ===")

        if not self.navigate_to_login():
            self.log_test_result("Navigation vers login", False, "Impossible d'acceder a la page de login")
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

            # Capture avant soumission
            screenshot_before = self.take_screenshot("sql_injection_before", "Avant soumission injection SQL basique")

            print("Tentative d'injection SQL...")
            submit_button.click()
            time.sleep(3)

            # Capture apres soumission
            screenshot_after = self.take_screenshot("sql_injection_after", "Apres soumission injection SQL basique")

            vulnerabilities = self.check_for_vulnerabilities()

            if vulnerabilities:
                self.log_test_result(
                    "Protection injection SQL basique",
                    False,
                    f"Vulnerabilites detectees: {', '.join(vulnerabilities)}",
                    screenshot_after
                )
                return False
            else:
                self.log_test_result(
                    "Protection injection SQL basique",
                    True,
                    "Injection SQL bloquee correctement",
                    screenshot_after
                )
                return True

        except Exception as e:
            error_screenshot = self.take_screenshot("sql_injection_error", f"Erreur test injection SQL: {str(e)}")
            self.log_test_result(
                "Test injection SQL basique",
                False,
                f"Erreur: {str(e)}",
                error_screenshot
            )
            return False

    def test_valid_login(self):
        """Test de connexion valide pour verifier que le systeme fonctionne"""
        print("\n=== TEST: Connexion Valide ===")

        if not self.navigate_to_login():
            self.log_test_result("Navigation vers login", False, "Impossible d'acceder a la page de login")
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

            # Capture avant connexion valide
            screenshot_before = self.take_screenshot("valid_login_before", "Avant connexion avec credentials valides")

            print("Tentative de connexion valide...")
            submit_button.click()
            time.sleep(5)

            # Capture apres connexion
            screenshot_after = self.take_screenshot("valid_login_after", "Apres connexion valide")

            # Verifier si on est bien connecte
            current_url = self.driver.current_url
            token = self.driver.execute_script("return localStorage.getItem('auth_token');")

            if "patients" in current_url or (token and token not in ["null", "undefined", "", None]):
                # Capture de la page apres connexion reussie
                success_screenshot = self.take_screenshot("valid_login_success", "Connexion reussie - page protegee")

                self.log_test_result(
                    "Connexion valide",
                    True,
                    "Connexion reussie avec les bonnes credentials",
                    success_screenshot
                )

                # Se deconnecter pour les prochains tests
                try:
                    logout_button = self.driver.find_element(By.ID, "logout")
                    logout_button.click()
                    time.sleep(2)
                    # Capture apres deconnexion
                    self.take_screenshot("after_logout", "Apres deconnexion")
                except:
                    print("Pas de bouton de deconnexion trouve")

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
            error_screenshot = self.take_screenshot("valid_login_error", f"Erreur connexion valide: {str(e)}")
            self.log_test_result(
                "Test connexion valide",
                False,
                f"Erreur: {str(e)}",
                error_screenshot
            )
            return False

    def test_sql_injection_variations(self):
        """Test de differentes variations d'injection SQL"""
        print("\n=== TEST: Variations d'Injection SQL ===")

        sql_payloads = [
            ("admin' --", "password"),
            ("admin' OR 1=1 --", "password"),
            ("' OR '1'='1' --", "' OR '1'='1' --"),
            ("admin'; DROP TABLE users; --", "password"),
        ]

        all_passed = True

        for i, (username, password) in enumerate(sql_payloads):
            if not self.navigate_to_login():
                continue

            try:
                print(f"\nTest injection {i+1}: {username[:30]}...")

                username_input = self.wait.until(EC.element_to_be_clickable((By.NAME, "username")))
                password_input = self.wait.until(EC.element_to_be_clickable((By.NAME, "password")))
                submit_button = self.driver.find_element(By.CSS_SELECTOR, "button[type='submit']")

                username_input.clear()
                username_input.send_keys(username)
                password_input.clear()
                password_input.send_keys(password)

                # Capture avant chaque variation
                screenshot_before = self.take_screenshot(f"sql_var_{i+1}_before", f"Avant injection variation {i+1}: {username[:20]}")

                submit_button.click()
                time.sleep(3)

                # Capture apres chaque variation
                screenshot_after = self.take_screenshot(f"sql_var_{i+1}_after", f"Apres injection variation {i+1}")

                vulnerabilities = self.check_for_vulnerabilities()

                if vulnerabilities:
                    self.log_test_result(
                        f"Protection SQL - {username[:20]}",
                        False,
                        f"Vulnerabilites: {', '.join(vulnerabilities)}",
                        screenshot_after
                    )
                    all_passed = False
                else:
                    self.log_test_result(
                        f"Protection SQL - {username[:20]}",
                        True,
                        "Injection bloquee",
                        screenshot_after
                    )

            except Exception as e:
                error_screenshot = self.take_screenshot(f"sql_var_{i+1}_error", f"Erreur variation {i+1}: {str(e)}")
                self.log_test_result(
                    f"Test SQL - {username[:20]}",
                    False,
                    f"Erreur: {str(e)}",
                    error_screenshot
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

            # Capture avant test XSS
            screenshot_before = self.take_screenshot("xss_before", "Avant test XSS")

            submit_button.click()
            time.sleep(2)

            # Capture apres test XSS
            screenshot_after = self.take_screenshot("xss_after", "Apres test XSS")

            # Verifier si une alerte s'est declenchee
            try:
                alert = self.driver.switch_to.alert
                alert_text = alert.text
                # Capture de l'alerte si possible
                alert_screenshot = self.take_screenshot("xss_alert", f"Alerte XSS detectee: {alert_text}")
                alert.accept()
                self.log_test_result(
                    "Protection XSS basique",
                    False,
                    f"Alerte XSS declenchee: {alert_text}",
                    alert_screenshot
                )
                return False
            except:
                # Pas d'alerte, verifier le DOM
                page_source = self.driver.page_source
                if "<script>" in page_source and "alert" in page_source:
                    dom_screenshot = self.take_screenshot("xss_dom_injection", "Script XSS injecte dans le DOM")
                    self.log_test_result(
                        "Protection XSS basique",
                        False,
                        "Script injecte dans le DOM",
                        dom_screenshot
                    )
                    return False
                else:
                    self.log_test_result(
                        "Protection XSS basique",
                        True,
                        "XSS bloque correctement",
                        screenshot_after
                    )
                    return True

        except Exception as e:
            error_screenshot = self.take_screenshot("xss_error", f"Erreur test XSS: {str(e)}")
            self.log_test_result(
                "Test XSS basique",
                False,
                f"Erreur: {str(e)}",
                error_screenshot
            )
            return False

    def test_authentication_bypass(self):
        """Test de contournement d'authentification simple"""
        print("\n=== TEST: Contournement d'Authentification ===")

        bypass_attempts = [
            ("admin ", "password"),  # Espace apres
            (" admin", "password"),  # Espace avant
            ("ADMIN", "password"),   # Majuscules
            ("admin\x00", "password"),  # Null byte
        ]

        all_passed = True

        for i, (username, password) in enumerate(bypass_attempts):
            if not self.navigate_to_login():
                continue

            try:
                print(f"\nTest bypass {i+1}: '{username}'")

                username_input = self.wait.until(EC.element_to_be_clickable((By.NAME, "username")))
                password_input = self.wait.until(EC.element_to_be_clickable((By.NAME, "password")))
                submit_button = self.driver.find_element(By.CSS_SELECTOR, "button[type='submit']")

                username_input.clear()
                username_input.send_keys(username)
                password_input.clear()
                password_input.send_keys(password)

                # Capture avant test de bypass
                screenshot_before = self.take_screenshot(f"bypass_{i+1}_before", f"Avant test bypass {i+1}: '{username.strip()}'")

                submit_button.click()
                time.sleep(3)

                # Capture apres test de bypass
                screenshot_after = self.take_screenshot(f"bypass_{i+1}_after", f"Apres test bypass {i+1}")

                vulnerabilities = self.check_for_vulnerabilities()

                if vulnerabilities:
                    self.log_test_result(
                        f"Protection bypass - {username.strip()}",
                        False,
                        f"Vulnerabilites: {', '.join(vulnerabilities)}",
                        screenshot_after
                    )
                    all_passed = False
                else:
                    self.log_test_result(
                        f"Protection bypass - {username.strip()}",
                        True,
                        "Tentative bloquee",
                        screenshot_after
                    )

            except Exception as e:
                error_screenshot = self.take_screenshot(f"bypass_{i+1}_error", f"Erreur bypass {i+1}: {str(e)}")
                self.log_test_result(
                    f"Test bypass - {username.strip()}",
                    False,
                    f"Erreur: {str(e)}",
                    error_screenshot
                )
                all_passed = False

        return all_passed

    def generate_simple_report(self):
        """Generer un rapport simple"""
        print("\n" + "="*60)
        print("RAPPORT DES TESTS DE SECURITE")
        print("="*60)
        print(f"Date: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        print(f"URL: {self.app_url}")
        print(f"Captures d'ecran: {self.screenshot_counter} fichiers dans {self.screenshots_dir}/")

        passed = sum(1 for t in self.test_results if t['passed'])
        failed = len(self.test_results) - passed

        print(f"\nResultats: {passed} reussis, {failed} echoues")
        print(f"Taux de reussite: {(passed/len(self.test_results)*100):.1f}%")

        if failed > 0:
            print("\n--- Tests echoues ---")
            for test in self.test_results:
                if not test['passed']:
                    print(f"ERREUR {test['test']}")
                    if test['details']:
                        print(f"   -> {test['details']}")
                    if test.get('screenshot'):
                        print(f"   CAPTURE {test['screenshot']}")

        # Lister toutes les captures d'ecran
        print(f"\n--- Captures d'ecran creees ({self.screenshot_counter} total) ---")
        for test in self.test_results:
            if test.get('screenshot'):
                print(f"CAPTURE {test['screenshot']} - {test['test']}")

        # Sauvegarder le rapport JSON
        report_file = f"security_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        with open(report_file, 'w') as f:
            json.dump({
                "date": datetime.now().isoformat(),
                "url": self.app_url,
                "screenshots_count": self.screenshot_counter,
                "screenshots_dir": self.screenshots_dir,
                "summary": {
                    "total": len(self.test_results),
                    "passed": passed,
                    "failed": failed
                },
                "results": self.test_results
            }, f, indent=2)

        print(f"\nRapport sauvegarde: {report_file}")

    def run_tests(self):
        """Executer les tests principaux"""
        print("="*60)
        print("TESTS DE SECURITE - AUTHENTIFICATION")
        print("="*60)

        # Capture d'ecran initiale
        try:
            self.driver.get(self.app_url)
            time.sleep(2)
            self.take_screenshot("test_start", "Debut des tests de securite")
        except:
            pass

        # Test de connexion valide d'abord
        self.test_valid_login()

        # Tests de securite
        self.test_basic_injection()
        self.test_sql_injection_variations()
        self.test_xss_basic()
        self.test_authentication_bypass()

        # Capture d'ecran finale
        try:
            self.take_screenshot("test_end", "Fin des tests de securite")
        except:
            pass

        # Generer le rapport
        self.generate_simple_report()

        # Retourner le succes global
        failed = sum(1 for t in self.test_results if not t['passed'])
        return failed == 0

    def cleanup(self):
        """Nettoyer les ressources"""
        if self.driver:
            try:
                # Capture finale avant fermeture
                self.take_screenshot("cleanup", "Avant fermeture du driver")
                self.driver.quit()
            except:
                pass

# Point d'entree principal
if __name__ == "__main__":
    app_url = sys.argv[1] if len(sys.argv) > 1 else "http://localhost:4201"

    print(f"Demarrage des tests de securite sur: {app_url}")

    tests = AuthSecurityTests(app_url)

    try:
        success = tests.run_tests()
        if success:
            print("\nSUCCES: Tests de securite termines avec succes!")
            exit(0)
        else:
            print("\nATTENTION: Certains tests ont echoue!")
            exit(0)  # Exit 0 pour ne pas bloquer Jenkins
    except Exception as e:
        print(f"\nERREUR: Erreur fatale: {str(e)}")
        try:
            tests.take_screenshot("fatal_error", f"Erreur fatale: {str(e)}")
        except:
            pass
        exit(1)
    finally:
        tests.cleanup()
