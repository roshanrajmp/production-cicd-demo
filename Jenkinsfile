pipeline {
    agent any

    environment {
        APP_NAME   = "production-cicd-demo"
        IMAGE_NAME = "production-cicd-demo"
        IMAGE_TAG  = "1.0.${BUILD_NUMBER}"
        NAMESPACE  = "production-demo"
        VENV       = ".venv"
    }

    stages {

        stage('Checkout') {
            steps {
                checkout scm
            }
        }

        stage('Python Dependencies') {
            steps {
                sh '''
                    set -eu

                    echo "Creating Python virtual environment..."
                    python3 -m venv "$VENV"

                    echo "Installing application dependencies..."
                    "$VENV/bin/python" -m pip install \
                        --no-cache-dir \
                        -r app/requirements.txt

                    echo "Installing test dependencies..."
                    "$VENV/bin/python" -m pip install \
                        --no-cache-dir \
                        pytest httpx2
                '''
            }
        }

        stage('Python Tests') {
            steps {
                sh '''
                    set -eu

                    echo "Checking Python version..."
                    "$VENV/bin/python" --version

                    echo "Running automated tests..."
                    "$VENV/bin/python" -m pytest -v
                '''
            }
        }

        stage('Docker Build') {
            steps {
                sh '''
                    set -eu

                    echo "Building Docker image..."
                    docker build \
                        -t "${IMAGE_NAME}:${IMAGE_TAG}" \
                        .
                '''
            }
        }

        stage('Load Image into Kind') {
            steps {
                sh '''
                    set -eu

                    echo "Loading image into Kubernetes node..."
                    docker save "${IMAGE_NAME}:${IMAGE_TAG}" |
                        docker exec -i desktop-control-plane \
                        ctr -n=k8s.io images import -
                '''
            }
        }

        stage('Deploy to Kubernetes') {
            steps {
                sh '''
                    set -eu

                    echo "Applying Kubernetes manifests..."
                    kubectl apply -f k8s/deployment.yaml
                    kubectl apply -f k8s/service.yaml

                    echo "Updating application image..."
                    kubectl -n "$NAMESPACE" \
                        set image deployment/"$APP_NAME" \
                        "$APP_NAME"="${IMAGE_NAME}:${IMAGE_TAG}"

                    echo "Waiting for deployment rollout..."
                    kubectl -n "$NAMESPACE" \
                        rollout status deployment/"$APP_NAME" \
                        --timeout=120s
                '''
            }
        }

        stage('Smoke Test') {
            steps {
                sh '''
                    set -eu

                    echo "Checking application pods..."
                    kubectl -n "$NAMESPACE" get pods

                    echo "Checking application service..."
                    kubectl -n "$NAMESPACE" get service "$APP_NAME"

                    echo "Checking application health endpoint..."
                    kubectl -n "$NAMESPACE" \
                        run "smoke-test-${BUILD_NUMBER}" \
                        --image=curlimages/curl:8.12.1 \
                        --restart=Never \
                        --rm -i \
                        --command -- \
                        curl -fsS \
                        "http://${APP_NAME}:8000/health"

                    echo "Smoke test completed successfully."
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

        always {
            echo 'Pipeline execution finished.'
        }
    }
}
