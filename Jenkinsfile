pipeline {
  agent any

  tools {
    nodejs 'NodeJS 19'  // Nom de l'installation NodeJS dans Jenkins
  }

  environment {
    CHROME_BIN = '/usr/bin/google-chrome'
  }

  stages {
    stage('Checkout') {
      steps {
        checkout scm
      }
    }

    stage('Install Dependencies') {
      steps {
        sh 'npm install'
      }
    }

    stage('Lint') {
      steps {
        sh 'npm run lint || true'  // Le || true permet de poursuivre même si lint échoue
      }
    }

    stage('Build') {
      steps {
        sh 'npm run build -- --configuration production'
      }
    }

    stage('Test') {
      steps {
        sh 'npm run test -- --watch=false --browsers=ChromeHeadless'
      }
      post {
        always {
          junit 'junit/test-results.xml'  // Si vous configurez Karma pour produire des résultats JUnit
        }
      }
    }

    stage('Selenium E2E Test') {
      steps {
        sh '''
          # Démarrer un serveur HTTP pour servir l'application
          npx http-server ./dist/patient-front -p 4201 &
          SERVER_PID=$!

          # Attendre que le serveur soit prêt
          sleep 5

          # Exécuter le test Selenium via Python
          python3 tests/auth.py

          # Arrêter le serveur
          kill $SERVER_PID
        '''
      }
    }
  }

  post {
    always {
      cleanWs()  // Nettoie l'espace de travail après le pipeline
    }
    success {
      echo 'Build réussi!'
    }
    failure {
      echo 'Build échoué!'
    }
  }
}
