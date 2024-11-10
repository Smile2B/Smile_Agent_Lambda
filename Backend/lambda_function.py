import json
import os
import logging
import uuid
from claude3_tools import (
    aws_well_arch_tool,
    code_gen_tool,
    diagram_tool,
    pil_to_base64,
    gen_image_caption
)

# Configure logging
logger = logging.getLogger()
logger.setLevel(logging.INFO)

# Set environment variables
os.environ['DIAGRAMS_OUTPUT_DIR'] = '/tmp'

os.makedirs('/tmp', exist_ok=True)
os.chmod('/tmp', 0o777)

def scan_aws_services():
    """
    Scans the installed diagrams library for all available AWS services
    """
    from diagrams.aws import (
        analytics,
        compute,
        database,
        network,
        security,
        storage,
        integration
    )
    
    modules_to_scan = {
        'analytics': analytics,
        'compute': compute,
        'database': database,
        'network': network,
        'security': security,
        'storage': storage,
        'integration': integration
    }
    
    service_mapping = {}
    
    for module_name, module in modules_to_scan.items():
        try:
            # Get all classes in the module
            classes = [attr for attr in dir(module) 
                      if not attr.startswith('_')]
            
            for class_name in classes:
                service_mapping[class_name] = module_name
                print(f"Found service: {class_name} in {module_name}")
                
        except Exception as e:
            print(f"Error scanning module {module_name}: {str(e)}")
    
    return service_mapping

def test_available_services():
    """
    Tests which services can actually be imported and used
    """
    import importlib
    
    service_mapping = scan_aws_services()
    verified_services = {}
    
    for service, module in service_mapping.items():
        try:
            # Try to import and instantiate the service
            module_path = f"diagrams.aws.{module}"
            mod = importlib.import_module(module_path)
            service_class = getattr(mod, service)
            
            # Try to create an instance (this will fail if the service isn't properly implemented)
            _ = service_class("test")
            
            # If we get here, the service is available
            verified_services[service] = module
            print(f"Verified service: {service} in module {module}")
            
        except Exception as e:
            print(f"Service {service} from {module} is not usable: {str(e)}")
    
    return verified_services

def handler(event, context):
    """Main Lambda handler"""
    try:
        # Add this temporarily
        print("Starting service scan...")
        verified_services = test_available_services()
        print("Complete verified services mapping:", verified_services)
        
        # Original handler code continues...
        logger.info(f"Received event: {json.dumps(event)}")
        
        # Parse the request body
        if isinstance(event.get('body'), str):
            body = json.loads(event['body'])
        else:
            body = event.get('body', {})
            
        tool_type = body.get('tool_type')
        query = body.get('query')
        
        
        # Log parsed data
        logger.info(f"Tool Type: {tool_type}")
        logger.info(f"Query: {query}")
        
        # Validate input
        if not tool_type or not query:
            return {
                'statusCode': 400,
                'headers': {
                    'Content-Type': 'application/json',
                    'Access-Control-Allow-Origin': '*'
                },
                'body': json.dumps({
                    'success': False,
                    'message': 'Missing required parameters: tool_type and query'
                })
            }
            
        # Process based on tool type
        try:
            if tool_type == "AWS Well Architected Tool":
                result = aws_well_arch_tool(query)
                response_data = {
                    'success': True,
                    'type': 'well-arch',
                    'data': {
                        'answer': result['ans'],
                        'resources': result['docs'].split('\n')
                    }
                }
                
            elif tool_type == "Diagram Tool":
                # Create unique temp directory for this request
                temp_dir = f"/tmp/diagram_{uuid.uuid4()}"
                os.makedirs(temp_dir, exist_ok=True)
                os.environ['DIAGRAMS_OUTPUT_DIR'] = temp_dir
                
                try:
                    image = diagram_tool(query)
                    if image:
                        image_base64 = pil_to_base64(image)
                        caption = gen_image_caption(image_base64)
                        response_data = {
                            'success': True,
                            'type': 'diagram',
                            'data': {
                                'image': image_base64,
                                'caption': caption
                            }
                        }
                    else:
                        raise Exception("Failed to generate diagram")
                finally:
                    # Cleanup temp directory
                    import shutil
                    try:
                        shutil.rmtree(temp_dir)
                    except Exception as e:
                        logger.warning(f"Failed to cleanup temp directory: {e}")
                    
            elif tool_type == "Code Gen Tool":
                code = code_gen_tool(query)
                response_data = {
                    'success': True,
                    'type': 'code',
                    'data': {
                        'code': code
                    }
                }
                
            else:
                return {
                    'statusCode': 400,
                    'headers': {
                        'Content-Type': 'application/json',
                        'Access-Control-Allow-Origin': '*'
                    },
                    'body': json.dumps({
                        'success': False,
                        'message': f'Unknown tool type: {tool_type}'
                    })
                }
                
            return {
                'statusCode': 200,
                'headers': {
                    'Content-Type': 'application/json',
                    'Access-Control-Allow-Origin': '*'
                },
                'body': json.dumps(response_data)
            }
            
        except Exception as e:
            logger.error(f"Error processing {tool_type} request: {str(e)}")
            return {
                'statusCode': 500,
                'headers': {
                    'Content-Type': 'application/json',
                    'Access-Control-Allow-Origin': '*'
                },
                'body': json.dumps({
                    'success': False,
                    'message': f'Error processing request: {str(e)}'
                })
            }
            
    except Exception as e:
        logger.error(f"Error processing request: {str(e)}")
        return {
            'statusCode': 500,
            'headers': {
                'Content-Type': 'application/json',
                'Access-Control-Allow-Origin': '*'
            },
            'body': json.dumps({
                'success': False,
                'message': f'Internal server error: {str(e)}'
            })
        }