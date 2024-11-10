# Initialize the client
lambda_client = DirectLambdaClient(
    lambda_function_name='your-lambda-function-name',
    region_name='us-east-1',
    timeout=300  # 5 minute timeout
)

# Generate a diagram
try:
    result = lambda_client.invoke_diagram_tool(
        "Create an architecture diagram showing an S3 bucket triggering a Lambda function"
    )
    
    # Save the diagram
    lambda_client.save_diagram_to_file(
        result['image'],
        'output_diagram.png'
    )
    
    # Get the diagram explanation
    print(result['caption'])
    
except Exception as e:
    print(f"Error: {e}")