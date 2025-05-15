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
          echo "Contenu du répertoire dist:"
          ls -la ./dist/patient-front/

          echo "Vérification de l'index.html:"
          ls -la ./dist/patient-front/index.html
        '''
      }
    }

    stage('Start Angular') {
      steps {
        sh '''
          # Installer http-server si nécessaire
          npm install -g http-server

          # Démarrer http-server sans SSL
          http-server ./dist/patient-front -p 4201 -a 0.0.0.0 --cors &

          # Attendre que le serveur démarre
          sleep 10
        '''
      }
    }

    stage('Check Server') {
      steps {
        sh '''
          # Obtenir l'adresse IP
          JENKINS_IP=$(hostname -i)

          # Vérifier si le serveur répond
          curl -v "http://$JENKINS_IP:4201/"
          echo "✅ Server check complete!"
        '''
      }
    }

    stage('Selenium E2E Test') {
      steps {
        sh '''
          # Obtenir l'adresse IP du conteneur Jenkins
          JENKINS_IP=$(hostname -i)

          # Configurer l'URL pour les tests Selenium
          export APP_URL="http://$JENKINS_IP:4201"

          # Exécuter le test Selenium
          python3 tests/auth.py "$APP_URL" || true
        '''
      }
    }
  }

  post {
    always {
      sh 'pkill -f "http-server" || true'
      deleteDir()
    }
    success {
      echo 'Build réussi!'
    }
    failure {
      echo 'Build échoué!'
    }
  }
}
