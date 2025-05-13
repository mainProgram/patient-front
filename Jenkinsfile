pipeline {
  agent any

  environment {
    CHROME_BIN = '/usr/bin/google-chrome'
    CHROMEDRIVER_BIN = '/usr/local/bin/chromedriver'
  }

  stages {
    stage('Clone') {
      steps {
        git url: 'https://github.com/mainProgram/patient-front.git', branch: 'main'
      }
    }

    stage('Install dependencies') {
      steps {
        dir('angular-app') {
          sh 'npm install'
        }
      }
    }

    stage('Build Angular app') {
      steps {
        dir('angular-app') {
          sh 'ng build'
        }
      }
    }

    stage('Run Selenium Login Test') {
      steps {
        dir('e2e-tests') {
          sh 'python3 ./tests/auth.py'
        }
      }
    }
  }
}
