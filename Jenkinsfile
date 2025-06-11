pipeline {
  agent any

  environment {
    TEST_USERNAME = credentials('admin')
    TEST_PASSWORD = credentials('password123')
  }

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
          echo "Contenu du répertoire dist:"
          ls -la ./dist/patient-front/

          echo "Contenu du répertoire browser:"
          ls -la ./dist/patient-front/browser/ || echo "Répertoire browser non trouvé"

          echo "Vérification de l'index.html:"
          if [ -f ./dist/patient-front/browser/index.html ]; then
            ls -la ./dist/patient-front/browser/index.html
            echo "index.html trouvé dans le dossier browser"
          else
            echo "index.html non trouvé dans le dossier browser"
            exit 1
          fi
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

    stage('Start Angular') {
      steps {
        sh '''
          npx http-server ./dist/patient-front/browser -p 4201 -a 0.0.0.0 --cors &
          sleep 10
        '''
      }
    }

    stage('Check Backend') {
      steps {
        sh '''
          for i in {1..30}; do
            if curl -s "http://backend-api:8080/api/health" > /dev/null || curl -s "http://backend-api:8080/api/patients" > /dev/null; then
              echo "Backend is up and running!"
              break
            elif [ $i -eq 30 ]; then
              echo "Backend non disponible après 30 tentatives, mais continuons les tests"
            else
              echo "Waiting for backend to start... ($i/30)"
              sleep 2
            fi
          done
        '''
      }
    }

    stage('Check Angular Server') {
      steps {
        sh '''
          JENKINS_IP=$(hostname -i)
          curl -v "http://$JENKINS_IP:4201/" || echo "Erreur lors de l'accès au serveur Angular"
          echo "Angular server check complete!"
        '''
      }
    }

    stage('Security Tests - Authentication') {
      steps {
        sh '''
          JENKINS_IP=$(hostname -i)
          export APP_URL="http://$JENKINS_IP:4201"

          echo "Exécution des tests de sécurité d'authentification..."
          python3 tests/auth.py "$APP_URL"
        '''
      }
    }

    stage('Cleanup') {
      steps {
        sh 'pkill -f "http-server" || true'
      }
    }
  }

  post {
    always {
      script {
        try {
          deleteDir()
        } catch (Exception e) {
          echo "Erreur lors du nettoyage: ${e.getMessage()}"
        }
      }
    }
    success {
      echo 'Build réussi!'
    }
    failure {
      echo 'Build échoué!'
    }
  }
}
