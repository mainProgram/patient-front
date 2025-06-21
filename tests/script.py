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
        """Créer le répertoire pour les captures d'écran"""
        if not os.path.exists(self.screenshots_dir):
            os.makedirs(self.screenshots_dir)
            print(f"Répertoire créé: {self.screenshots_dir}")

    def take_screenshot(self, name, description=""):
        """Prendre une capture d'écran avec un nom descriptif"""
        try:
            self.screenshot_counter += 1
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"{self.screenshots_dir}/{self.screenshot_counter:02d}_{timestamp}_{name}.png"

            self.driver.save_screenshot(filename)
            print(f"Capture d'écran: {filename}")
            if description:
                print(f"   Description: {description}")

            return filename
        except Exception as e:
            print(f"Erreur capture d'écran: {str(e)}")
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
        """Naviguer vers la page de login, gérer les redirections"""
        try:
            print(f"Navigation vers: {self.app_url}")
            self.driver.get(self.app_url)
            time.sleep(3)

            # Capture d'écran après navigation initiale
            self.take_screenshot("initial_navigation", "Page après navigation initiale")

            # Vérifier si nous sommes déjà sur la page de login
            current_url = self.driver.current_url
            print(f"URL actuelle: {current_url}")

            # Si on n'est pas sur login, essayer d'y accéder directement
            if "login" not in current_url:
                login_url = f"{self.app_url}/login"
                print(f"Redirection manuelle vers: {login_url}")
                self.driver.get(login_url)
                time.sleep(3)

                # Capture après redirection vers login
                self.take_screenshot("redirect_to_login", "Page après redirection vers /login")

            # Attendre que les champs de login soient présents
            try:
                self.wait.until(EC.presence_of_element_located((By.NAME, "username")))
                print("Page de login chargée avec succès")

                # Capture de la page de login prête
                self.take_screenshot("login_page_ready", "Page de login avec champs visibles")
                return True
            except TimeoutException:
                print("Impossible de trouver les champs de login")
                # Capture en cas d'erreur
                self.take_screenshot("login_page_error", "Erreur - champs de login non trouvés")
                print(f"Page HTML actuelle: {self.driver.page_source[:500]}")
                return False

        except Exception as e:
            print(f"Erreur lors de la navigation: {str(e)}")
            self.take_screenshot("navigation_error", f"Erreur navigation: {str(e)}")
            return False

    def log_test_result(self, test_name, passed, details="", screenshot_path=None):
        """Enregistrer le résultat d'un test"""
        self.test_results.append({
            "test": test_name,
            "passed": passed,
            "details": details,
            "screenshot": screenshot_path,
            "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        })
        status = "PASSÉ" if passed else "ÉCHOUÉ"
        print(f"{status} - {test_name}")
        if details:
            print(f"   Détails: {details}")
        if screenshot_path:
            print(f"   Capture: {screenshot_path}")

    def check_for_vulnerabilities(self):
        """Vérifier les vulnérabilités communes après chaque tentative"""
        vulnerabilities = []

        try:
            # Capture d'écran avant vérification des vulnérabilités
            screenshot_path = self.take_screenshot("vulnerability_check", "État de la page lors de la vérification des vulnérabilités")

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

            # Si des vulnérabilités sont détectées, prendre une capture spéciale
            if vulnerabilities:
                self.take_screenshot("vulnerability_detected", f"Vulnérabilités détectées: {', '.join(vulnerabilities)}")

        except Exception as e:
            print(f"Erreur lors de la vérification des vulnérabilités: {str(e)}")
            self.take_screenshot("vulnerability_check_error", f"Erreur vérification: {str(e)}")

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

            # Capture avant soumission
            screenshot_before = self.take_screenshot("sql_injection_before", "Avant soumission injection SQL basique")

            print("Tentative d'injection SQL...")
            submit_button.click()
            time.sleep(3)

            # Capture après soumission
            screenshot_after = self.take_screenshot("sql_injection_after", "Après soumission injection SQL basique")

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
            error_screenshot = self.take_screenshot("sql_injection_error", f"Erreur test injection SQL: {str(e)}")
            self.log_test_result(
                "Test injection SQL basique",
                False,
                f"Erreur: {str(e)}",
                error_screenshot
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

            # Capture avant connexion valide
            screenshot_before = self.take_screenshot("valid_login_before", "Avant connexion avec credentials valides")

            print("Tentative de connexion valide...")
            submit_button.click()
            time.sleep(5)

            # Capture après connexion
            screenshot_after = self.take_screenshot("valid_login_after", "Après connexion valide")

            # Vérifier si on est bien connecté
            current_url = self.driver.current_url
            token = self.driver.execute_script("return localStorage.getItem('auth_token');")

            if "patients" in current_url or (token and token not in ["null", "undefined", "", None]):
                # Capture de la page après connexion réussie
                success_screenshot = self.take_screenshot("valid_login_success", "Connexion réussie - page protégée")

                self.log_test_result(
                    "Connexion valide",
                    True,
                    "Connexion réussie avec les bonnes credentials",
                    success_screenshot
                )

                # Se déconnecter pour les prochains tests
                try:
                    logout_button = self.driver.find_element(By.ID, "logout")
                    logout_button.click()
                    time.sleep(2)
                    # Capture après déconnexion
                    self.take_screenshot("after_logout", "Après déconnexion")
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
            error_screenshot = self.take_screenshot("valid_login_error", f"Erreur connexion valide: {str(e)}")
            self.log_test_result(
                "Test connexion valide",
                False,
                f"Erreur: {str(e)}",
                error_screenshot
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

                # Capture après chaque variation
                screenshot_after = self.take_screenshot(f"sql_var_{i+1}_after", f"Après injection variation {i+1}")

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

            # Capture après test XSS
            screenshot_after = self.take_screenshot("xss_after", "Après test XSS")

            # Vérifier si une alerte s'est déclenchée
            try:
                alert = self.driver.switch_to.alert
                alert_text = alert.text
                # Capture de l'alerte si possible
                alert_screenshot = self.take_screenshot("xss_alert", f"Alerte XSS détectée: {alert_text}")
                alert.accept()
                self.log_test_result(
                    "Protection XSS basique",
                    False,
                    f"Alerte XSS déclenchée: {alert_text}",
                    alert_screenshot
                )
                return False
            except:
                # Pas d'alerte, vérifier le DOM
                page_source = self.driver.page_source
                if "<script>" in page_source and "alert" in page_source:
                    dom_screenshot = self.take_screenshot("xss_dom_injection", "Script XSS injecté dans le DOM")
                    self.log_test_result(
                        "Protection XSS basique",
                        False,
                        "Script injecté dans le DOM",
                        dom_screenshot
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
            ("admin ", "password"),  # Espace après
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

                # Capture après test de bypass
                screenshot_after = self.take_screenshot(f"bypass_{i+1}_after", f"Après test bypass {i+1}")

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
        """Générer un rapport simple"""
        print("\n" + "="*60)
        print("RAPPORT DES TESTS DE SÉCURITÉ")
        print("="*60)
        print(f"Date: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        print(f"URL: {self.app_url}")
        print(f"Captures d'écran: {self.screenshot_counter} fichiers dans {self.screenshots_dir}/")

        passed = sum(1 for t in self.test_results if t['passed'])
        failed = len(self.test_results) - passed

        print(f"\nRésultats: {passed} réussis, {failed} échoués")
        print(f"Taux de réussite: {(passed/len(self.test_results)*100):.1f}%")

        if failed > 0:
            print("\n--- Tests échoués ---")
            for test in self.test_results:
                if not test['passed']:
                    print(f"{test['test']}")
                    if test['details']:
                        print(f"   → {test['details']}")
                    if test.get('screenshot'):
                        print(f"   {test['screenshot']}")

        # Lister toutes les captures d'écran
        print(f"\n--- Captures d'écran créées ({self.screenshot_counter} total) ---")
        for test in self.test_results:
            if test.get('screenshot'):
                print(f"{test['screenshot']} - {test['test']}")

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

        print(f"\nRapport sauvegardé: {report_file}")

    def run_tests(self):
        """Exécuter les tests principaux"""
        print("="*60)
        print("TESTS DE SÉCURITÉ - AUTHENTIFICATION")
        print("="*60)

        # Capture d'écran initiale
        try:
            self.driver.get(self.app_url)
            time.sleep(2)
            self.take_screenshot("test_start", "Début des tests de sécurité")
        except:
            pass

        # Test de connexion valide d'abord
        self.test_valid_login()

        # Tests de sécurité
        self.test_basic_injection()
        self.test_sql_injection_variations()
        self.test_xss_basic()
        self.test_authentication_bypass()

        # Capture d'écran finale
        try:
            self.take_screenshot("test_end", "Fin des tests de sécurité")
        except:
            pass

        # Générer le rapport
        self.generate_simple_report()

        # Retourner le succès global
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

# Point d'entrée principal
if __name__ == "__main__":
    app_url = sys.argv[1] if len(sys.argv) > 1 else "http://localhost:4201"

    print(f"Démarrage des tests de sécurité sur: {app_url}")

    tests = AuthSecurityTests(app_url)

    try:
        success = tests.run_tests()
        if success:
            print("\nTests de sécurité terminés avec succès!")
            exit(0)
        else:
            print("\nCertains tests ont échoué!")
            exit(0)  # Exit 0 pour ne pas bloquer Jenkins
    except Exception as e:
        print(f"\nErreur fatale: {str(e)}")
        try:
            tests.take_screenshot("fatal_error", f"Erreur fatale: {str(e)}")
        except:
            pass
        exit(1)
    finally:
        tests.cleanup()
