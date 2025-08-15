import boto3
import json
import uuid
from datetime import datetime

# Initialize clients
bedrock_agent_runtime = boto3.client('bedrock-agent-runtime')
s3_client = boto3.client('s3')

# Configuration
agent_id = 'OWEMRO6IAT'
agent_alias_id = 'TSTALIASID'
s3_bucket = 'lucky8bucket'  # Replace with your actual bucket name
user_input = 'Run instruction for all contact_ids found. If multiple conversations are found, return all details from them.'

def lambda_handler(event, context):
    try:
        print(f'Raw event: {json.dumps(event, default=str)}')
        
        # Handle different event sources
        if 'body' in event:
            if event['body'] is None:
                body = {}
            elif isinstance(event['body'], str):
                body = json.loads(event['body']) if event['body'] else {}
            else:
                body = event['body']
        else:
            # Direct Lambda invoke
            body = event
        
        print(f'Parsed body: {json.dumps(body, default=str)}')
        
        # Extract input with fallbacks and validation
        user_input = (
            body.get('input') or 
            body.get('inputText') or 
            body.get('message') or 
            body.get('query') 
        ).strip()
        
        session_id = body.get('sessionId', str(uuid.uuid4()))
        folder = body.get('input_folder', str))
        
        print(f'Processing - user_input: "{user_input}", session_id: "{session_id}"')
        
        # Validate input is not empty
        if not user_input:
            return {
                'statusCode': 400,
                'headers': {
                    'Content-Type': 'application/json',
                    'Access-Control-Allow-Origin': '*'
                },
                'body': json.dumps({
                    'error': 'Missing required parameter',
                    'message': 'inputText cannot be empty. Please provide input in one of: input, inputText, message, or query',
                    'received_body': body
                })
            }
        
        # Invoke the agent with proper parameter name
        response = bedrock_agent_runtime.invoke_agent(
            agentId=agent_id,
            agentAliasId=agent_alias_id,
            sessionId=session_id,
            inputText=user_input,  # Fixed variable name
            enableTrace=True,  # Optional: for debugging
            endSession=False,   # Keep session open for longer responses
            streamingConfigurations={
                "streamFinalResponse": True
                # "applyGuardrailInterval": 20  # Optional: chunk size control
            }
        )

        print(f'Bedrock response received: {type(response)}')
        
        # Process the streaming response
        full_response = ""
        if 'completion' in response:
            for event_chunk in response['completion']:
                if 'chunk' in event_chunk:
                    chunk = event_chunk['chunk']
                    if 'bytes' in chunk:
                        full_response += chunk['bytes'].decode('utf-8')
        
        print(f'Full response: {full_response}')
        
        # Create response data
        response_data = {
            "timestamp": datetime.now().isoformat(),
            "agent_id": agent_id,
            "session_id": session_id,
            "input": user_input,
            "response": full_response,
            "status": "success"
        }
        
        # Generate S3 key
        timestamp = datetime.now().strftime('%Y/%m/%d/%H%M%S')
        s3_key = f"agent-responses/{timestamp}-{session_id[:8]}.json"
        
        # Save to S3 (optional - comment out if not needed)
        try:
            s3_client.put_object(
                Bucket=s3_bucket,
                Key=s3_key,
                Body=json.dumps(response_data, indent=2, ensure_ascii=False),
                ContentType='application/json'
            )
            print(f"Response saved to S3: s3://{s3_bucket}/{s3_key}")
            response_data['s3_location'] = f"s3://{s3_bucket}/{s3_key}"
        except Exception as s3_error:
            print(f"S3 save error (non-critical): {s3_error}")
            # Don't fail the whole function for S3 errors
        
        # Return proper API Gateway response
        return {
            'statusCode': 200,
            'headers': {
                'Content-Type': 'application/json',
                'Access-Control-Allow-Origin': '*'
            },
            'body': json.dumps(response_data)
        }
        
    except json.JSONDecodeError as e:
        print(f"JSON parsing error: {e}")
        return {
            'statusCode': 400,
            'headers': {
                'Content-Type': 'application/json',
                'Access-Control-Allow-Origin': '*'
            },
            'body': json.dumps({
                'error': 'Invalid JSON in request body',
                'details': str(e)
            })
        }
        
    except Exception as e:
        print(f"Error invoking agent: {e}")
        import traceback
        traceback.print_exc()
        
        return {
            'statusCode': 500,
            'headers': {
                'Content-Type': 'application/json',
                'Access-Control-Allow-Origin': '*'
            },
            'body': json.dumps({
                'error': 'Internal server error',
                'details': str(e),
                'timestamp': datetime.now().isoformat()
            })
        }