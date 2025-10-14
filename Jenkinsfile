pipeline{
    agent any
    environment {
        VENV_DIR = 'venv'
        AWS_ACCOUNT_ID = '294337990291'
        AWS_PATH = '/usr/local/bin/aws'
        AWS_REGION = 'us-east-2'
        REPOSITORY_NAMESPACE = 'courses'
        PROJECT_NAME = 'ml-project-1'
        IMAGE_TAG = 'latest'
        REPOSITORY_NAME = "${REPOSITORY_NAMESPACE}/${PROJECT_NAME}"
        ECR_REGISTRY_URL = "${AWS_ACCOUNT_ID}.dkr.ecr.${AWS_REGION}.amazonaws.com"
        REPOSITORY_URI = "${ECR_REGISTRY_URL}/${REPOSITORY_NAME}:${IMAGE_TAG}"
        ECS_CLUSTER_NAME = 'mlops-cluster'
        ECS_SERVICE_NAME = 'ml-project-service'
        APP_PORT = '5001'
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
        stage('Building and Pushing Podman Image to AWS ECR') {
            steps {
                 withCredentials([[$class: 'AmazonWebServicesCredentialsBinding', credentialsId: 'my-aws-credentials']]) {
                    script {
                        echo 'Building and Pushing Podman Image to AWS ECR'
                        sh '''
                        export PATH=$PATH:${AWS_PATH}
                        
                        # 1. Log in to the ECR Registry URL (the domain part)
                        aws ecr get-login-password --region ${AWS_REGION} | podman login --username AWS --password-stdin ${ECR_REGISTRY_URL}
                    
                        # 2. Build and tag the image using Podman 
                        podman build -t ${REPOSITORY_URI} .

                        # 3. Push the image to ECR using Podman 
                        podman push ${REPOSITORY_URI}
                        '''
                    }
                }
            }
        }
        stage('Deploy to AWS ECS') {
            steps {
                withCredentials([[$class: 'AmazonWebServicesCredentialsBinding', credentialsId: 'my-aws-credentials']]) {
                    script {
                        echo 'Deploying to AWS ECS.............'
                        sh '''
                        export PATH=$PATH:${AWS_PATH}
                        
                        # Update ECS service with the new image
                        aws ecs update-service \
                            --cluster ${ECS_CLUSTER_NAME} \
                            --service ${ECS_SERVICE_NAME} \
                            --force-new-deployment \
                            --desired-count 1 \
                            --region ${AWS_REGION}
                        
                        # Wait for the service to stabilize
                        aws ecs wait services-stable \
                            --cluster ${ECS_CLUSTER_NAME} \
                            --services ${ECS_SERVICE_NAME} \
                            --region ${AWS_REGION}
                        
                        echo 'ECS deployment completed successfully'

                        # Get the latest task ARN
                        TASK_ARN=$(aws ecs list-tasks \
                            --cluster ${ECS_CLUSTER_NAME} \
                            --service-name ${ECS_SERVICE_NAME} \
                            --region ${AWS_REGION} \
                            --desired-status RUNNING \
                            --query "taskArns[-1]" \
                            --output text)

                        echo "Found running ECS task: $TASK_ARN"

                        # Get the network interface ID (ENI)
                        ENI_ID=$(aws ecs describe-tasks \
                            --cluster ${ECS_CLUSTER_NAME} \
                            --tasks $TASK_ARN \
                            --region ${AWS_REGION} \
                            --query "tasks[0].attachments[0].details[?name=='networkInterfaceId'].value" \
                            --output text)

                        echo "Network Interface ID: $ENI_ID"

                        # Get the public IP associated with the ENI
                        PUBLIC_IP=$(aws ec2 describe-network-interfaces \
                            --network-interface-ids $ENI_ID \
                            --region ${AWS_REGION} \
                            --query "NetworkInterfaces[0].Association.PublicIp" \
                            --output text)

                        echo "======================================================="
                        echo "✅ Deployment Successful!"
                        echo "🌐 Your app is accessible at: http://$PUBLIC_IP:${APP_PORT}"
                        echo "======================================================="
                        '''
                    }
                }
            }
        }
    }
}