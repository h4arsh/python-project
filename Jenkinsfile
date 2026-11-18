pipeline {

    agent any

    options {
        skipDefaultCheckout(true)
    }

    environment {
        PYTHON = 'C:\\Program Files\\Python312\\python.exe'
    }

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

                bat '''
                    "%PYTHON%" --version
                    "%PYTHON%" -m venv .venv
                    .venv\\Scripts\\python -m pip install --upgrade pip
                    .venv\\Scripts\\python -m pip install -r requirements.txt
                '''
            }
        }

        stage('Test') {
            steps {
                echo 'Testing Python application'

                bat '''
                    .venv\\Scripts\\python -m compileall -q .
                    .venv\\Scripts\\python -m pytest -q
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
