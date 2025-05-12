pipeline {
  agent any

  environment {
    CHROMEDRIVER_PATH = "/usr/bin/chromedriver"
    PYTHONPATH = "/usr/bin/python3"
  }

  stages {
    stage('Install Dependencies') {
      steps {
        sh '''
          npm install
          pip install selenium
        '''
      }
    }

    stage('Build Angular App') {
      steps {
        sh 'ng build --configuration production'
      }
    }

    stage('Start Angular App') {
      steps {
        // Démarrer un serveur simple en arrière-plan pour servir Angular
        sh 'nohup npx http-server ./dist/patient-front -p 4200 &'
        sh 'sleep 5'  // attendre que le serveur démarre
      }
    }

    stage('Run Selenium Python Tests') {
      steps {
        // Utiliser xvfb pour exécuter Chrome headless via selenium
        sh '''
          chmod +x ./tests/auth.py
          xvfb-run ${PYTHONPATH} auth.py
        '''
      }
    }
  }

  post {
    always {
      echo "🧪 Pipeline terminé (succès ou échec)"
    }
    failure {
      echo "❌ Échec du pipeline : vérifier les logs du test Selenium"
    }
  }
}
