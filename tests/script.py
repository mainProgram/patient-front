import sys
import time
import json
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
    self.setup_driver()

  def setup_driver(self):
    options = Options()
    options.add_argument("--no-sandbox")
    options.add_argument("--disable-dev-shm-usage")
    options.add_argument("--window-size=1920,1080")

    self.driver = webdriver.Remote(
      command_executor='http://selenium:4444/wd/hub',
      options=options
    )
    self.wait = WebDriverWait(self.driver, 30)

  def log_test_result(self, test_name, passed, details=""):
    """Enregistrer le résultat d'un test"""
    self.test_results.append({
      "test": test_name,
      "passed": passed,
      "details": details,
      "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    })
    status = "✅ PASSÉ" if passed else "❌ ÉCHOUÉ"
    print(f"{status} - {test_name}")
    if details:
      print(f"   Détails: {details}")

  def check_for_vulnerabilities(self):
    """Vérifier les vulnérabilités communes après chaque tentative"""
    vulnerabilities = []

    # Vérifier si un token a été généré
    token = self.driver.execute_script("return localStorage.getItem('auth_token');")
    if token and token not in ["null", "undefined", ""]:
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

    return vulnerabilities

  def test_sql_injection_attacks(self):
    """Test de différentes attaques par injection SQL"""
    print("\n=== TEST: Injections SQL ===")

    sql_payloads = [
      # Injections classiques
      ("admin' OR '1'='1", "password"),
      ("admin' OR '1'='1' --", "password"),
      ("admin' OR '1'='1' /*", "password"),
      ("' OR 1=1 --", "' OR 1=1 --"),
      ("admin'; DROP TABLE users; --", "password"),
      ("admin' UNION SELECT NULL, NULL --", "password"),
      ("admin' AND 1=0 UNION SELECT 'admin', 'password' --", "password"),

      # Injections time-based
      ("admin' AND SLEEP(5) --", "password"),
      ("admin' AND 1=IF(2>1,SLEEP(5),0) --", "password"),

      # Injections avec encodage
      ("admin%27%20OR%20%271%27%3D%271", "password"),
      ("admin\' OR \'1\'=\'1", "password"),
    ]

    all_passed = True

    for username, password in sql_payloads:
      try:
        print(f"\nTest injection SQL: username='{username[:30]}...'")
        self.driver.get(self.app_url)
        time.sleep(2)

        username_input = self.wait.until(EC.element_to_be_clickable((By.NAME, "username")))
        password_input = self.wait.until(EC.element_to_be_clickable((By.NAME, "password")))
        submit_button = self.driver.find_element(By.CSS_SELECTOR, "button[type='submit']")

        username_input.clear()
        username_input.send_keys(username)
        password_input.clear()
        password_input.send_keys(password)

        # Mesurer le temps de réponse (pour détecter les time-based injections)
        start_time = time.time()
        submit_button.click()
        time.sleep(3)
        response_time = time.time() - start_time

        vulnerabilities = self.check_for_vulnerabilities()

        if vulnerabilities:
          self.log_test_result(
            f"Protection injection SQL - {username[:30]}",
            False,
            f"Vulnérabilités détectées: {', '.join(vulnerabilities)}"
          )
          all_passed = False
        else:
          # Vérifier aussi le temps de réponse
          if response_time > 4 and "SLEEP" in username:
            self.log_test_result(
              f"Protection injection SQL time-based - {username[:30]}",
              False,
              f"Possible vulnérabilité time-based (temps de réponse: {response_time:.2f}s)"
            )
            all_passed = False
          else:
            self.log_test_result(
              f"Protection injection SQL - {username[:30]}",
              True,
              "Attaque bloquée correctement"
            )

      except Exception as e:
        self.log_test_result(
          f"Protection injection SQL - {username[:30]}",
          False,
          f"Erreur durant le test: {str(e)}"
        )
        all_passed = False

    return all_passed

  def test_xss_attacks(self):
    """Test d'attaques XSS dans les champs de connexion"""
    print("\n=== TEST: Attaques XSS ===")

    xss_payloads = [
      # XSS basiques
      ("<script>alert('XSS')</script>", "password"),
      ("admin<script>alert(1)</script>", "password"),
      ("<img src=x onerror=alert('XSS')>", "password"),
      ("<svg onload=alert('XSS')>", "password"),
      ("javascript:alert('XSS')", "password"),

      # XSS encodés
      ("&lt;script&gt;alert('XSS')&lt;/script&gt;", "password"),
      ("&#60;script&#62;alert('XSS')&#60;/script&#62;", "password"),

      # XSS dans les événements
      ("admin' onmouseover='alert(1)", "password"),
      ("admin\" autofocus onfocus=alert(1)//", "password"),
    ]

    all_passed = True

    for username, password in xss_payloads:
      try:
        print(f"\nTest XSS: {username[:50]}...")
        self.driver.get(self.app_url)
        time.sleep(2)

        username_input = self.wait.until(EC.element_to_be_clickable((By.NAME, "username")))
        password_input = self.wait.until(EC.element_to_be_clickable((By.NAME, "password")))
        submit_button = self.driver.find_element(By.CSS_SELECTOR, "button[type='submit']")

        username_input.clear()
        username_input.send_keys(username)
        password_input.clear()
        password_input.send_keys(password)

        submit_button.click()
        time.sleep(2)

        # Vérifier si une alerte JavaScript s'est déclenchée
        try:
          alert = self.driver.switch_to.alert
          alert_text = alert.text
          alert.accept()
          self.log_test_result(
            f"Protection XSS - {username[:30]}",
            False,
            f"Alerte XSS déclenchée: {alert_text}"
          )
          all_passed = False
        except:
          # Pas d'alerte, c'est bien
          pass

        # Vérifier si le script a été injecté dans le DOM
        page_source = self.driver.page_source
        if "<script>" in page_source and username in page_source:
          self.log_test_result(
            f"Protection XSS - {username[:30]}",
            False,
            "Script injecté dans le DOM"
          )
          all_passed = False
        else:
          vulnerabilities = self.check_for_vulnerabilities()
          if not vulnerabilities:
            self.log_test_result(
              f"Protection XSS - {username[:30]}",
              True,
              "Attaque XSS bloquée correctement"
            )

      except Exception as e:
        self.log_test_result(
          f"Protection XSS - {username[:30]}",
          False,
          f"Erreur durant le test: {str(e)}"
        )
        all_passed = False

    return all_passed

  def test_authentication_bypass_attacks(self):
    """Test de contournement d'authentification"""
    print("\n=== TEST: Contournement d'authentification ===")

    bypass_attempts = [
      # Tentatives avec caractères spéciaux
      ("admin\x00", "password"),
      ("admin%00", "password"),
      ("admin\n", "password"),
      ("admin\r\n", "password"),

      # Tentatives avec espaces et caractères invisibles
      (" admin", "password"),
      ("admin ", "password"),
      (" admin ", "password"),
      ("ad min", "password"),

      # Tentatives de troncature
      ("admin" + "a" * 1000, "password"),
      ("admin", "password" + "a" * 1000),

      # Tentatives avec null bytes
      ("admin\0", "password\0"),

      # Tentatives de confusion de casse
      ("ADMIN", "password"),
      ("Admin", "password"),
      ("aDmIn", "password"),
    ]

    all_passed = True

    for username, password in bypass_attempts:
      try:
        print(f"\nTest bypass: username='{username[:30]}...'")
        self.driver.get(self.app_url)
        time.sleep(2)

        username_input = self.wait.until(EC.element_to_be_clickable((By.NAME, "username")))
        password_input = self.wait.until(EC.element_to_be_clickable((By.NAME, "password")))
        submit_button = self.driver.find_element(By.CSS_SELECTOR, "button[type='submit']")

        username_input.clear()
        username_input.send_keys(username)
        password_input.clear()
        password_input.send_keys(password)

        submit_button.click()
        time.sleep(3)

        vulnerabilities = self.check_for_vulnerabilities()

        if vulnerabilities:
          self.log_test_result(
            f"Protection bypass auth - {username[:30]}",
            False,
            f"Vulnérabilités détectées: {', '.join(vulnerabilities)}"
          )
          all_passed = False
        else:
          self.log_test_result(
            f"Protection bypass auth - {username[:30]}",
            True,
            "Tentative de bypass bloquée"
          )

      except Exception as e:
        self.log_test_result(
          f"Protection bypass auth - {username[:30]}",
          False,
          f"Erreur durant le test: {str(e)}"
        )
        all_passed = False

    return all_passed

  def test_session_security(self):
    """Test de la sécurité des sessions"""
    print("\n=== TEST: Sécurité des sessions ===")

    try:
      # D'abord se connecter avec des credentials valides
      self.driver.get(self.app_url)
      time.sleep(2)

      username_input = self.wait.until(EC.element_to_be_clickable((By.NAME, "username")))
      password_input = self.wait.until(EC.element_to_be_clickable((By.NAME, "password")))
      submit_button = self.driver.find_element(By.CSS_SELECTOR, "button[type='submit']")

      username_input.send_keys("admin")
      password_input.send_keys("password123")
      submit_button.click()
      time.sleep(3)

      # Récupérer le token et les cookies
      token = self.driver.execute_script("return localStorage.getItem('auth_token');")
      cookies = self.driver.get_cookies()

      # Test 1: Vérifier la présence et la sécurité du token
      if not token:
        self.log_test_result(
          "Présence du token d'authentification",
          False,
          "Aucun token trouvé après connexion"
        )
        return False

      # Test 2: Vérifier la complexité du token
      if len(token) < 20:
        self.log_test_result(
          "Complexité du token",
          False,
          f"Token trop court ({len(token)} caractères)"
        )
      else:
        self.log_test_result(
          "Complexité du token",
          True,
          f"Token de longueur appropriée ({len(token)} caractères)"
        )

      # Test 3: Vérifier les flags de sécurité des cookies
      session_cookie_found = False
      for cookie in cookies:
        if 'session' in cookie['name'].lower() or 'auth' in cookie['name'].lower():
          session_cookie_found = True
          if not cookie.get('httpOnly'):
            self.log_test_result(
              f"Cookie {cookie['name']} - Flag HttpOnly",
              False,
              "Cookie sans flag HttpOnly (vulnérable au XSS)"
            )
          else:
            self.log_test_result(
              f"Cookie {cookie['name']} - Flag HttpOnly",
              True,
              "Flag HttpOnly présent"
            )

          if not cookie.get('secure'):
            self.log_test_result(
              f"Cookie {cookie['name']} - Flag Secure",
              False,
              "Cookie sans flag Secure (vulnérable en HTTP)"
            )

      # Test 4: Tester la manipulation du token
      print("\nTest de manipulation du token...")

      # Modifier le token
      self.driver.execute_script("localStorage.setItem('auth_token', 'fake-token-12345');")

      # Essayer d'accéder à une page protégée
      self.driver.get(f"{self.app_url}/patients")
      time.sleep(3)

      # Vérifier si on est redirigé vers login
      current_url = self.driver.current_url
      if "login" in current_url:
        self.log_test_result(
          "Protection contre token invalide",
          True,
          "Redirection vers login avec token invalide"
        )
      else:
        self.log_test_result(
          "Protection contre token invalide",
          False,
          "Accès autorisé avec token invalide!"
        )

      # Test 5: Tester la suppression du token
      self.driver.execute_script("localStorage.removeItem('auth_token');")
      self.driver.get(f"{self.app_url}/patients")
      time.sleep(3)

      if "login" in self.driver.current_url:
        self.log_test_result(
          "Protection sans token",
          True,
          "Redirection vers login sans token"
        )
      else:
        self.log_test_result(
          "Protection sans token",
          False,
          "Accès autorisé sans token!"
        )

      return True

    except Exception as e:
      self.log_test_result(
        "Test de sécurité des sessions",
        False,
        f"Erreur: {str(e)}"
      )
      return False

  def test_brute_force_protection(self):
    """Test de protection contre le brute force"""
    print("\n=== TEST: Protection Brute Force ===")

    try:
      # Effectuer plusieurs tentatives de connexion échouées
      failed_attempts = 0
      max_attempts = 10

      for i in range(max_attempts):
        print(f"Tentative {i+1}/{max_attempts}")
        self.driver.get(self.app_url)
        time.sleep(1)

        username_input = self.wait.until(EC.element_to_be_clickable((By.NAME, "username")))
        password_input = self.wait.until(EC.element_to_be_clickable((By.NAME, "password")))
        submit_button = self.driver.find_element(By.CSS_SELECTOR, "button[type='submit']")

        username_input.clear()
        username_input.send_keys("admin")
        password_input.clear()
        password_input.send_keys(f"wrongpassword{i}")

        start_time = time.time()
        submit_button.click()
        response_time = time.time() - start_time
        time.sleep(2)

        # Vérifier si on détecte un ralentissement ou un blocage
        if i > 5:  # Après 5 tentatives
          if response_time > 3:  # Si le temps de réponse augmente
            self.log_test_result(
              "Détection de ralentissement après échecs multiples",
              True,
              f"Ralentissement détecté après {i+1} tentatives"
            )
            return True

          # Vérifier si un message d'erreur spécifique apparaît
          error_messages = self.driver.find_elements(By.CLASS_NAME, "error-message")
          for msg in error_messages:
            if "bloqu" in msg.text.lower() or "trop" in msg.text.lower():
              self.log_test_result(
                "Protection brute force",
                True,
                f"Blocage détecté après {i+1} tentatives"
              )
              return True

        failed_attempts += 1

      # Si on arrive ici, aucune protection n'a été détectée
      self.log_test_result(
        "Protection brute force",
        False,
        f"Aucune protection détectée après {max_attempts} tentatives"
      )
      return False

    except Exception as e:
      self.log_test_result(
        "Test protection brute force",
        False,
        f"Erreur: {str(e)}"
      )
      return False

  def test_ldap_injection_attacks(self):
    """Test d'injections LDAP"""
    print("\n=== TEST: Injections LDAP ===")

    ldap_payloads = [
      ("admin)(|(password=*))", "password"),
      ("*", "*"),
      ("admin)(&(password=*))", "password"),
      ("admin)(cn=*))", "password"),
      ("*)(uid=*))(|(uid=*", "password"),
    ]

    all_passed = True

    for username, password in ldap_payloads:
      try:
        print(f"\nTest injection LDAP: {username}")
        self.driver.get(self.app_url)
        time.sleep(2)

        username_input = self.wait.until(EC.element_to_be_clickable((By.NAME, "username")))
        password_input = self.wait.until(EC.element_to_be_clickable((By.NAME, "password")))
        submit_button = self.driver.find_element(By.CSS_SELECTOR, "button[type='submit']")

        username_input.clear()
        username_input.send_keys(username)
        password_input.clear()
        password_input.send_keys(password)

        submit_button.click()
        time.sleep(3)

        vulnerabilities = self.check_for_vulnerabilities()

        if vulnerabilities:
          self.log_test_result(
            f"Protection injection LDAP - {username}",
            False,
            f"Vulnérabilités: {', '.join(vulnerabilities)}"
          )
          all_passed = False
        else:
          self.log_test_result(
            f"Protection injection LDAP - {username}",
            True,
            "Injection LDAP bloquée"
          )

      except Exception as e:
        self.log_test_result(
          f"Protection injection LDAP - {username}",
          False,
          f"Erreur: {str(e)}"
        )
        all_passed = False

    return all_passed

  def generate_report(self):
    """Générer un rapport détaillé des tests"""
    print("\n" + "="*80)
    print("RAPPORT DÉTAILLÉ DES TESTS DE SÉCURITÉ")
    print("="*80)
    print(f"Date: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"URL testée: {self.app_url}")
    print(f"Nombre total de tests: {len(self.test_results)}")

    passed_tests = sum(1 for test in self.test_results if test['passed'])
    failed_tests = len(self.test_results) - passed_tests

    print(f"Tests réussis: {passed_tests}")
    print(f"Tests échoués: {failed_tests}")
    print(f"Taux de réussite: {(passed_tests/len(self.test_results)*100):.2f}%")

    print("\n--- DÉTAILS DES TESTS ---")

    # Grouper par catégorie
    categories = {
      "SQL Injection": [],
      "XSS": [],
      "Authentication Bypass": [],
      "Session Security": [],
      "Brute Force": [],
      "LDAP Injection": [],
      "Autres": []
    }

    for test in self.test_results:
      test_name = test['test']
      if "SQL" in test_name:
        categories["SQL Injection"].append(test)
      elif "XSS" in test_name:
        categories["XSS"].append(test)
      elif "bypass" in test_name.lower():
        categories["Authentication Bypass"].append(test)
      elif "session" in test_name.lower() or "token" in test_name.lower():
        categories["Session Security"].append(test)
      elif "brute" in test_name.lower():
        categories["Brute Force"].append(test)
      elif "LDAP" in test_name:
        categories["LDAP Injection"].append(test)
      else:
        categories["Autres"].append(test)

    for category, tests in categories.items():
      if tests:
        print(f"\n### {category} ###")
        for test in tests:
          status = "✅" if test['passed'] else "❌"
          print(f"{status} {test['test']}")
          if test['details']:
            print(f"   → {test['details']}")

    # Recommandations
    print("\n--- RECOMMANDATIONS DE SÉCURITÉ ---")

    recommendations = []

    # Analyser les échecs pour générer des recommandations
    for test in self.test_results:
      if not test['passed']:
        if "SQL" in test['test']:
          recommendations.append("• Implémenter des requêtes préparées (prepared statements)")
          recommendations.append("• Valider et échapper toutes les entrées utilisateur")
        elif "XSS" in test['test']:
          recommendations.append("• Encoder toutes les sorties HTML")
          recommendations.append("• Implémenter une Content Security Policy (CSP)")
        elif "session" in test['test'].lower():
          recommendations.append("• Ajouter les flags HttpOnly et Secure aux cookies")
          recommendations.append("• Implémenter une rotation des tokens de session")
        elif "brute" in test['test'].lower():
          recommendations.append("• Implémenter un système de rate limiting")
          recommendations.append("• Ajouter un CAPTCHA après plusieurs échecs")
          recommendations.append("• Implémenter un verrouillage temporaire des comptes")

    # Supprimer les doublons
    recommendations = list(set(recommendations))

    for rec in recommendations:
      print(rec)

    # Sauvegarder le rapport dans un fichier
    report_filename = f"security_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
    with open(report_filename, 'w', encoding='utf-8') as f:
      json.dump({
        "date": datetime.now().isoformat(),
        "url": self.app_url,
        "summary": {
          "total_tests": len(self.test_results),
          "passed": passed_tests,
          "failed": failed_tests,
          "success_rate": f"{(passed_tests/len(self.test_results)*100):.2f}%"
        },
        "test_results": self.test_results,
        "recommendations": recommendations
      }, f, indent=2, ensure_ascii=False)

    print(f"\nRapport sauvegardé dans: {report_filename}")

  def run_all_tests(self):
    """Exécuter tous les tests de sécurité"""
    print("="*80)
    print("DÉBUT DES TESTS DE SÉCURITÉ D'AUTHENTIFICATION")
    print("="*80)

    # Exécuter tous les tests
    self.test_sql_injection_attacks()
    self.test_xss_attacks()
    self.test_authentication_bypass_attacks()
    self.test_session_security()
    self.test_brute_force_protection()
    self.test_ldap_injection_attacks()

    # Générer le rapport
    self.generate_report()

    # Retourner le statut global
    failed_tests = sum(1 for test in self.test_results if not test['passed'])
    return failed_tests == 0

  def cleanup(self):
    """Nettoyer les ressources"""
    if self.driver:
      time.sleep(2)
      self.driver.quit()

# Point d'entrée principal
if __name__ == "__main__":
  app_url = sys.argv[1] if len(sys.argv) > 1 else "http://localhost:4201"

  security_tests = AuthSecurityTests(app_url)

  try:
    success = security_tests.run_all_tests()
    if success:
      print("\n✅ TOUS LES TESTS DE SÉCURITÉ SONT PASSÉS!")
      exit(0)
    else:
      print("\n❌ CERTAINS TESTS DE SÉCURITÉ ONT ÉCHOUÉ!")
      exit(1)
  except Exception as e:
    print(f"\n❌ Erreur fatale: {str(e)}")
    security_tests.driver.save_screenshot("fatal_error.png")
    exit(1)
  finally:
    security_tests.cleanup()
