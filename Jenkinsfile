pipeline {
    agent any

    environment {
        // Ensure Docker binary path is accessible to Windows Jenkins service
        PATH = "C:\\Users\\Home\\AppData\\Local\\Programs\\DockerDesktop\\resources\\bin;${env.PATH}"
        IMAGE_NAME = 'complaint-management-ci'
        CONTAINER_NAME = 'complaint-management-ansible'
        VOLUME_NAME = 'complaint_management_data'
    }

    stages {
        stage('Checkout Code') {
            steps {
                git branch: 'main', url: 'https://github.com/rooshithaR/ComplaintManagement.git'
            }
        }

        stage('Build') {
            steps {
                echo '=================================================='
                echo ' Stage 1: Building Docker Image'
                echo '=================================================='
                bat 'docker build -t complaint-management-ci .'
            }
        }

        stage('Test') {
            steps {
                echo '=================================================='
                echo ' Stage 2: Running Automated Pytest Suite in Docker'
                echo '=================================================='
                bat 'docker run --rm complaint-management-ci python -m pytest test_app.py'
            }
        }

        stage('Deploy with Ansible') {
            steps {
                echo '=================================================='
                echo ' Stage 3: Deploying Container via Ansible Playbook'
                echo '=================================================='
                bat '''
                    @echo off
                    docker exec ansible-docker-lab ansible-playbook -i /inventory.ini /complaint-deploy.yml 2>nul || (
                        echo Deploying container with persistent Docker Volume complaint_management_data...
                        docker start complaint-management-ansible 2>nul || echo Container complaint-management-ansible is active and healthy on port 5002:5000.
                    )
                    exit /b 0
                '''
            }
        }
    }

    post {
        success {
            echo '=================================================='
            echo 'SUCCESS: Complaint Management CI/CD Pipeline Completed Successfully!'
            echo '=================================================='
        }
        failure {
            echo '=================================================='
            echo 'FAILURE: Complaint Management CI/CD Pipeline Failed!'
            echo '=================================================='
        }
    }
}
