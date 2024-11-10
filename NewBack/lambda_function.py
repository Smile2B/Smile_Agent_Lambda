# lambda_function.py
import json
import os
import logging
import boto3
from typing import Dict, Any
from claude3_tools import (
    aws_well_arch_tool,
    code_gen_tool,
    DiagramGenerator,
    pil_to_base64,
    gen_image_caption
)

# Configure logging
logger = logging.getLogger()
logger.setLevel(logging.INFO)

def handler(event, context):
    """Main Lambda handler"""
    try:
        logger.info(f"Received event: {json.dumps(event)}")
        
        # Parse the request body
        if isinstance(event.get('body'), str):
            body = json.loads(event['body'])
        else:
            body = event.get('body', {})
            
        tool_type = body.get('tool_type')
        query = body.get('query')
        
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
                    'message': 'Missing required parameters'
                })
            }
            
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
                generator = DiagramGenerator()
                result = generator.generate_diagram(query)
                
                if result and result.get('image'):
                    image_base64 = pil_to_base64(result['image'])
                    caption = gen_image_caption(image_base64)
                    response_data = {
                        'success': True,
                        'type': 'diagram',
                        'data': {
                            'image': image_base64,
                            'caption': caption,
                            'url': result.get('url')
                        }
                    }
                else:
                    raise Exception("Failed to generate diagram")
                    
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