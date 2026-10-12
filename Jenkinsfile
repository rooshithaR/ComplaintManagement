pipeline {
    agent any

    environment {
        IMAGE_NAME = 'complaint-management-ci'
        ANSIBLE_CONTAINER = 'ansible-docker-lab'
        PLAYBOOK_PATH = '/complaint-deploy.yml'
        INVENTORY_PATH = '/inventory.ini'
    }

    stages {
        stage('Build') {
            steps {
                echo '=================================================='
                echo ' Stage 1: Building Docker Image'
                echo '=================================================='
                sh 'docker build -t complaint-management-ci .'
            }
        }

        stage('Test') {
            steps {
                echo '=================================================='
                echo ' Stage 2: Running Automated Pytest Suite in Docker'
                echo '=================================================='
                sh 'docker run --rm complaint-management-ci python -m pytest test_app.py'
            }
        }

        stage('Deploy with Ansible') {
            steps {
                echo '=================================================='
                echo ' Stage 3: Deploying Container via Ansible Playbook'
                echo '=================================================='
                sh '''
                    docker exec ${ANSIBLE_CONTAINER} \
                    ansible-playbook \
                    -i ${INVENTORY_PATH} \
                    ${PLAYBOOK_PATH}
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
        always {
            echo 'Pipeline execution cycle concluded.'
        }
    }
}
