import base64
import io
import json
import os
import subprocess
import re
from typing import Type, Union, Dict, Any, List
import logging
import sys
import boto3
from langchain_community.embeddings import BedrockEmbeddings
from langchain_community.vectorstores import FAISS
from PIL import Image
from botocore.exceptions import ClientError

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Initialize AWS clients
try:
    bedrock_runtime = boto3.client(
        service_name="bedrock-runtime",
        region_name=os.environ.get('AWS_REGION', 'us-east-1')
    )
except Exception as e:
    logger.error(f"Failed to initialize Bedrock client: {e}")
    raise

def load_json(path_to_json: str) -> Dict[str, Any]:
    """Load JSON files with proper error handling"""
    try:
        with open(path_to_json, "r") as config_file:
            conf = json.load(config_file)
            return conf
    except FileNotFoundError:
        logger.error(f"JSON file not found: {path_to_json}")
        raise
    except json.JSONDecodeError:
        logger.error(f"Invalid JSON file: {path_to_json}")
        raise
    except Exception as error:
        logger.error(f"Error loading JSON file: {error}")
        raise

# Load AWS service mapping
try:
    aws_service_to_module_mapping = load_json("diag_mapping.json")
except Exception as e:
    logger.error(f"Failed to load AWS service mapping: {e}")
    raise


def pil_to_base64(image, format="png"):
    """Convert PIL image to base64 with error handling"""
    try:
        with io.BytesIO() as buffer:
            image.save(buffer, format)
            return base64.b64encode(buffer.getvalue()).decode()
    except Exception as e:
        logger.error(f"Error converting image to base64: {e}")
        raise

def call_claude_3(
    system_prompt: str,
    prompt: str,
    model_id: str = "anthropic.claude-3-sonnet-20240229-v1:0",
):
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

    except ClientError as e:
        logger.error(f"AWS Bedrock error: {e}")
        raise
    except Exception as e:
        logger.error(f"Error calling Claude 3: {e}")
        raise


def call_claude_3_code(
    system_prompt: str,
    prompt: str,
    model_id: str = "anthropic.claude-3-sonnet-20240229-v1:0",
):
    """Call Claude 3 for code generation"""
    try:
        prompt_config = {
            "anthropic_version": "bedrock-2023-05-31",
            "max_tokens": 4096,
            "stop_sequences": ["```"],
            "system": system_prompt,
            "messages": [
                {
                    "role": "user",
                    "content": [
                        {"type": "text", "text": prompt},
                    ],
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
        results = response_body.get("content")[0].get("text")
        return results

    except Exception as e:
        logger.error(f"Error in code generation: {e}")
        raise


def gen_image_caption(base64_string):

    system_prompt = """

    You are an experienced AWS Solutions Architect with deep knowledge of AWS services and best practices for designing and implementing cloud architectures. Maintain a professional and consultative tone, providing clear and detailed explanations tailored for technical audiences. Your task is to describe and explain AWS architecture diagrams presented by users. Your descriptions should cover the purpose and functionality of the included AWS services, their interactions, data flows, and any relevant design patterns or best practices.
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
                        "text": "Please describe the following AWS architecture diagram, explaining the purpose of each service, their interactions, and any relevant design considerations or best practices.",
                    },
                ],
            }
        ],
    }

    body = json.dumps(prompt_config)

    modelId = "anthropic.claude-3-sonnet-20240229-v1:0"
    accept = "application/json"
    contentType = "application/json"

    response = bedrock_runtime.invoke_model(
        body=body, modelId=modelId, accept=accept, contentType=contentType
    )
    response_body = json.loads(response.get("body").read())

    results = response_body.get("content")[0].get("text")
    return results

def call_claude_3_fill(
    system_prompt: str,
    prompt: str,
    model_id: str = "anthropic.claude-3-sonnet-20240229-v1:0",
):

    prompt_config = {
        "anthropic_version": "bedrock-2023-05-31",
        "max_tokens": 4096,
        "system": system_prompt,
        "stop_sequences": ["```"],
        "messages": [
            {
                "role": "user",
                "content": [
                    {"type": "text", "text": prompt},
                ],
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

    modelId = model_id
    accept = "application/json"
    contentType = "application/json"

    response = bedrock_runtime.invoke_model(
        body=body, modelId=modelId, accept=accept, contentType=contentType
    )
    response_body = json.loads(response.get("body").read())

    results = response_body.get("content")[0].get("text")
    return results

def aws_well_arch_tool(query):
    """
    Use this tool for any AWS related question to help customers understand best practices 
    on building on AWS. It will use the relevant context from the AWS Well-Architected 
    Framework to answer the customer's query.
    """
    # Initialize embeddings
    embeddings = BedrockEmbeddings()
    
    try:
        # Load the vector store
        vectorstore = FAISS.load_local(
            "local_index",
            embeddings
        )
        
        # Perform similarity search
        docs = vectorstore.similarity_search(query)
        context = ""
        doc_sources_string = ""
        
        for doc in docs:
            doc_sources_string += doc.metadata["source"] + "\n" + doc.page_content
            context += doc.page_content

        prompt = f"""Use the following pieces of context to answer the question at the end.

        {context}

        Question: {query}
        Answer:"""

        system_prompt = """
        You are an expert certified AWS solutions architect professional, skilled at helping 
        customers solve their problems. You are able to reference context from the AWS 
        Well-Architected Framework to help customers solve their problem.
        """

        generated_text = call_claude_3(system_prompt, prompt)
        
        resp_json = {
            "ans": str(generated_text), 
            "docs": doc_sources_string
        }

        return resp_json
        
    except Exception as e:
        logging.error(f"Error in aws_well_arch_tool: {str(e)}")
        raise

# helper functions
def save_and_run_python_code(code: str, file_name: str = None):
    """Save and run Python code with enhanced error handling"""
    if file_name is None:
        file_name = "test_diag.py"
    
    temp_dir = '/tmp'
    file_path = os.path.join(temp_dir, file_name)
    
    try:
        os.makedirs(temp_dir, exist_ok=True)
        os.chmod(temp_dir, 0o777)
        
        code_with_output_dir = f"""
import os
os.environ['DIAGRAMS_OUTPUT_DIR'] = '/tmp'
{code}
"""
        
        with open(file_path, 'w') as file:
            file.write(code_with_output_dir)
        
        original_dir = os.getcwd()
        os.chdir(temp_dir)
        
        result = subprocess.run(
            [sys.executable, file_path],
            capture_output=True,
            text=True,
            check=True,
            timeout=30
        )
        
        return result
        
    except subprocess.TimeoutExpired:
        logger.error("Code execution timed out")
        raise
    except subprocess.CalledProcessError as e:
        logger.error(f"Error running Python code: {e.stdout}\n{e.stderr}")
        raise
    except Exception as e:
        logger.error(f"Unexpected error in save_and_run_python_code: {e}")
        raise
    finally:
        os.chdir(original_dir)
        try:
            os.remove(file_path)
        except Exception as e:
            logger.warning(f"Failed to clean up temporary file: {e}")
          
def process_code(code):
    # Split the code into lines
    lines = code.split("\n")

    # Initialize variables to store the updated code and diagram filename
    updated_lines = []
    diagram_filename = None
    inside_diagram_block = False

    for line in lines:
        if line == ".":
            line = line.replace(".", "")
        if "endoftext" in line:
            line = ""
        if "# In[" in line:
            line = ""
        if line == "```":
            line = ""

        # Check if the line contains "with Diagram("
        if "with Diagram(" in line:
            # replace / in the line with _
            line = line.replace("/", "_")

            # Extract the diagram name between "with Diagram('NAME',"
            diagram_name = (
                line.split("with Diagram(")[1].split(",")[0].strip("'").strip('"')
            )

            # Convert the diagram name to lowercase, replace spaces with underscores, and add ".png" extension
            diagram_filename = (
                diagram_name.lower()
                .replace(" ", "_")
                .replace(")", "")
                .replace('"', "")
                .replace("/", "_")
                .replace(":", "")
                + ".png"
            )

            # Check if the line contains "filename="
            if "filename=" in line:
                # Extract the filename from the "filename=" parameter
                diagram_filename = (
                    line.split("filename=")[1].split(")")[0].strip("'").strip('"')
                    + ".png"
                )

            inside_diagram_block = True

        # Check if the line contains the end of the "with Diagram:" block
        if inside_diagram_block and line.strip() == "":
            inside_diagram_block = False

        # TODO: not sure if it handles all edge cases...
        # Only include lines that are inside the "with Diagram:" block or not related to the diagram
        if inside_diagram_block or not line.strip().startswith("diag."):
            updated_lines.append(line)

    # Join the updated lines to create the updated code
    updated_code = "\n".join(updated_lines)

    return updated_code, diagram_filename

def correct_imports(code):
    """
    Uses the mapping to ensure correct imports and handles AWS service name variants
    """
    try:
        # Initialize lists to track services and their modules
        detected_services = []
        
        # Create a mapping of service variants
        service_variants = {
            'LambdaFunction': 'Lambda',
            'DynamoDb': 'Dynamodb',
            'DynamoDB': 'Dynamodb',
            'APIGateway': 'APIGateway'
        }
        
        # Detect all AWS services mentioned in the code
        for service in aws_service_to_module_mapping:
            if service in code or service_variants.get(service, '') in code:
                detected_services.append(service)
                
        logger.info(f"Detected services: {detected_services}")
        
        # Group services by their modules
        module_to_services = {}
        for service in detected_services:
            module = aws_service_to_module_mapping[service]
            if module not in module_to_services:
                module_to_services[module] = set()  # Use set to avoid duplicates
            module_to_services[module].add(service)
            
        logger.info(f"Module mapping: {module_to_services}")
        
        # Generate import statements
        import_lines = ['from diagrams import Cluster, Diagram']
        for module, services in module_to_services.items():
            services_str = ', '.join(sorted(services))  # Sort for consistency
            import_lines.append(f"from diagrams.aws.{module} import {services_str}")
            
        # Get the diagram code (everything after the imports)
        diagram_code = ''
        in_diagram = False
        for line in code.split('\n'):
            if 'with Diagram(' in line:
                in_diagram = True
                diagram_code = line + '\n'
            elif in_diagram:
                diagram_code += line + '\n'
                
        # Combine imports and diagram code
        final_code = '\n'.join(import_lines) + '\n\n' + diagram_code.strip()
        
        logger.info("Generated imports:")
        logger.info(import_lines)
        
        return final_code

    except Exception as e:
        logger.error(f"Error in correct_imports: {str(e)}")
        logger.error(f"Original code:\n{code}")
        raise

# Update claude3_tools.py - diagram_tool function

def diagram_tool(query):
    """
    Generate diagrams with proper Docker path handling
    """
    try:
        system_prompt = f"""
        You are an expert python programmer that has mastered the Diagrams library. You are able to write code to generate AWS diagrams based on what the user asks. Only return the code as it will be run through a program to generate the diagram for the user.

        Important: For DynamoDB, use 'Dynamodb' not 'DynamoDB' as the class name.
        For Lambda, use 'Lambda' not 'LambdaFunction' as the class name.

        Here is the full list of services supported along with the correct import from the library: {aws_service_to_module_mapping}
        """

        code = call_claude_3_fill(system_prompt, query)
        logger.info("Base code:")
        logger.info(code)

        # Clean up hallucinated code
        code = code.replace("DynamoDB", "Dynamodb")  # Fix common class name issues
        code = code.replace("LambdaFunction", "Lambda")
        
        code, file_name = process_code(code)
        if not file_name:
            raise ValueError("No filename was generated from the diagram code")
            
        code = code.replace("```python", "").replace("```", "").replace('"""', "")

        logger.info("Cleaned code:")
        logger.info(code)

        # Ensure proper imports
        if "Dynamodb" in code and "from diagrams.aws.database import" in code:
            code = code.replace(
                "from diagrams.aws.database import",
                "from diagrams.aws.database import Dynamodb,"
            )

        # Get the temp directory from environment variable
        temp_dir = '/tmp'
        
        # Ensure the temp directory exists
        os.makedirs(temp_dir, exist_ok=True)
        os.chmod(temp_dir, 0o777)
        
        # Construct minimal diagram code
        diagram_code = f"""
from diagrams import Cluster, Diagram
from diagrams.aws.database import Dynamodb
from diagrams.aws.compute import Lambda
from diagrams.aws.network import APIGateway

# Graph attributes
graph_attr = {{
    "splines": "ortho",
    "nodesep": "0.60",
    "ranksep": "0.75",
    "fontname": "Sans-Serif"
}}

with Diagram(
    filename="{os.path.join(temp_dir, 'diagram')}",
    show=False,
    outformat="png",
    direction="LR",
    graph_attr=graph_attr
):
    api = APIGateway("API Gateway")
    with Cluster("Lambda"):
        fn = Lambda("Function")
    db = Dynamodb("DynamoDB")
    
    api >> fn >> db
"""
        
        # Write and execute the code
        temp_file = os.path.join(temp_dir, 'diagram.py')
        with open(temp_file, 'w') as f:
            f.write(diagram_code)
            
        result = subprocess.run(
            [sys.executable, temp_file],
            env=os.environ,
            capture_output=True,
            text=True,
            timeout=30
        )
        
        if result.returncode != 0:
            raise Exception(f"Failed to generate diagram: {result.stderr}")

        # Find the generated PNG file
        png_file = os.path.join(temp_dir, 'diagram.png')
        if not os.path.exists(png_file):
            raise FileNotFoundError(f"Generated diagram not found at {png_file}")
            
        # Load and return the image
        with Image.open(png_file) as img:
            img_copy = img.copy()
            
        # Cleanup
        try:
            os.remove(temp_file)
            os.remove(png_file)
        except Exception as e:
            logger.warning(f"Cleanup warning: {e}")
            
        return img_copy

    except Exception as e:
        logger.error(f"Error in diagram_tool: {str(e)}")
        logger.error(f"Generated code:\n{diagram_code}")
        return None
   
def remove_first_line(text):
    lines = text.split("\n")
    if len(lines) > 1:
        lines = lines[1:]
    return "\n".join(lines)

def code_gen_tool(prompt):
    """
    Use this tool only when you need to generate code based on a customers's request. The input is the customer's question. The tool returns code that the customer can use.
    """
    system_prompt = """
    You are an expert programmer with extensive knowledge of various programming languages and frameworks. Maintain a professional and efficient tone, focusing on providing concise and accurate code solutions. Your task is to provide code solutions to programming problems or requirements posed by users. The code should be well-commented, efficient, and follow best practices. You should not provide any explanations or additional context unless explicitly requested. The code should be formatted correctly and ready to be copied and pasted into an editor.
    """

    generated_text = call_claude_3_code(system_prompt, prompt)
    # remove first line
    generated_text = remove_first_line(generated_text)

    return generated_text