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

    stage('Start Angular') {
      steps {
        sh '''
          # Utiliser le flag -S pour spécifier l'index.html par défaut
          npx http-server ./dist/patient-front -p 4201 -a 0.0.0.0 -S -o false &
          sleep 5
        '''
      }
    }

    stage('Selenium E2E Test') {
      steps {
        sh '''
          # Obtenir l'adresse IP du conteneur Jenkins
          JENKINS_IP=$(hostname -i)

          # Configurer l'URL pour les tests Selenium en utilisant l'adresse IP
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
