import boto3
import json
import uuid
from datetime import datetime

# Initialize clients
bedrock_agent_runtime = boto3.client('bedrock-agent-runtime')
s3_client = boto3.client('s3')

# Configuration
agent_id = 'OWEMRO6IAT'
agent_alias_id = 'LDOXC5OFNQ'
s3_bucket = 's3://lucky8bucket'  # Replace with your actual bucket name
# user_input = 'give me information about ID'

def lambda_handler(event, context):
    try:
        print(f'Raw event: {event}')
        
        # Handle different event sources (API Gateway, direct invoke, etc.)
        if 'body' in event and event['body']:
            # API Gateway event
            if isinstance(event['body'], str):
                body = json.loads(event['body'])
            else:
                body = event['body']
        else:
            # Direct Lambda invoke or other sources
            body = event
        
        print(f'Parsed body: {body}')
        
        # Extract parameters with proper fallbacks
        user_input = body.get('input', body.get('inputText', ''))
        session_id = body.get('sessionId', str(uuid.uuid4()))
        
        if not user_input:
            return {
                'statusCode': 400,
                'headers': {
                    'Content-Type': 'application/json',
                    'Access-Control-Allow-Origin': '*'
                },
                'body': json.dumps({
                    'error': 'Missing required parameter: input or inputText'
                })
            }
        
        print(f'Processing input: {user_input}, sessionId: {session_id}')
        
        # Invoke the agent with proper parameter name
        response = bedrock_agent_runtime.invoke_agent(
            agentId=agent_id,
            agentAliasId=agent_alias_id,
            sessionId=session_id,
            inputText=user_input  # Fixed variable name
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