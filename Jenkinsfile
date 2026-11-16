pipeline {

    agent any

    stages {

        stage('Checkout') {
            steps {
                echo 'Downloading application from GitHub'
                checkout scm
            }
        }

        stage('Install Dependencies') {
            steps {
                echo 'Installing Python dependencies'

                sh '''
                    python3 --version
                    python3 -m venv .venv
                    .venv/bin/pip install -r requirements.txt
                '''
            }
        }

        stage('Test') {
            steps {
                echo 'Testing Python application'

                sh '''
                    .venv/bin/python -m compileall -q .
                    .venv/bin/python -m pytest -q
                '''
            }
        }

        stage('Build') {
            steps {
                echo 'Application build completed'
            }
        }

    }

    post {
        success {
            echo 'CI Pipeline completed successfully!'
        }

        failure {
            echo 'Pipeline failed. Check the console output.'
        }
    }
}