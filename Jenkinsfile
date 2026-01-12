pipeline {
    agent any

    environment {
        // Use Minikube's Docker Daemon
        DOCKER_HOST = 'unix:///var/run/docker.sock'
        IMAGE_NAME = 'research-agent'
        TAG = "build-${BUILD_NUMBER}"
    }

    stages {
        stage('Checkout') {
            steps {
                checkout scm
            }
        }

        stage('Build Docker Image') {
            steps {
                script {
                    sh "docker build -t ${IMAGE_NAME}:${TAG} ."
                    // Also tag as latest so local k8s picks it up if pull policy is never
                    sh "docker tag ${IMAGE_NAME}:${TAG} ${IMAGE_NAME}:latest"
                }
            }
        }

        stage('Deploy (Update Manifest)') {
            steps {
                script {
                    // Update the deployment.yaml with the new tag
                    // Note: In a real gitops flow, we would commit this back to git.
                    // For Scenario B demo, we will just simulate the change or do a direct apply (optional)
                    // But wait, ArgoCD is watching Git. So we MUST commit to Git.
                    
                    // Allow Jenkins to push to Git
                    sh 'git config user.email "jenkins@ci.local"'
                    sh 'git config user.name "Jenkins CI"'
                    
                    // Update YAML using sed
                    sh "sed -i 's/research-agent:.*/research-agent:${TAG}/' k8s/deployment.yaml"
                    
                    // Commit and Push
                    // (Requires Credentials - we will handle this in Jenkins UI setup)
                    // sh "git commit -am 'Bump version to ${TAG}'"
                    // sh "git push origin main"
                }
            }
        }
    }
}
