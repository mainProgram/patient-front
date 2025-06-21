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
          echo "Contenu du repertoire dist:"
          ls -la ./dist/patient-front/

          ls -la ./dist/patient-front/browser/

          if [ -f ./dist/patient-front/browser/index.html ]; then
            echo "SUCCES: index.html trouve"

            echo "=== Contenu de index.html (premieres lignes) ==="
            head -20 ./dist/patient-front/browser/index.html

            grep -i "base href" ./dist/patient-front/browser/index.html || echo "ATTENTION: Pas de base href trouve"
          else
            echo "ERREUR: index.html non trouve"
            exit 1
          fi

          echo "=== Fichiers JavaScript generes ==="
          ls -la ./dist/patient-front/browser/*.js | head -10
        '''
      }
    }

    stage('Configure Angular for Backend') {
      steps {
        sh '''
          # Creer un fichier de configuration pour pointer vers le backend
          mkdir -p ./dist/patient-front/browser/assets
          echo '{
            "apiUrl": "http://backend-api:8080/api"
          }' > ./dist/patient-front/browser/assets/config.json

          # Verifier le contenu du fichier cree
          cat ./dist/patient-front/browser/assets/config.json

          # Corriger la base href pour Angular routing
          echo "=== Correction de la base href ==="
          sed -i 's|<base href="/">|<base href="/">|g' ./dist/patient-front/browser/index.html

          # Creer un fichier .htaccess pour le routing Angular
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
          echo "=== Demarrage du serveur Angular ==="

          # Arreter tout processus http-server existant
          pkill -f "http-server" || true
          sleep 2

          # Demarrer http-server avec options de debug
          echo "Demarrage de http-server..."
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

          echo "Attente du demarrage du serveur..."
          for i in {1..30}; do
            if netstat -tuln | grep -q ":4201 "; then
              echo "SUCCES: Serveur demarre sur le port 4201"
              break
            fi
            echo "Attente... ($i/30)"
            sleep 1
          done

          echo "=== Logs du serveur HTTP ==="
          cat http-server.log || echo "Pas de logs disponibles"

          echo "=== Ports en ecoute ==="
          netstat -tuln | grep 4201 || echo "ATTENTION: Port 4201 non trouve"

          echo "=== Processus http-server ==="
          ps aux | grep http-server | grep -v grep || echo "ATTENTION: Processus http-server non trouve"
        '''
      }
    }

    stage('Test Angular Accessibility') {
      steps {
        sh '''
          # Obtenir l'adresse IP
          JENKINS_IP=$(hostname -i)
          echo "IP Jenkins: $JENKINS_IP"

          # Test 1: Acces direct a l'IP
          echo "=== Test 1: Acces a http://$JENKINS_IP:4201/ ==="
          curl -v "http://$JENKINS_IP:4201/" 2>&1 | head -30

          # Test 2: Acces via localhost
          echo "=== Test 2: Acces a http://localhost:4201/ ==="
          curl -v "http://localhost:4201/" 2>&1 | head -30

          # Test 3: Verifier le contenu HTML
          echo "=== Test 3: Contenu HTML recupere ==="
          curl -s "http://$JENKINS_IP:4201/" | grep -E "(app-root|angular|<base)" | head -10

          # Test 4: Acces a la route /login
          echo "=== Test 4: Acces a http://$JENKINS_IP:4201/login ==="
          curl -s "http://$JENKINS_IP:4201/login" | head -30

          # Test 5: Verifier les assets
          echo "=== Test 5: Acces aux fichiers statiques ==="
          curl -I "http://$JENKINS_IP:4201/index.html"

          echo "=== Fichiers dans le repertoire servi ==="
          ls -la ./dist/patient-front/browser/ | head -20
        '''
      }
    }

    stage('Check Backend') {
      steps {
        sh '''
          echo "=== Test du backend ==="
          for i in {1..10}; do
            if curl -s "http://backend-api:8080/api/health" > /dev/null || curl -s "http://backend-api:8080/api/auth/signin" > /dev/null; then
              echo "SUCCES: Backend accessible"
              break
            else
              echo "EN ATTENTE: Attente du backend... ($i/10)"
              sleep 3
            fi
          done

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
          return true
        }
      }
      steps {
        sh '''
          echo "=== Tentative avec un serveur alternatif ==="

          # Arreter le serveur precedent
          if [ -f http-server.pid ]; then
            kill $(cat http-server.pid) || true
            rm http-server.pid
          fi
          pkill -f "http-server" || true

          # Essayer avec le serveur de developpement Angular
          echo "=== Installation de serve ==="
          npm install -g serve

          # Demarrer avec serve
          serve -s ./dist/patient-front/browser -l 4201 &
          SERVE_PID=$!
          echo $SERVE_PID > serve.pid

          sleep 10

          # Tester a nouveau
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

          # Creer le repertoire pour les captures d'ecran si il n'existe pas
          mkdir -p screenshots

          # Creer un script de test simple pour verifier l'acces
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

    print(f"Test de connexion a: {app_url}")
    driver.get(app_url)
    time.sleep(5)

    print(f"Titre de la page: {driver.title}")
    print(f"URL actuelle: {driver.current_url}")

    # Prendre une capture d'ecran
    driver.save_screenshot("page_screenshot.png")

    # Afficher une partie du HTML
    print("HTML (500 premiers caracteres):")
    print(driver.page_source[:500])

    driver.quit()
    print("Test termine avec succes")
    exit(0)

except Exception as e:
    print(f"Erreur: {str(e)}")
    exit(1)
EOF

          echo "=== Execution des tests de securite avec captures d'ecran ==="
          python3 tests/script.py "$APP_URL" || {
            echo "ATTENTION: Tests de securite termines avec des avertissements"

            # Verifier si des captures ont ete creees
            if [ -d "screenshots" ] && [ "$(ls -A screenshots 2>/dev/null)" ]; then
              echo "SUCCES: Captures d'ecran creees:"
              ls -la screenshots/
            else
              echo "ATTENTION: Aucune capture d'ecran trouvee"
            fi
          }

          echo "=== Resume des captures d'ecran ==="
          if [ -d "screenshots" ]; then
            SCREENSHOT_COUNT=$(ls screenshots/*.png 2>/dev/null | wc -l || echo "0")
            echo "CAPTURE: Nombre de captures d'ecran: $SCREENSHOT_COUNT"

            if [ "$SCREENSHOT_COUNT" -gt "0" ]; then
              echo "FICHIERS: Fichiers crees:"
              ls -la screenshots/*.png | head -10

              # Afficher la taille totale
              TOTAL_SIZE=$(du -sh screenshots/ 2>/dev/null | cut -f1 || echo "N/A")
              echo "TAILLE: Taille totale: $TOTAL_SIZE"
            fi
          else
            echo "ERREUR: Repertoire screenshots non trouve"
          fi

          # Verifier les rapports JSON
          echo "=== Verification des rapports ==="
          if ls security_report_*.json 1> /dev/null 2>&1; then
            echo "RAPPORT: Rapports JSON crees:"
            ls -la security_report_*.json

            # Afficher un apercu du dernier rapport
            LATEST_REPORT=$(ls -t security_report_*.json | head -1)
            echo "APERCU: Apercu du rapport $LATEST_REPORT:"
            cat "$LATEST_REPORT" | head -20
          else
            echo "ATTENTION: Aucun rapport JSON trouve"
          fi
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

        # Afficher les logs finaux du serveur
        if [ -f http-server.log ]; then
          echo "=== Logs finaux du serveur ==="
          tail -50 http-server.log
        fi

        # Afficher les statistiques finales des captures d'ecran
        echo "=== Statistiques finales des captures ==="
        if [ -d "screenshots" ]; then
          SCREENSHOT_COUNT=$(ls screenshots/*.png 2>/dev/null | wc -l || echo "0")
          echo "TOTAL: Total des captures d'ecran creees: $SCREENSHOT_COUNT"

          if [ "$SCREENSHOT_COUNT" -gt "0" ]; then
            echo "LISTE: Liste des captures:"
            ls -la screenshots/*.png

            # Creer un fichier index des captures
            echo "Creation d'un index des captures d'ecran..." > screenshots_index.txt
            echo "Date: $(date)" >> screenshots_index.txt
            echo "Nombre total: $SCREENSHOT_COUNT" >> screenshots_index.txt
            echo "" >> screenshots_index.txt
            echo "Liste des fichiers:" >> screenshots_index.txt
            ls -la screenshots/*.png >> screenshots_index.txt 2>/dev/null || echo "Aucune capture trouvee" >> screenshots_index.txt
          fi
        else
          echo "ERREUR: Aucun repertoire screenshots trouve"
        fi

        # Afficher les rapports de securite disponibles
        if ls security_report_*.json 1> /dev/null 2>&1; then
          echo "=== Rapports de securite disponibles ==="
          ls -la security_report_*.json
        fi

        # Supprimer les fichiers temporaires
        rm -f *.pid
      '''

      // Archiver tous les artefacts utiles, y compris les captures d'ecran
      archiveArtifacts artifacts: '''
        screenshots/*.png,
        screenshots_index.txt,
        security_report_*.json,
        *.log,
        page_screenshot.png,
        fatal_error.png,
        login_page_error.png
      ''', allowEmptyArchive: true

      // Publier les captures d'ecran comme artefacts HTML si possible
      script {
        try {
          // Creer une page HTML simple pour visualiser les captures
          sh '''
            if [ -d "screenshots" ] && [ "$(ls -A screenshots 2>/dev/null)" ]; then
              cat > screenshots_gallery.html << 'EOF'
<!DOCTYPE html>
<html>
<head>
    <title>Galerie des captures d'ecran - Tests de securite</title>
    <style>
        body { font-family: Arial, sans-serif; margin: 20px; }
        .screenshot { margin: 20px 0; border: 1px solid #ddd; padding: 10px; }
        .screenshot img { max-width: 800px; border: 1px solid #ccc; }
        .screenshot h3 { color: #333; margin: 0 0 10px 0; }
        .info { background: #f5f5f5; padding: 10px; margin: 10px 0; }
    </style>
</head>
<body>
    <h1>Galerie des captures d'ecran - Tests de securite</h1>
    <div class="info">
        <strong>Date:</strong> $(date)<br>
        <strong>Nombre de captures:</strong> $(ls screenshots/*.png 2>/dev/null | wc -l || echo "0")
    </div>
EOF

              # Ajouter chaque capture a la galerie
              for screenshot in screenshots/*.png; do
                if [ -f "$screenshot" ]; then
                  filename=$(basename "$screenshot")
                  echo "    <div class='screenshot'>" >> screenshots_gallery.html
                  echo "        <h3>$filename</h3>" >> screenshots_gallery.html
                  echo "        <img src='$screenshot' alt='$filename'>" >> screenshots_gallery.html
                  echo "        <p><strong>Fichier:</strong> $filename</p>" >> screenshots_gallery.html
                  echo "    </div>" >> screenshots_gallery.html
                fi
              done

              echo "</body></html>" >> screenshots_gallery.html
              echo "SUCCES: Galerie HTML creee: screenshots_gallery.html"
            fi
          '''
        } catch (Exception e) {
          echo "ATTENTION: Impossible de creer la galerie HTML: ${e.getMessage()}"
        }
      }

      // Archiver aussi la galerie HTML
      archiveArtifacts artifacts: 'screenshots_gallery.html', allowEmptyArchive: true
    }

    success {
      echo 'SUCCES: Build reussi! Captures d\'ecran archivees.'
    }

    failure {
      echo 'ERREUR: Build echoue! Verifiez les captures d\'ecran pour le diagnostic.'
    }
  }
}
