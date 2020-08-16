pipeline {
  agent { docker { image 'python:3.8.2' } }
  stages {
    stage('test') {
      steps {
        sh 'python backend/test/test_scaffolder_class.py'
      }
    }
  }
}
