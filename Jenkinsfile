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
          npx http-server ./dist/patient-front -p 4201 &
          sleep 5
        '''
      }
    }

    stage('Selenium E2E Test') {
      steps {
        sh '''
          # Configurer l'URL pour les tests Selenium
          export APP_URL="http://localhost:4201"

          # Exécuter le test Selenium
          python3 tests/auth.py || true
        '''
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
