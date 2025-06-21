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

            # Capture de la page initiale
            self.take_screenshot("01_page_initiale")

            current_url = self.driver.current_url
            print(f"URL actuelle: {current_url}")

            if "login" not in current_url:
                login_url = f"{self.app_url}/login"
                print(f"Redirection manuelle vers: {login_url}")
                self.driver.get(login_url)
                time.sleep(3)

            try:
                self.wait.until(EC.presence_of_element_located((By.NAME, "username")))
                self.take_screenshot("02_page_login")
                print("✅ Page de login chargée avec succès")
                return True
            except TimeoutException:
                print("❌ Impossible de trouver les champs de login")
                self.take_screenshot("03_erreur_login")
                return False

        except Exception as e:
            print(f"❌ Erreur lors de la navigation: {str(e)}")
            self.take_screenshot("04_erreur_navigation")
            return False

    def log_test_result(self, test_name, passed, details="", screenshot=None):
        """Enregistrer le résultat d'un test avec capture"""
        result = {
            "test": test_name,
            "passed": passed,
            "details": details,
            "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            "screenshot": screenshot
        }
        self.test_results.append(result)

        status = "✅ PASSÉ" if passed else "❌ ÉCHOUÉ"
        print(f"{status} - {test_name}")
        if details:
            print(f"   Détails: {details}")

    def test_valid_login(self):
        """Test de connexion valide"""
        print("\\n=== TEST: Connexion Valide ===")

        if not self.navigate_to_login():
            return False

        try:
            username_input = self.wait.until(EC.element_to_be_clickable((By.NAME, "username")))
            password_input = self.wait.until(EC.element_to_be_clickable((By.NAME, "password")))
            submit_button = self.driver.find_element(By.CSS_SELECTOR, "button[type='submit']")

            username_input.clear()
            username_input.send_keys("admin")
            password_input.clear()
            password_input.send_keys("password123")

            self.take_screenshot("05_avant_connexion_valide")

            submit_button.click()
            time.sleep(5)

            current_url = self.driver.current_url
            token = self.driver.execute_script("return localStorage.getItem('auth_token');")

            if "patients" in current_url or (token and token not in ["null", "undefined", "", None]):
                screenshot = self.take_screenshot("06_connexion_reussie")
                self.log_test_result(
                    "Connexion valide",
                    True,
                    "Connexion réussie avec les bonnes credentials",
                    screenshot
                )

                try:
                    logout_button = self.driver.find_element(By.ID, "logout")
                    logout_button.click()
                    time.sleep(2)
                except:
                    pass

                return True
            else:
                screenshot = self.take_screenshot("07_echec_connexion")
                self.log_test_result(
                    "Connexion valide",
                    False,
                    "Impossible de se connecter",
                    screenshot
                )
                return False

        except Exception as e:
            screenshot = self.take_screenshot("08_erreur_test_connexion")
            self.log_test_result(
                "Test connexion valide",
                False,
                f"Erreur: {str(e)}",
                screenshot
            )
            return False

    def test_sql_injection(self):
        """Test d'injection SQL"""
        print("\\n=== TEST: Injection SQL ===")

        if not self.navigate_to_login():
            return False

        try:
            username_input = self.wait.until(EC.element_to_be_clickable((By.NAME, "username")))
            password_input = self.wait.until(EC.element_to_be_clickable((By.NAME, "password")))
            submit_button = self.driver.find_element(By.CSS_SELECTOR, "button[type='submit']")

            # Injection SQL
            username_input.clear()
            username_input.send_keys("admin' OR '1'='1")
            password_input.clear()
            password_input.send_keys("password")

            self.take_screenshot("09_tentative_injection_sql")

            submit_button.click()
            time.sleep(3)

            current_url = self.driver.current_url
            token = self.driver.execute_script("return localStorage.getItem('auth_token');")

            if "patients" in current_url or (token and token not in ["null", "undefined", "", None]):
                screenshot = self.take_screenshot("10_injection_sql_reussie")
                self.log_test_result(
                    "Protection injection SQL",
                    False,
                    "VULNÉRABILITÉ CRITIQUE: Injection SQL réussie!",
                    screenshot
                )
                return False
            else:
                screenshot = self.take_screenshot("11_injection_sql_bloquee")
                self.log_test_result(
                    "Protection injection SQL",
                    True,
                    "Injection SQL bloquée correctement",
                    screenshot
                )
                return True

        except Exception as e:
            screenshot = self.take_screenshot("12_erreur_test_sql")
            self.log_test_result(
                "Test injection SQL",
                False,
                f"Erreur: {str(e)}",
                screenshot
            )
            return False

    def generate_html_report(self):
        """Générer un rapport HTML avec les captures"""
        print("\\n📊 Génération du rapport HTML...")

        passed = sum(1 for t in self.test_results if t['passed'])
        failed = len(self.test_results) - passed

        html = f"""<!DOCTYPE html>
<html>
<head>
    <title>Rapport de Sécurité - {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}</title>
    <style>
        body {{ font-family: Arial, sans-serif; margin: 20px; background: #f5f5f5; }}
        .container {{ max-width: 1200px; margin: 0 auto; background: white; padding: 30px; border-radius: 10px; box-shadow: 0 0 20px rgba(0,0,0,0.1); }}
        h1 {{ color: #333; text-align: center; }}
        .summary {{ display: flex; justify-content: space-around; margin: 30px 0; }}
        .stat {{ text-align: center; padding: 20px; border-radius: 8px; }}
        .stat.success {{ background: #d4edda; color: #155724; }}
        .stat.danger {{ background: #f8d7da; color: #721c24; }}
        .stat.info {{ background: #d1ecf1; color: #0c5460; }}
        .test {{ margin: 20px 0; padding: 20px; border: 1px solid #ddd; border-radius: 8px; }}
        .test.passed {{ border-left: 5px solid #28a745; }}
        .test.failed {{ border-left: 5px solid #dc3545; background: #fff5f5; }}
        .test h3 {{ margin: 0 0 10px 0; }}
        .screenshot {{ margin: 20px 0; text-align: center; }}
        .screenshot img {{ max-width: 100%; border: 1px solid #ddd; border-radius: 8px; cursor: pointer; }}
        .modal {{ display: none; position: fixed; z-index: 1000; left: 0; top: 0; width: 100%; height: 100%; background: rgba(0,0,0,0.9); }}
        .modal-content {{ margin: 2% auto; display: block; max-width: 90%; max-height: 90%; }}
        .close {{ position: absolute; top: 15px; right: 35px; color: #f1f1f1; font-size: 40px; font-weight: bold; cursor: pointer; }}
    </style>
</head>
<body>
    <div class="container">
        <h1>📋 Rapport de Tests de Sécurité - Authentification</h1>
        <p style="text-align: center; color: #666;">URL testée: {self.app_url}</p>

        <div class="summary">
            <div class="stat info">
                <h2>{len(self.test_results)}</h2>
                <p>Tests exécutés</p>
            </div>
            <div class="stat success">
                <h2>{passed}</h2>
                <p>Tests réussis</p>
            </div>
            <div class="stat danger">
                <h2>{failed}</h2>
                <p>Tests échoués</p>
            </div>
        </div>

        <h2>📊 Détails des Tests</h2>
"""

        for i, test in enumerate(self.test_results):
            status = "passed" if test['passed'] else "failed"
            icon = "✅" if test['passed'] else "❌"

            html += f"""
        <div class="test {status}">
            <h3>{icon} {test['test']}</h3>
            <p><strong>Statut:</strong> {'Réussi' if test['passed'] else 'Échoué'}</p>
            <p><strong>Détails:</strong> {test.get('details', 'N/A')}</p>
            <p><strong>Timestamp:</strong> {test['timestamp']}</p>
"""

            if test.get('screenshot'):
                html += f"""
            <div class="screenshot">
                <img src="{test['screenshot']}" alt="Capture du test" onclick="openModal('modal{i}')">
            </div>

            <div id="modal{i}" class="modal" onclick="closeModal('modal{i}')">
                <span class="close">&times;</span>
                <img class="modal-content" src="{test['screenshot']}">
            </div>
"""

            html += "</div>"

        html += """
        <h2>🔒 Recommandations de Sécurité</h2>
        <ul>
            <li>Implémenter des requêtes préparées pour éviter les injections SQL</li>
            <li>Normaliser les entrées (trim, lowercase) avant validation</li>
            <li>Ajouter un système de rate limiting</li>
            <li>Implémenter un CAPTCHA après plusieurs échecs</li>
            <li>Ajouter des logs de sécurité pour toutes les tentatives de connexion</li>
        </ul>
    </div>

    <script>
        function openModal(id) {
            document.getElementById(id).style.display = "block";
        }

        function closeModal(id) {
            document.getElementById(id).style.display = "none";
        }
    </script>
</body>
</html>
"""

        # Sauvegarder le rapport HTML
        report_file = "security_report.html"
        with open(report_file, 'w', encoding='utf-8') as f:
            f.write(html)

        print(f"✅ Rapport HTML sauvegardé: {report_file}")

        # Sauvegarder aussi un JSON
        json_file = f"security_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        with open(json_file, 'w') as f:
            json.dump({
                "date": datetime.now().isoformat(),
                "url": self.app_url,
                "summary": {
                    "total": len(self.test_results),
                    "passed": passed,
                    "failed": failed
                },
                "results": self.test_results,
                "screenshots": self.screenshots
            }, f, indent=2)

    def run_tests(self):
        """Exécuter les tests principaux"""
        print("="*60)
        print("TESTS DE SÉCURITÉ AVEC CAPTURES D'ÉCRAN")
        print("="*60)

        self.test_valid_login()
        self.test_sql_injection()

        self.generate_html_report()

        # Lister toutes les captures créées
        print("\\n📸 Captures d'écran créées:")
        for screenshot in self.screenshots:
            print(f"  - {screenshot}")

    def cleanup(self):
        if self.driver:
            self.driver.quit()

# Point d'entrée principal
if __name__ == "__main__":
    app_url = sys.argv[1] if len(sys.argv) > 1 else "http://localhost:4201"

    tests = AuthSecurityTests(app_url)

    try:
        tests.run_tests()
        print("\\n✅ Tests terminés!")
        exit(0)
    except Exception as e:
        print(f"\\n❌ Erreur: {str(e)}")
        exit(1)
    finally:
        tests.cleanup()
EOF

          # Exécuter le test
          python3 tests/security_test_with_screenshots.py "$APP_URL"

          # Lister les captures créées
          echo "=== Captures d'écran créées ==="
          ls -la test-screenshots/ || echo "Pas de captures trouvées"

          # Compter les captures
          if [ -d test-screenshots ]; then
            echo "Nombre de captures: $(ls -1 test-screenshots/*.png 2>/dev/null | wc -l)"
          fi
        '''
      }
    }

    stage('Generate Screenshot Gallery') {
      steps {
        sh '''
          # Créer une galerie HTML pour visualiser toutes les captures
          cat > screenshot_gallery.html << 'EOF'
<!DOCTYPE html>
<html>
<head>
    <title>Galerie des Captures - Tests de Sécurité</title>
    <style>
        body { font-family: Arial, sans-serif; margin: 20px; background: #f0f0f0; }
        h1 { text-align: center; color: #333; }
        .gallery { display: grid; grid-template-columns: repeat(auto-fill, minmax(300px, 1fr)); gap: 20px; padding: 20px; }
        .screenshot { background: white; padding: 10px; border-radius: 8px; box-shadow: 0 2px 10px rgba(0,0,0,0.1); }
        .screenshot img { width: 100%; height: auto; border-radius: 4px; cursor: pointer; }
        .screenshot h3 { margin: 10px 0 5px 0; font-size: 14px; color: #555; }
    </style>
</head>
<body>
    <h1>📸 Galerie des Captures d'Écran</h1>
    <div class="gallery">
EOF

          # Ajouter chaque capture à la galerie
          if [ -d test-screenshots ]; then
            for img in test-screenshots/*.png; do
              if [ -f "$img" ]; then
                filename=$(basename "$img")
                echo "<div class='screenshot'><h3>$filename</h3><img src='$img' alt='$filename' onclick='window.open(this.src)'></div>" >> screenshot_gallery.html
              fi
            done
          fi

          echo "</div></body></html>" >> screenshot_gallery.html

          echo "✅ Galerie HTML créée"
        '''
      }
    }
  }

  post {
    always {
      // Archiver TOUS les artefacts importants
      archiveArtifacts artifacts: '''
        test-screenshots/**/*.png,
        security_report*.json,
        security_report.html,
        screenshot_gallery.html,
        *.log
      ''', allowEmptyArchive: true

      // Publier le rapport HTML
      publishHTML([
        allowMissing: false,
        alwaysLinkToLastBuild: true,
        keepAll: true,
        reportDir: '.',
        reportFiles: 'security_report.html',
        reportName: 'Security Test Report',
        reportTitles: 'Security Test Report'
      ])

      // Publier la galerie de captures
      publishHTML([
        allowMissing: false,
        alwaysLinkToLastBuild: true,
        keepAll: true,
        reportDir: '.',
        reportFiles: 'screenshot_gallery.html',
        reportName: 'Screenshots Gallery',
        reportTitles: 'Test Screenshots'
      ])

      sh '''
        echo "=== Résumé des artefacts ==="
        echo "📸 Captures d'écran:"
        find . -name "*.png" -type f | head -20

        echo -e "\\n📄 Rapports:"
        ls -la *.html *.json 2>/dev/null || echo "Aucun rapport trouvé"
      '''
    }
    success {
      echo 'Build réussi avec captures!'
    }
    failure {
      echo 'Build échoué!'
    }
  }
}
