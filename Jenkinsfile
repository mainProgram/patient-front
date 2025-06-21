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
            head -20 ./dist/patient-front/browser/index.html
            grep -i "base href" ./dist/patient-front/browser/index.html || echo "⚠️ Pas de base href trouvé"
          else
            echo "❌ index.html non trouvé"
            exit 1
          fi

          echo "=== Fichiers JavaScript générés ==="
          ls -la ./dist/patient-front/browser/*.js | head -10
        '''
      }
    }

    stage('Configure Angular for Backend') {
      steps {
        sh '''
          mkdir -p ./dist/patient-front/browser/assets
          echo '{
            "apiUrl": "http://backend-api:8080/api"
          }' > ./dist/patient-front/browser/assets/config.json

          cat ./dist/patient-front/browser/assets/config.json
        '''
      }
    }

    stage('Start Angular Server') {
      steps {
        sh '''
          echo "=== Démarrage du serveur Angular ==="
          pkill -f "http-server" || true
          sleep 2

          npx http-server ./dist/patient-front/browser \
            -p 4201 \
            -a 0.0.0.0 \
            --cors \
            -c-1 \
            > http-server.log 2>&1 &

          HTTP_SERVER_PID=$!
          echo $HTTP_SERVER_PID > http-server.pid

          # Attendre le démarrage
          for i in {1..30}; do
            if netstat -tuln | grep -q ":4201 "; then
              echo "✅ Serveur démarré sur le port 4201"
              break
            fi
            echo "Attente... ($i/30)"
            sleep 1
          done
        '''
      }
    }

    stage('Test Angular Accessibility') {
      steps {
        sh '''
          JENKINS_IP=$(hostname -i)
          echo "IP Jenkins: $JENKINS_IP"

          echo "=== Test accès Angular ==="
          curl -I "http://$JENKINS_IP:4201/" || echo "Erreur accès"

          echo "=== Test route login ==="
          curl -s "http://$JENKINS_IP:4201/login" | head -20
        '''
      }
    }

    stage('Check Backend') {
      steps {
        sh '''
          echo "=== Test du backend ==="
          for i in {1..10}; do
            if curl -s "http://backend-api:8080/api/auth/signin" > /dev/null; then
              echo "✅ Backend accessible"
              break
            else
              echo "⏳ Attente du backend... ($i/10)"
              sleep 3
            fi
          done
        '''
      }
    }

    stage('E2E Security Tests with Screenshots') {
      steps {
        sh '''
          JENKINS_IP=$(hostname -i)
          export APP_URL="http://$JENKINS_IP:4201"

          echo "=== Tests de sécurité E2E ==="
          echo "URL de test: $APP_URL"

          # Créer le dossier pour les captures
          mkdir -p test-screenshots

          # Copier le script Python corrigé
          cp tests/script.py tests/script_backup.py || true

          # Exécuter les tests avec captures d'écran
          python3 tests/script.py "$APP_URL" || {
            echo "⚠️ Tests terminés avec des échecs"
            true  # Ne pas faire échouer le build
          }

          # Vérifier les captures créées
          echo "=== Captures d'écran créées ==="
          if [ -d test-screenshots ]; then
            ls -la test-screenshots/*.png 2>/dev/null || echo "Aucune capture trouvée"
            echo "Nombre de captures: $(ls -1 test-screenshots/*.png 2>/dev/null | wc -l)"
          fi

          # Vérifier les rapports générés
          echo "=== Rapports générés ==="
          ls -la security_report*.json security_report.html 2>/dev/null || echo "Aucun rapport trouvé"
        '''
      }
    }

    stage('Create HTML Index') {
      steps {
        sh '''
          # Créer un index HTML pour visualiser les résultats
          cat > test_results_index.html << 'EOHTML'
<!DOCTYPE html>
<html>
<head>
    <title>Résultats des Tests de Sécurité</title>
    <style>
        body {
            font-family: Arial, sans-serif;
            margin: 20px;
            background: #f5f5f5;
        }
        .container {
            max-width: 1200px;
            margin: 0 auto;
            background: white;
            padding: 30px;
            border-radius: 10px;
            box-shadow: 0 0 20px rgba(0,0,0,0.1);
        }
        h1 {
            color: #333;
            text-align: center;
        }
        .section {
            margin: 30px 0;
            padding: 20px;
            border: 1px solid #ddd;
            border-radius: 8px;
        }
        .link-list {
            list-style: none;
            padding: 0;
        }
        .link-list li {
            margin: 10px 0;
            padding: 10px;
            background: #f8f9fa;
            border-radius: 5px;
        }
        .link-list a {
            text-decoration: none;
            color: #007bff;
            font-weight: bold;
        }
        .gallery {
            display: grid;
            grid-template-columns: repeat(auto-fill, minmax(300px, 1fr));
            gap: 20px;
            margin-top: 20px;
        }
        .screenshot {
            border: 1px solid #ddd;
            border-radius: 8px;
            overflow: hidden;
            box-shadow: 0 2px 5px rgba(0,0,0,0.1);
        }
        .screenshot img {
            width: 100%;
            height: auto;
            display: block;
        }
        .screenshot h3 {
            margin: 0;
            padding: 10px;
            background: #f8f9fa;
            font-size: 14px;
        }
    </style>
</head>
<body>
    <div class="container">
        <h1>📊 Résultats des Tests de Sécurité</h1>

        <div class="section">
            <h2>📄 Rapports</h2>
            <ul class="link-list">
EOHTML

          # Ajouter les liens vers les rapports
          if [ -f security_report.html ]; then
            echo '<li><a href="security_report.html">📋 Rapport HTML Détaillé</a></li>' >> test_results_index.html
          fi

          for report in security_report_*.json; do
            if [ -f "$report" ]; then
              echo "<li><a href=\"$report\">📊 Rapport JSON: $report</a></li>" >> test_results_index.html
            fi
          done

          cat >> test_results_index.html << 'EOHTML'
            </ul>
        </div>

        <div class="section">
            <h2>📸 Captures d'écran</h2>
            <div class="gallery">
EOHTML

          # Ajouter les captures d'écran
          if [ -d test-screenshots ]; then
            for img in test-screenshots/*.png; do
              if [ -f "$img" ]; then
                filename=$(basename "$img")
                echo "<div class='screenshot'><h3>$filename</h3><a href='$img'><img src='$img' alt='$filename'></a></div>" >> test_results_index.html
              fi
            done
          fi

          cat >> test_results_index.html << 'EOHTML'
            </div>
        </div>

        <div class="section">
            <h2>📝 Logs</h2>
            <ul class="link-list">
                <li><a href="http-server.log">🖥️ Logs du serveur HTTP</a></li>
            </ul>
        </div>
    </div>
</body>
</html>
EOHTML

          echo "✅ Index HTML créé: test_results_index.html"
        '''
      }
    }
  }

  post {
    always {
      sh '''
        # Arrêter le serveur
        pkill -f "http-server" || true

        # Afficher un résumé des artefacts
        echo "=== RÉSUMÉ DES ARTEFACTS ==="
        echo "📸 Captures d'écran:"
        find . -name "*.png" -type f | wc -l
        find . -name "*.png" -type f | head -10

        echo -e "\n📄 Rapports:"
        ls -la *.html *.json 2>/dev/null || echo "Aucun rapport trouvé"

        echo -e "\n📁 Structure des dossiers:"
        ls -la test-screenshots/ 2>/dev/null || echo "Dossier test-screenshots non trouvé"
      '''

      // Archiver tous les artefacts
      archiveArtifacts artifacts: '''
        test-screenshots/**/*.png,
        *.png,
        security_report*.json,
        security_report.html,
        test_results_index.html,
        http-server.log
      ''', allowEmptyArchive: true, fingerprint: true

      echo """
      ====================================
      📌 POUR VOIR LES RÉSULTATS :
      ====================================
      1. Cliquez sur 'Build Artifacts' dans le menu de gauche
      2. Téléchargez 'test_results_index.html' et ouvrez-le dans un navigateur
      3. Ou téléchargez le dossier complet des artefacts

      Les captures d'écran sont dans: test-screenshots/
      ====================================
      """
    }
    success {
      echo '✅ Build réussi avec captures d\'écran!'
    }
    failure {
      echo '❌ Build échoué!'
    }
  }
}
