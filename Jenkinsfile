pipeline {
    agent any

    environment {
        APP_NAME = "production-cicd-demo"
        IMAGE_NAME = "production-cicd-demo"
        IMAGE_TAG = "1.0.${BUILD_NUMBER}"
        NAMESPACE = "production-demo"
    }

    stages {

        stage('Checkout') {
            steps {
                checkout scm
            }
        }

        stage('Python Tests') {
            steps {
                sh '''
                    python3 --version
                    python3 -m pytest -v
                '''
            }
        }

        stage('Docker Build') {
            steps {
                sh '''
                    echo "Building Docker image..."
                    docker build \
                      -t ${IMAGE_NAME}:${IMAGE_TAG} \
                      .
                '''
            }
        }

        stage('Load Image into Kind') {
            steps {
                sh '''
                    echo "Loading image into Kubernetes node..."
                    docker save ${IMAGE_NAME}:${IMAGE_TAG} | \
                    docker exec -i desktop-control-plane \
                    ctr -n=k8s.io images import -
                '''
            }
        }

        stage('Deploy to Kubernetes') {
            steps {
                sh '''
                    kubectl apply -f k8s/deployment.yaml
                    kubectl apply -f k8s/service.yaml

                    kubectl -n ${NAMESPACE} \
                      set image deployment/${APP_NAME} \
                      ${APP_NAME}=${IMAGE_NAME}:${IMAGE_TAG}

                    kubectl -n ${NAMESPACE} \
                      rollout status deployment/${APP_NAME} \
                      --timeout=120s
                '''
            }
        }

        stage('Smoke Test') {
            steps {
                sh '''
                    kubectl -n ${NAMESPACE} \
                      get pods

                    kubectl -n ${NAMESPACE} \
                      get service ${APP_NAME}
                '''
            }
        }
    }

    post {
        success {
            echo 'CI/CD pipeline completed successfully.'
        }

        failure {
            echo 'CI/CD pipeline failed. Check the failed stage.'
        }
    }
}