# Build the image
docker build -t claude3-agent .

# Test the image locally (optional)
docker run --rm claude3-agent python -c "import diagrams; print('Diagrams package working')"

# Tag and push
docker tag claude3-agent:latest 905418109231.dkr.ecr.us-east-1.amazonaws.com/claude3-agent:latest
docker push 905418109231.dkr.ecr.us-east-1.amazonaws.com/claude3-agent:latest

# Update Lambda
aws lambda update-function-code \
    --function-name claude3-agent-function \
    --image-uri 905418109231.dkr.ecr.us-east-1.amazonaws.com/claude3-agent:latest