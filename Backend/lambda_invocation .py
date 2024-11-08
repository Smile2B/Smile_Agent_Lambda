import boto3
import json
import base64
from typing import Dict, Any, Optional
from botocore.config import Config

class DirectLambdaClient:
    def __init__(
        self, 
        lambda_function_name: str,
        region_name: str = 'us-east-1',
        max_retries: int = 3,
        timeout: int = 300  # 5 minutes timeout
    ):
        """
        Initialize the Direct Lambda Client
        
        Args:
            lambda_function_name: Name or ARN of the Lambda function
            region_name: AWS region name
            max_retries: Maximum number of retry attempts
            timeout: Timeout in seconds for the Lambda invocation
        """
        config = Config(
            region_name=region_name,
            retries=dict(max_attempts=max_retries),
            read_timeout=timeout,
            connect_timeout=timeout
        )
        
        self.lambda_client = boto3.client('lambda', config=config)
        self.function_name = lambda_function_name

    def invoke_diagram_tool(self, query: str) -> Dict[str, Any]:
        """
        Invoke the diagram tool directly through Lambda
        
        Args:
            query: The diagram generation query
            
        Returns:
            Dict containing the response data including the generated diagram
        """
        payload = {
            'body': {
                'tool_type': 'Diagram Tool',
                'query': query
            }
        }
        
        try:
            response = self.lambda_client.invoke(
                FunctionName=self.function_name,
                InvocationType='RequestResponse',
                Payload=json.dumps(payload)
            )
            
            # Read and parse the response
            response_payload = json.loads(response['Payload'].read())
            
            if response['StatusCode'] != 200:
                raise Exception(f"Lambda invocation failed: {response_payload}")
                
            # Parse the response body
            response_body = json.loads(response_payload.get('body', '{}'))
            
            if not response_body.get('success', False):
                raise Exception(f"Tool execution failed: {response_body.get('message', 'Unknown error')}")
                
            return response_body['data']
            
        except Exception as e:
            raise Exception(f"Error invoking Lambda function: {str(e)}")

    def invoke_well_arch_tool(self, query: str) -> Dict[str, Any]:
        """
        Invoke the AWS Well-Architected tool directly through Lambda
        
        Args:
            query: The well-architected query
            
        Returns:
            Dict containing the response data including the answer and resources
        """
        payload = {
            'body': {
                'tool_type': 'AWS Well Architected Tool',
                'query': query
            }
        }
        
        try:
            response = self.lambda_client.invoke(
                FunctionName=self.function_name,
                InvocationType='RequestResponse',
                Payload=json.dumps(payload)
            )
            
            response_payload = json.loads(response['Payload'].read())
            
            if response['StatusCode'] != 200:
                raise Exception(f"Lambda invocation failed: {response_payload}")
                
            response_body = json.loads(response_payload.get('body', '{}'))
            
            if not response_body.get('success', False):
                raise Exception(f"Tool execution failed: {response_body.get('message', 'Unknown error')}")
                
            return response_body['data']
            
        except Exception as e:
            raise Exception(f"Error invoking Lambda function: {str(e)}")

    def invoke_code_gen_tool(self, query: str) -> Dict[str, Any]:
        """
        Invoke the code generation tool directly through Lambda
        
        Args:
            query: The code generation query
            
        Returns:
            Dict containing the response data including the generated code
        """
        payload = {
            'body': {
                'tool_type': 'Code Gen Tool',
                'query': query
            }
        }
        
        try:
            response = self.lambda_client.invoke(
                FunctionName=self.function_name,
                InvocationType='RequestResponse',
                Payload=json.dumps(payload)
            )
            
            response_payload = json.loads(response['Payload'].read())
            
            if response['StatusCode'] != 200:
                raise Exception(f"Lambda invocation failed: {response_payload}")
                
            response_body = json.loads(response_payload.get('body', '{}'))
            
            if not response_body.get('success', False):
                raise Exception(f"Tool execution failed: {response_body.get('message', 'Unknown error')}")
                
            return response_body['data']
            
        except Exception as e:
            raise Exception(f"Error invoking Lambda function: {str(e)}")

    def save_diagram_to_file(self, image_data: str, output_path: str) -> None:
        """
        Save a base64 encoded diagram to a file
        
        Args:
            image_data: Base64 encoded image data
            output_path: Path where the image should be saved
        """
        try:
            image_bytes = base64.b64decode(image_data)
            with open(output_path, 'wb') as f:
                f.write(image_bytes)
        except Exception as e:
            raise Exception(f"Error saving diagram: {str(e)}")
