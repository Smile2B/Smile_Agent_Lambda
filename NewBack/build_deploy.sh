# build_deploy.sh
#!/bin/bash

# Configuration
AWS_REGION="us-east-1"
AWS_ACCOUNT_ID="905418109231"
ECR_REPO_NAME="claude3-agent"
LAMBDA_FUNCTION_NAME="claude3-agent-function"
LAMBDA_ROLE_ARN="arn:aws:iam::905418109231:role/smile-agent-lambda-role"
DIAGRAM_BUCKET_NAME="amazonqbucketsmile"
S3_PREFIX="smile-agent-diagrams"

# Login to ECR
aws ecr get-login-password --region $AWS_REGION | docker login --username AWS --password-stdin $AWS_ACCOUNT_ID.dkr.ecr.$AWS_REGION.amazonaws.com

# Build Docker image
docker build -t $ECR_REPO_NAME:latest .

# Tag and push to ECR
docker tag $ECR_REPO_NAME:latest $AWS_ACCOUNT_ID.dkr.ecr.$AWS_REGION.amazonaws.com/$ECR_REPO_NAME:latest
docker push $AWS_ACCOUNT_ID.dkr.ecr.$AWS_REGION.amazonaws.com/$ECR_REPO_NAME:latest

# Update Lambda function
aws lambda update-function-code \
    --function-name $LAMBDA_FUNCTION_NAME \
    --image-uri $AWS_ACCOUNT_ID.dkr.ecr.$AWS_REGION.amazonaws.com/$ECR_REPO_NAME:latest

# Update Lambda configuration
aws lambda update-function-configuration \
    --function-name $LAMBDA_FUNCTION_NAME \
    --timeout 300 \
    --memory-size 2048 \
    --environment Variables="{
        DIAGRAM_BUCKET_NAME=$DIAGRAM_BUCKET_NAME,
        AWS_REGION=$AWS_REGION
    }" \
    --ephemeral-storage Size=10240

echo "Deployment completed successfully!"