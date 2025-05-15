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
         # Exécuter le test Selenium via Python en spécifiant l'URL
         APP_URL=http://jenkins:4201 python3 tests/auth.py

         # Ou utiliser l'adresse IP interne si le nom du service ne fonctionne pas
         # APP_URL=http://$(hostname -i):4201 python3 tests/auth.py
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
