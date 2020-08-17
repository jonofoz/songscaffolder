pipeline {
    agent { docker { image 'python:3.7.2' } }
    stages {
        stage('Build') {
            steps {
                echo "Building environment..."
                sh 'pip install -r requirements.txt'
                echo "requirements installed."
            }
        }
        stage('test') {
            steps {
                echo "Running Unittests..."
                sh 'python backend/test/test_scaffolder_class.py'
                echo "Done with the tests."
            }
            post {
                always {
                    echo "Finishing up!"
                    junit 'test-reports/*.xml'
                    echo "Done."
                }
            }
        }
    }
}