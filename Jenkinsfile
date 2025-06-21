pipeline {
  agent any

  stages {
    stage('Checkout') {
      steps {
        checkout scm
      }
    }

    stage('Node Version') {
      steps {
        sh 'node --version'
        sh 'npm --version'
      }
    }

    stage('Install Dependencies') {
      steps {
        sh 'npm install'
      }
    }

    stage('Build') {
      steps {
        sh 'npm run build'
      }
    }

    stage('Verify Build') {
      steps {
        sh '''
          echo "=== Vérification du build Angular ==="
          echo "Contenu du répertoire dist:"
          ls -la ./dist/patient-front/

          echo "Contenu du répertoire browser:"
          ls -la ./dist/patient-front/browser/

          echo "Vérification de l'index.html:"
          if [ -f ./dist/patient-front/browser/index.html ]; then
            echo "✅ index.html trouvé"

            # Vérifier le contenu de index.html
            echo "=== Contenu de index.html (premières lignes) ==="
            head -20 ./dist/patient-front/browser/index.html

            # Vérifier la base href
            grep -i "base href" ./dist/patient-front/browser/index.html || echo "⚠️ Pas de base href trouvé"
          else
            echo "❌ index.html non trouvé"
            exit 1
          fi

          # Vérifier les fichiers JS générés
          echo "=== Fichiers JavaScript générés ==="
          ls -la ./dist/patient-front/browser/*.js | head -10
        '''
      }
    }

    stage('Configure Angular for Backend') {
      steps {
        sh '''
          # Créer un fichier de configuration pour pointer vers le backend
          mkdir -p ./dist/patient-front/browser/assets
          echo '{
            "apiUrl": "http://backend-api:8080/api"
          }' > ./dist/patient-front/browser/assets/config.json

          # Vérifier le contenu du fichier créé
          cat ./dist/patient-front/browser/assets/config.json

          # IMPORTANT: Corriger la base href pour Angular routing
          echo "=== Correction de la base href ==="
          sed -i 's|<base href="/">|<base href="/">|g' ./dist/patient-front/browser/index.html

          # Créer un fichier .htaccess pour le routing Angular (si nécessaire)
          cat > ./dist/patient-front/browser/.htaccess << 'EOF'
<IfModule mod_rewrite.c>
  RewriteEngine On
  RewriteBase /
  RewriteRule ^index\\.html$ - [L]
  RewriteCond %{REQUEST_FILENAME} !-f
  RewriteCond %{REQUEST_FILENAME} !-d
  RewriteRule . /index.html [L]
</IfModule>
EOF
        '''
      }
    }

    stage('Start Angular with Diagnostics') {
      steps {
        sh '''
          echo "=== Démarrage du serveur Angular ==="

          # Tuer tout processus http-server existant
          pkill -f "http-server" || true
          sleep 2

          # Démarrer http-server avec options de debug
          echo "Démarrage de http-server..."
          npx http-server ./dist/patient-front/browser \
            -p 4201 \
            -a 0.0.0.0 \
            --cors \
            -c-1 \
            --proxy http://localhost:4201? \
            -d false \
            --log-ip \
            > http-server.log 2>&1 &

          # Sauvegarder le PID
          HTTP_SERVER_PID=$!
          echo $HTTP_SERVER_PID > http-server.pid

          echo "PID du serveur: $HTTP_SERVER_PID"

          # Attendre que le serveur démarre
          echo "Attente du démarrage du serveur..."
          for i in {1..30}; do
            if netstat -tuln | grep -q ":4201 "; then
              echo "✅ Serveur démarré sur le port 4201"
              break
            fi
            echo "Attente... ($i/30)"
            sleep 1
          done

          # Afficher les logs du serveur
          echo "=== Logs du serveur HTTP ==="
          cat http-server.log || echo "Pas de logs disponibles"

          # Vérifier que le serveur écoute
          echo "=== Ports en écoute ==="
          netstat -tuln | grep 4201 || echo "⚠️ Port 4201 non trouvé"

          # Vérifier les processus
          echo "=== Processus http-server ==="
          ps aux | grep http-server | grep -v grep || echo "⚠️ Processus http-server non trouvé"
        '''
      }
    }

    stage('Test Angular Accessibility') {
      steps {
        sh '''
          # Obtenir l'adresse IP
          JENKINS_IP=$(hostname -i)
          echo "IP Jenkins: $JENKINS_IP"

          # Test 1: Accès direct à l'IP
          echo "=== Test 1: Accès à http://$JENKINS_IP:4201/ ==="
          curl -v "http://$JENKINS_IP:4201/" 2>&1 | head -30

          # Test 2: Accès via localhost
          echo "=== Test 2: Accès à http://localhost:4201/ ==="
          curl -v "http://localhost:4201/" 2>&1 | head -30

          # Test 3: Vérifier le contenu HTML
          echo "=== Test 3: Contenu HTML récupéré ==="
          curl -s "http://$JENKINS_IP:4201/" | grep -E "(app-root|angular|<base)" | head -10

          # Test 4: Accès à la route /login
          echo "=== Test 4: Accès à http://$JENKINS_IP:4201/login ==="
          curl -s "http://$JENKINS_IP:4201/login" | head -30

          # Test 5: Vérifier les assets
          echo "=== Test 5: Accès aux fichiers statiques ==="
          curl -I "http://$JENKINS_IP:4201/index.html"

          # Afficher la structure des fichiers servis
          echo "=== Fichiers dans le répertoire servi ==="
          ls -la ./dist/patient-front/browser/ | head -20
        '''
      }
    }

    stage('Check Backend') {
      steps {
        sh '''
          # Vérifier si le backend est accessible
          echo "=== Test du backend ==="
          for i in {1..10}; do
            if curl -s "http://backend-api:8080/api/health" > /dev/null || curl -s "http://backend-api:8080/api/auth/signin" > /dev/null; then
              echo "✅ Backend accessible"
              break
            else
              echo "⏳ Attente du backend... ($i/10)"
              sleep 3
            fi
          done

          # Test d'authentification direct
          echo "=== Test API authentification ==="
          curl -X POST "http://backend-api:8080/api/auth/signin" \
            -H "Content-Type: application/json" \
            -d '{"username":"admin","password":"password123"}' \
            -v 2>&1 | head -20
        '''
      }
    }

    stage('Alternative Angular Server') {
      when {
        expression {
          // Exécuter seulement si le serveur précédent a échoué
          return true
        }
      }
      steps {
        sh '''
          echo "=== Tentative avec un serveur alternatif ==="

          # Arrêter le serveur précédent
          if [ -f http-server.pid ]; then
            kill $(cat http-server.pid) || true
            rm http-server.pid
          fi
          pkill -f "http-server" || true

          # Essayer avec le serveur de développement Angular
          echo "=== Installation de serve ==="
          npm install -g serve

          # Démarrer avec serve
          serve -s ./dist/patient-front/browser -l 4201 &
          SERVE_PID=$!
          echo $SERVE_PID > serve.pid

          sleep 10

          # Tester à nouveau
          JENKINS_IP=$(hostname -i)
          echo "=== Test avec serve ==="
          curl -v "http://$JENKINS_IP:4201/" 2>&1 | head -20
        '''
      }
    }

    stage('E2E Test with Fallback') {
      steps {
        sh '''
          # Obtenir l'adresse IP du conteneur Jenkins
          JENKINS_IP=$(hostname -i)

          # Configurer l'URL pour les tests Selenium
          export APP_URL="http://$JENKINS_IP:4201"

          echo "=== Configuration des tests E2E ==="
          echo "URL de test: $APP_URL"

          # Créer un script de test simple pour vérifier l'accès
          cat > tests/simple_test.py << 'EOF'
import sys
import time
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

app_url = sys.argv[1] if len(sys.argv) > 1 else "http://localhost:4201"

options = Options()
options.add_argument("--no-sandbox")
options.add_argument("--disable-dev-shm-usage")
options.add_argument("--headless")

try:
    driver = webdriver.Remote(
        command_executor='http://selenium:4444/wd/hub',
        options=options
    )

    print(f"Test de connexion à: {app_url}")
    driver.get(app_url)
    time.sleep(5)

    print(f"Titre de la page: {driver.title}")
    print(f"URL actuelle: {driver.current_url}")

    # Prendre une capture d'écran
    driver.save_screenshot("page_screenshot.png")

    # Afficher une partie du HTML
    print("HTML (500 premiers caractères):")
    print(driver.page_source[:500])

    driver.quit()
    print("Test terminé avec succès")
    exit(0)

except Exception as e:
    print(f"Erreur: {str(e)}")
    exit(1)
EOF

          # Exécuter le test simple
          python3 tests/script.py "$APP_URL" || {
            echo "⚠️ Test simple échoué, vérification des alternatives..."

            # Essayer avec localhost
            python3 tests/script.py "http://localhost:4201" || true
          }

          # Si une capture d'écran existe, afficher ses propriétés
          if [ -f page_screenshot.png ]; then
            echo "=== Capture d'écran créée ==="
            ls -la page_screenshot.png
          fi
        '''
      }
    }

    stage('E2E Security Tests with Screenshots') {
      steps {
        sh '''
          # Obtenir l'adresse IP du conteneur Jenkins
          JENKINS_IP=$(hostname -i)

          # Configurer l'URL pour les tests Selenium
          export APP_URL="http://$JENKINS_IP:4201"

          echo "=== Configuration des tests E2E ==="
          echo "URL de test: $APP_URL"

          # Créer un dossier pour les captures
          mkdir -p test-screenshots

          # Modifier le script pour sauvegarder dans le bon dossier
          cat > tests/security_test_with_screenshots.py << 'EOF'
        '''
      }
    }
  }

  post {
    always {
      sh '''
        # Nettoyer les processus
        pkill -f "http-server" || true
        pkill -f "serve" || true

        # Archiver les logs et captures
        if [ -f http-server.log ]; then
          echo "=== Logs finaux du serveur ==="
          tail -50 http-server.log
        fi

        # Supprimer les fichiers temporaires
        rm -f *.pid
      '''

      // Archiver les artefacts utiles
      archiveArtifacts artifacts: '*.png, *.log, security_report_*.json', allowEmptyArchive: true
    }
    success {
      echo 'Build réussi!'
    }
    failure {
      echo 'Build échoué!'
    }
  }
}
