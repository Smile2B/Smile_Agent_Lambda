#!/bin/bash
cd Backend || { echo "Error: backend directory not found"; exit 1; }
# Configuration
AWS_REGION="us-east-1"
ECR_REPO_NAME="claude3-agent"
LAMBDA_FUNCTION_NAME="claude3-agent-function"
LAMBDA_ROLE_ARN="arn:aws:iam::905418109231:role/smile-agent-lambda-role"
LAMBDA_MEMORY=4096
LAMBDA_TIMEOUT=900
LAMBDA_EPHEMERAL_STORAGE=10240

# Ensure AWS CLI is configured
if ! aws sts get-caller-identity &> /dev/null; then
    echo "Error: AWS CLI not configured. Please run 'aws configure' first."
    exit 1
fi

# Get AWS account ID
AWS_ACCOUNT_ID=$(aws sts get-caller-identity --query Account --output text)

# ECR repository should exist, log if it doesn't
if ! aws ecr describe-repositories --repository-names ${ECR_REPO_NAME} &> /dev/null; then
    echo "Warning: ECR repository ${ECR_REPO_NAME} does not exist. Please create it first."
    exit 1
fi

# Authenticate Docker to ECR
echo "Authenticating Docker to ECR..."
aws ecr get-login-password --region ${AWS_REGION} | docker login --username AWS --password-stdin ${AWS_ACCOUNT_ID}.dkr.ecr.${AWS_REGION}.amazonaws.com

# Build Docker image
echo "Building Docker image..."
docker build -t ${ECR_REPO_NAME}:latest .

# Check if Docker build was successful
if [ $? -eq 0 ]; then
    echo "Docker image built successfully"
    
    # Tag and push the image
    echo "Tagging and pushing image to ECR..."
    docker tag ${ECR_REPO_NAME}:latest ${AWS_ACCOUNT_ID}.dkr.ecr.${AWS_REGION}.amazonaws.com/${ECR_REPO_NAME}:latest
    docker push ${AWS_ACCOUNT_ID}.dkr.ecr.${AWS_REGION}.amazonaws.com/${ECR_REPO_NAME}:latest

    # Check if Lambda function exists, only update if it does
    if aws lambda get-function --function-name ${LAMBDA_FUNCTION_NAME} &> /dev/null; then
        echo "Updating Lambda function code..."
        aws lambda update-function-code \
            --function-name ${LAMBDA_FUNCTION_NAME} \
            --image-uri ${AWS_ACCOUNT_ID}.dkr.ecr.${AWS_REGION}.amazonaws.com/${ECR_REPO_NAME}:latest

        # Wait for update to complete
        echo "Waiting for Lambda function update to complete..."
        sleep 5

        # Update Lambda configuration
        echo "Updating Lambda configuration..."
        aws lambda update-function-configuration \
            --function-name ${LAMBDA_FUNCTION_NAME} \
            --timeout ${LAMBDA_TIMEOUT} \
            --memory-size ${LAMBDA_MEMORY} \
            --ephemeral-storage Size=${LAMBDA_EPHEMERAL_STORAGE}

        echo "Function update completed successfully!"
    else
        echo "Warning: Lambda function ${LAMBDA_FUNCTION_NAME} not found. No updates performed."
        exit 1
    fi
else
    echo "Docker build failed. Please check the Dockerfile and build logs."
    exit 1
fi

# Keep the latest image but remove unused images and build cache to save space
echo "Cleaning up unused Docker images..."
docker system prune -f

echo "Update completed successfully!"
