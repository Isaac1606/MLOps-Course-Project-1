pipeline{
    agent any
    environment {
        VENV_DIR = 'venv'
        AWS_ACCOUNT_ID = '294337990291'
        AWS_PATH = '/usr/local/bin/aws'
        AWS_REGION = 'us-east-2'
        REPOSITORY_NAMESPACE = 'courses'
        PROJECT_NAME = 'mlproject-1'
        REPOSITORY_NAME = '${REPOSITORY_NAMESPACE}/${PROJECT_NAME}'
        IMAGE_TAG = 'latest'
        ECR_REGISTRY_URL = '${AWS_ACCOUNT_ID}.dkr.ecr.${AWS_REGION}.amazonaws.com'
    }
    stages {
        stage('Cloning Github repo to Jenkins') {
            steps {
                script{
                    echo 'Cloning Github repo to Jenkins..........'
                    checkout scmGit(branches: [[name: '*/main']], extensions: [], userRemoteConfigs: [[credentialsId: 'github-token', url: 'https://github.com/Isaac1606/MLOps-Course-Project-1.git']])
                }
            }
        }
        stage('Setting up our Virtual Environment and Installing dependencies') {
            steps {
                script{
                    echo 'Setting up our Virtual Environment and Installing dependencies'
                    sh '''
                    python -m venv ${VENV_DIR}
                    . ${VENV_DIR}/bin/activate
                    pip install --upgrade pip
                    pip install -e .
                    '''
                }
            }
        }
        stage('Building and Pushing Docker Image to AWS ECR') {
            steps {
                withCredentials([file(credentialsId: 'AWSKey', variable: 'AWS_APPLICATION_CREDENTIALS')]) {
                    script {
                        echo 'Building and Pushing Docker Image to AWS ECR'
                         // The full URI used for tagging and pushing
                        def repositoryUri = "${ECR_REGISTRY_URL}/${REPOSITORY_NAME}:${IMAGE_TAG}"
                        sh '''
                        export PATH=$PATH:$(AWS_PATH)
                        
                        # 1. Log in to the ECR Registry URL (the domain part)
                        aws ecr get-login-password --region ${AWS_REGION} | podman login --username AWS --password-stdin ${ECR_REGISTRY_URL}
                    
                        # 2. Build and tag the image using Podman (command is identical to Docker)
                        podman build -t ${repositoryUri} .

                        # 3. Push the image to ECR using Podman (command is identical to Docker)
                        podman push ${repositoryUri}
                        '''
                    }
                }
            }
        }
    }
}