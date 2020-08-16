pipeline {
  agent { docker { image 'python:3.7.2' } }
  stages {
    stage('build') {
      steps {
        sh 'pip install -r requirements.txt'
      }
    }
    stage('test') {
      steps {
        sh 'python backend/test/test_scaffolder_class.py'
      }
      post {
        always {
          junit 'test-reports/*.xml'
        }
      }
    }
  }
}