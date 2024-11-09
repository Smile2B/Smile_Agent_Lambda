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

# Configure logging with more detail
logger = logging.getLogger()
logger.setLevel(logging.INFO)

def handler(event, context):
    """Main Lambda handler"""
    try:
        # Force log the incoming event
        logger.info(f"Received event: {json.dumps(event)}")
        
        # Parse the request body with explicit logging
        if isinstance(event.get('body'), str):
            logger.info("Parsing string body")
            body = json.loads(event['body'])
        else:
            logger.info("Using dict body")
            body = event.get('body', {})
            
        logger.info(f"Parsed body: {json.dumps(body)}")
        
        tool_type = body.get('tool_type')
        query = body.get('query')
        
        logger.info(f"Tool Type: {tool_type}")
        logger.info(f"Query: {query}")
        
        # Validate input with explicit logging
        if not tool_type or not query:
            logger.error("Missing required parameters")
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
            
        # Process based on tool type with explicit logging
        try:
            logger.info(f"Processing with tool type: {tool_type}")
            
            if tool_type == "AWS Well Architected Tool":
                logger.info("Starting AWS Well Architected Tool processing")
                result = aws_well_arch_tool(query)
                logger.info("AWS Well Architected Tool processing complete")
                response_data = {
                    'success': True,
                    'type': 'well-arch',
                    'data': {
                        'answer': result['ans'],
                        'resources': result['docs'].split('\n')
                    }
                }
                
            elif tool_type == "Diagram Tool":
                logger.info("Starting Diagram Tool processing")
                # Create unique temp directory for this request
                temp_dir = f"/tmp/diagram_{uuid.uuid4()}"
                os.makedirs(temp_dir, exist_ok=True)
                os.environ['DIAGRAMS_OUTPUT_DIR'] = temp_dir
                
                try:
                    image = diagram_tool(query)
                    if image:
                        logger.info("Image generated successfully")
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
                logger.info("Starting Code Gen Tool processing")
                code = code_gen_tool(query)
                response_data = {
                    'success': True,
                    'type': 'code',
                    'data': {
                        'code': code
                    }
                }
                
            else:
                logger.error(f"Unknown tool type: {tool_type}")
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
                
            logger.info(f"Sending response: {json.dumps(response_data)}")
            return {
                'statusCode': 200,
                'headers': {
                    'Content-Type': 'application/json',
                    'Access-Control-Allow-Origin': '*'
                },
                'body': json.dumps(response_data)
            }
            
        except Exception as e:
            logger.error(f"Error processing {tool_type} request: {str(e)}", exc_info=True)
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
        logger.error(f"Error in handler: {str(e)}", exc_info=True)
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