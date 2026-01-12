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
                withCredentials([usernamePassword(credentialsId: 'github-token', passwordVariable: 'GIT_PASSWORD', usernameVariable: 'GIT_USERNAME')]) {
                    script {
                        // Allow Jenkins to push to Git
                        sh 'git config user.email "jenkins@ci.local"'
                        sh 'git config user.name "Jenkins CI"'
                        
                        // Update YAML using sed (Replace image tag)
                        // This finds 'image: research-agent:...' and replaces it
                        sh "sed -i 's|image: research-agent:.*|image: research-agent:${TAG}|' k8s/deployment.yaml"
                        
                        // Commit and Push
                        // [skip ci] prevents infinite build loop
                        sh "git commit -am 'Bump version to ${TAG} [skip ci]'" 
                        
                        // Push using injected credentials
                        sh("git push https://${GIT_USERNAME}:${GIT_PASSWORD}@github.com/prabhudayala/research-agent.git HEAD:main")
                    }
                }
            }
        }
    }
}
