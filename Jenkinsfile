pipeline {
  agent any

  environment {
    CHROME_BIN = '/usr/bin/google-chrome'
    CHROMEDRIVER_BIN = '/usr/local/bin/chromedriver'
    PYTHONPATH = "/usr/bin/python3"
  }

  stages {
    stage('Clone') {
      steps {
        git url: 'https://github.com/mainProgram/patient-front.git', branch: 'main'
      }
    }

    stage('Install dependencies') {
      steps {
        dir('patient-front') {
          sh '''
            npm install
            pip install selenium

          '''
        }
      }
    }

    stage('Build Angular app') {
      steps {
        dir('patient-front') {
          sh 'ng build --configuration production'
        }
      }
    }

    stage('Start Angular') {
      steps {
        sh 'nohup npx http-server ./dist/patient-front -p 4200 &'
        sh 'sleep 5'
      }
    }

    stage('Run Selenium Python Test') {
      steps {
        sh 'xvfb-run ${PYTHONPATH} selenium_login_test.py'
      }
    }

    //stage('Run Selenium Login Test') {
    //  steps {
    //    dir('patient-front') {
    //      sh 'python3 tests/auth.py'
    //    }
    //  }
    //}
  }
}
