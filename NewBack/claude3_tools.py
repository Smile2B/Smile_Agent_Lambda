import base64
import io
import json
import os
import subprocess
import re
import uuid
import sys
import logging
from typing import Dict, Any, Optional, List
import boto3
from PIL import Image
from botocore.exceptions import ClientError
from langchain_community.embeddings import BedrockEmbeddings
from langchain_community.vectorstores import FAISS

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Initialize AWS clients
bedrock_runtime = boto3.client(
    service_name="bedrock-runtime",
    region_name=os.environ.get('AWS_REGION', 'us-east-1')
)
s3_client = boto3.client('s3')

BUCKET_NAME = os.environ.get('DIAGRAM_BUCKET_NAME', 'amazonqbucketsmile')
S3_PREFIX = 'smile-agent-diagrams'

def call_claude_3(
    system_prompt: str,
    prompt: str,
    model_id: str = "anthropic.claude-3-sonnet-20240229-v1:0",
) -> str:
    """Call Claude 3 with enhanced error handling"""
    try:
        prompt_config = {
            "anthropic_version": "bedrock-2023-05-31",
            "max_tokens": 4096,
            "system": system_prompt,
            "messages": [
                {
                    "role": "user",
                    "content": [
                        {"type": "text", "text": prompt},
                    ],
                }
            ],
        }
        body = json.dumps(prompt_config)
        
        response = bedrock_runtime.invoke_model(
            body=body,
            modelId=model_id,
            accept="application/json",
            contentType="application/json"
        )
        
        response_body = json.loads(response.get("body").read())
        return response_body.get("content")[0].get("text")
        
    except Exception as e:
        logger.error(f"Error calling Claude 3: {e}")
        raise
def pil_to_base64(image: Image, format: str = "PNG") -> str:
    """Convert PIL image to base64"""
    try:
        with io.BytesIO() as buffer:
            image.save(buffer, format)
            return base64.b64encode(buffer.getvalue()).decode()
    except Exception as e:
        logger.error(f"Error converting image to base64: {e}")
        raise

def gen_image_caption(base64_string: str) -> str:
    """Generate caption for AWS architecture diagram"""
    try:
        system_prompt = """
        You are an AWS Solutions Architect explaining architecture diagrams.
        Provide clear, technical explanations of AWS architecture diagrams, including:
        - Purpose and functionality of each service
        - Service interactions and data flows
        - Design patterns and best practices
        - Security considerations
        - Scalability aspects
        """
        
        prompt_config = {
            "anthropic_version": "bedrock-2023-05-31",
            "max_tokens": 4096,
            "system": system_prompt,
            "messages": [
                {
                    "role": "user",
                    "content": [
                        {
                            "type": "image",
                            "source": {
                                "type": "base64",
                                "media_type": "image/png",
                                "data": base64_string,
                            },
                        },
                        {
                            "type": "text",
                            "text": "Please describe this AWS architecture diagram, explaining the purpose of each service, their interactions, and any relevant design considerations or best practices.",
                        },
                    ],
                }
            ],
        }
        
        body = json.dumps(prompt_config)
        response = bedrock_runtime.invoke_model(
            body=body,
            modelId="anthropic.claude-3-sonnet-20240229-v1:0",
            accept="application/json",
            contentType="application/json"
        )
        
        response_body = json.loads(response.get("body").read())
        return response_body.get("content")[0].get("text")
        
    except Exception as e:
        logger.error(f"Error generating image caption: {e}")
        raise
class DiagramGenerator:
    def __init__(self):
        self.temp_dir = '/tmp'
        os.makedirs(self.temp_dir, exist_ok=True)
        os.environ['DIAGRAMS_OUTPUT_DIR'] = self.temp_dir
        self.service_mapping = self._load_service_mapping()
        
        # Set Graphviz configuration for Lambda environment
        os.environ['PATH'] = f"{os.environ.get('PATH')}:/opt/graphviz/bin"
        os.environ['LD_LIBRARY_PATH'] = f"{os.environ.get('LD_LIBRARY_PATH', '')}:/opt/graphviz/lib"

    def _load_service_mapping(self) -> Dict[str, str]:
        try:
            mapping_path = os.path.join(os.path.dirname(__file__), "diag_mapping.json")
            with open(mapping_path, "r") as f:
                return json.load(f)
        except Exception as e:
            logger.error(f"Error loading service mapping: {e}")
            return {}

    def _call_claude_3_fill(
        self,
        system_prompt: str,
        prompt: str,
        model_id: str = "anthropic.claude-3-sonnet-20240229-v1:0"
    ) -> str:
        """Special Claude 3 call for diagram code generation"""
        try:
            prompt_config = {
                "anthropic_version": "bedrock-2023-05-31",
                "max_tokens": 4096,
                "system": system_prompt,
                "messages": [
                    {
                        "role": "user",
                        "content": [{"type": "text", "text": prompt}],
                    },
                    {
                        "role": "assistant",
                        "content": [
                            {
                                "type": "text",
                                "text": "Here is the code with no explanation ```python",
                            },
                        ],
                    },
                ],
            }
            
            body = json.dumps(prompt_config)
            response = bedrock_runtime.invoke_model(
                body=body,
                modelId=model_id,
                accept="application/json",
                contentType="application/json"
            )
            
            response_body = json.loads(response.get("body").read())
            return response_body.get("content")[0].get("text")
            
        except Exception as e:
            logger.error(f"Error in code generation: {e}")
            raise

    def generate_image_caption(self, base64_string: str) -> str:
        """Generate caption for AWS architecture diagram"""
        try:
            system_prompt = """
            You are an AWS Solutions Architect explaining architecture diagrams.
            Provide clear, technical explanations of AWS architecture diagrams, including:
            - Purpose and functionality of each service
            - Service interactions and data flows
            - Design patterns and best practices
            - Security considerations
            - Scalability aspects
            """
            
            prompt_config = {
                "anthropic_version": "bedrock-2023-05-31",
                "max_tokens": 4096,
                "system": system_prompt,
                "messages": [
                    {
                        "role": "user",
                        "content": [
                            {
                                "type": "image",
                                "source": {
                                    "type": "base64",
                                    "media_type": "image/png",
                                    "data": base64_string,
                                },
                            },
                            {
                                "type": "text",
                                "text": "Please describe this AWS architecture diagram, explaining the purpose of each service, their interactions, and any relevant design considerations or best practices.",
                            },
                        ],
                    }
                ],
            }
            
            body = json.dumps(prompt_config)
            response = bedrock_runtime.invoke_model(
                body=body,
                modelId="anthropic.claude-3-sonnet-20240229-v1:0",
                accept="application/json",
                contentType="application/json"
            )
            
            response_body = json.loads(response.get("body").read())
            return response_body.get("content")[0].get("text")
            
        except Exception as e:
            logger.error(f"Error generating image caption: {e}")
            raise

    def _execute_diagram_code(self, code_file: str):
        """Execute the generated diagram code with enhanced error handling"""
        try:
            # Read the code for debugging
            with open(code_file, 'r') as f:
                code_content = f.read()
            logger.info(f"Executing diagram code:\n{code_content}")
            
            # Run with full error capture
            result = subprocess.run(
                [sys.executable, code_file],
                capture_output=True,
                text=True,
                env={
                    **os.environ,
                    'PYTHONPATH': os.getenv('LAMBDA_TASK_ROOT', ''),
                    'DIAGRAMS_OUTPUT_DIR': self.temp_dir
                }
            )
            
            if result.returncode != 0:
                logger.error(f"Diagram generation stderr: {result.stderr}")
                logger.error(f"Diagram generation stdout: {result.stdout}")
                raise Exception(f"Code execution failed: {result.stderr}")
                
            logger.info("Diagram generation successful")
            
        except Exception as e:
            logger.error(f"Error executing diagram code: {str(e)}")
            raise

    def generate_diagram(self, query: str) -> Optional[Dict[str, Any]]:
        """Generate AWS architecture diagram based on query"""
        try:
            diagram_id = str(uuid.uuid4())
            code_file = os.path.join(self.temp_dir, f"diagram_{diagram_id}.py")
            output_file = os.path.join(self.temp_dir, f"diagram_{diagram_id}.png")
            
            # Generate and log the code
            code = self._generate_diagram_code(query, diagram_id)
            logger.info(f"Generated diagram code:\n{code}")
            
            # Write code to file
            with open(code_file, 'w') as f:
                f.write(code)
            
            # Execute code
            self._execute_diagram_code(code_file)
            
            # Wait for the output file to be generated
            dot_file = os.path.join(self.temp_dir, f"diagram_{diagram_id}")
            if os.path.exists(dot_file):
                # Generate PNG using dot directly
                cmd = [
                    'dot',
                    '-Tpng',
                    '-o', output_file,
                    dot_file
                ]
                subprocess.run(cmd, check=True)
            
            # Verify output file
            if not os.path.exists(output_file):
                logger.error(f"Output file not found at: {output_file}")
                logger.error(f"Directory contents: {os.listdir(self.temp_dir)}")
                raise Exception("Diagram generation failed - output file not found")
                
            # Open and verify the image before uploading
            image = Image.open(output_file)
            
            # Upload to S3
            s3_key = f"{S3_PREFIX}/diagram_{diagram_id}.png"
            try:
                with open(output_file, 'rb') as img_file:
                    s3_client.upload_fileobj(img_file, BUCKET_NAME, s3_key)
                
                url = s3_client.generate_presigned_url(
                    'get_object',
                    Params={'Bucket': BUCKET_NAME, 'Key': s3_key},
                    ExpiresIn=3600
                )
            except Exception as e:
                logger.error(f"S3 upload error: {str(e)}")
                url = None
            
            # Generate caption
            base64_image = pil_to_base64(image)
            caption = gen_image_caption(base64_image)
            
            return {
                'success': True,
                'image': image,
                'url': url,
                'caption': caption
            }
            
        except Exception as e:
            logger.error(f"Error generating diagram: {str(e)}")
            raise
            
        finally:
            # Clean up temporary files
            self._cleanup([
                code_file,
                output_file,
                os.path.join(self.temp_dir, f"diagram_{diagram_id}"),  # dot file
            ])

    def _generate_diagram_code(self, query: str, diagram_id: str) -> str:
        """Generate Python code for the diagram"""
        system_prompt = f"""
        You are an expert python programmer that has mastered the Diagrams library. 
        Generate code for AWS architecture diagrams with these requirements:
        
        1. Use only these supported services and their correct imports:
        {json.dumps(self.service_mapping, indent=2)}
        
        2. Important rules:
        - Don't use CloudWatch/monitoring services
        - For DynamoDB, use 'Dynamodb' not 'DynamoDB'
        - For Lambda, use 'Lambda' not 'LambdaFunction'
        - Do not include diagram configuration, it will be added automatically
        
        Generate only the diagram content code without the Diagram configuration.
        Example format:
        s3 = S3("S3 Bucket")
        lambda_func = Lambda("Lambda Function")
        s3 >> lambda_func
        
        Generate only the Python code, no explanations.
        """
        
        code = self._call_claude_3_fill(system_prompt, query)
        code = self._clean_code(code, diagram_id)
        code = self._correct_imports(code)
        return code

    def _clean_code(self, code: str, diagram_id: str) -> str:
        """Clean up generated code and ensure correct file paths"""
        # Remove code blocks and docstrings
        code = code.replace("```python", "").replace("```", "").replace('"""', "")
        
        # Clean up service names
        code = code.replace("DynamoDB", "Dynamodb")
        code = code.replace("LambdaFunction", "Lambda")
        
        # Remove any existing Diagram configuration
        lines = code.split("\n")
        cleaned_lines = []
        inside_diagram = False
        
        for line in lines:
            if "with Diagram(" in line:
                inside_diagram = True
                continue
            if inside_diagram and line.strip().endswith("):"):
                inside_diagram = False
                continue
            if not line.strip().startswith("from diagrams import") and not line.strip().startswith("import"):
                cleaned_lines.append(line)

        # Add proper diagram configuration with full path
        full_output_path = os.path.join(self.temp_dir, f"diagram_{diagram_id}")
        diagram_config = f'''
with Diagram(
    "AWS Architecture",
    filename="{full_output_path}",
    show=False,
    direction="LR",
    outformat="png",
    graph_attr={{"dpi": "300"}}
):
{os.linesep.join("    " + line for line in cleaned_lines if line.strip())}
'''
        return diagram_config

    def _correct_imports(self, code: str) -> str:
        """Ensure correct imports based on service mapping"""
        try:
            detected_services = set()
            for service in self.service_mapping:
                if service in code:
                    detected_services.add(service)
            
            # Generate import statements
            imports = ['from diagrams import Cluster, Diagram']
            for service in detected_services:
                module = self.service_mapping[service]
                imports.append(f"from diagrams.aws.{module} import {service}")
            
            # Add code with proper environment setup
            full_code = f'''
import os
os.environ["DIAGRAMS_OUTPUT_DIR"] = "{self.temp_dir}"
os.environ["PATH"] = "{os.environ.get('PATH')}:/opt/graphviz/bin"
os.environ["LD_LIBRARY_PATH"] = "{os.environ.get('LD_LIBRARY_PATH', '')}:/opt/graphviz/lib"

{os.linesep.join(imports)}

{code}
'''
            return full_code
            
        except Exception as e:
            logger.error(f"Error correcting imports: {str(e)}")
            raise

    def _cleanup(self, files: List[str]):
        """Clean up temporary files"""
        for file in files:
            try:
                if os.path.exists(file):
                    os.remove(file)
            except Exception as e:
                logger.warning(f"Failed to cleanup {file}: {str(e)}")

def aws_well_arch_tool(query: str) -> Dict[str, Any]:
    """AWS Well-Architected Framework tool"""
    try:
        embeddings = BedrockEmbeddings()
        vectorstore = FAISS.load_local("local_index", embeddings)
        
        docs = vectorstore.similarity_search(query)
        context = ""
        doc_sources = ""
        
        for doc in docs:
            doc_sources += f"{doc.metadata['source']}\n{doc.page_content}"
            context += doc.page_content
            
        prompt = f"""Use the following context to answer the question:
        {context}
        Question: {query}
        Answer:"""
        
        system_prompt = """
        You are an expert AWS solutions architect professional, helping customers 
        solve problems using the AWS Well-Architected Framework.
        """
        
        answer = call_claude_3(system_prompt, prompt)
        
        return {
            "ans": answer,
            "docs": doc_sources
        }
        
    except Exception as e:
        logger.error(f"Error in AWS Well-Architected tool: {e}")
        raise

def code_gen_tool(prompt: str) -> str:
    """Generate code based on user request"""
    try:
        system_prompt = """
        You are an expert programmer focused on providing concise, efficient code solutions.
        Generate well-commented, production-ready code that follows best practices.
        Provide only the code without additional explanation.
        """
        
        code = call_claude_3_code(system_prompt, prompt)
        return code.split('\n', 1)[1] if '\n' in code else code
        
    except Exception as e:
        logger.error(f"Error in code generation tool: {e}")
        raise

def call_claude_3_code(system_prompt: str, prompt: str, 
                      model_id: str = "anthropic.claude-3-sonnet-20240229-v1:0"):
    """Generate code using Claude 3"""
    try:
        prompt_config = {
            "anthropic_version": "bedrock-2023-05-31",
            "max_tokens": 4096,
            "stop_sequences": ["```"],
            "system": system_prompt,
            "messages": [
                {
                    "role": "user",
                    "content": [{"type": "text", "text": prompt}],
                },
                {"role": "assistant", "content": "```"},
            ],
        }
        
        body = json.dumps(prompt_config)
        response = bedrock_runtime.invoke_model(
            body=body,
            modelId=model_id,
            accept="application/json",
            contentType="application/json"
        )
        
        response_body = json.loads(response.get("body").read())
        return response_body.get("content")[0].get("text")
        
    except Exception as e:
        logger.error(f"Error in code generation: {e}")
        raise

def remove_first_line(text: str) -> str:
    """Remove the first line from generated code"""
    lines = text.split("\n")
    return "\n".join(lines[1:]) if len(lines) > 1 else text

def validate_environment() -> bool:
    try:
        required_env_vars = [
            'AWS_REGION',
            'DIAGRAM_BUCKET_NAME',
            'DIAGRAMS_OUTPUT_DIR'
        ]
        
        missing_vars = [var for var in required_env_vars 
                       if not os.environ.get(var)]
        
        if missing_vars:
            logger.error(f"Missing required environment variables: {missing_vars}")
            return False
            
        # Validate temp directory
        temp_dir = os.environ.get('DIAGRAMS_OUTPUT_DIR', '/tmp')
        if not os.path.exists(temp_dir):
            os.makedirs(temp_dir, exist_ok=True)
        os.chmod(temp_dir, 0o777)
        
        # Validate AWS credentials
        boto3.client('sts').get_caller_identity()
        
        # Test graphviz installation
        try:
            subprocess.run(['dot', '-V'], 
                         capture_output=True, 
                         text=True, 
                         check=True)
        except Exception as e:
            logger.error(f"Graphviz test failed: {e}")
            return False
            
        # Test diagrams library
        try:
            import diagrams
            from diagrams import Diagram
            logger.info("Diagrams library validated successfully")
        except ImportError as e:
            logger.error(f"Diagrams import failed: {e}")
            return False
            
        return True
        
    except Exception as e:
        logger.error(f"Environment validation failed: {e}")
        return False