
import json
import boto3
import uuid
import os

bedrock_agent_runtime = boto3.client('bedrock-agent-runtime')
AGENT_ID = 'Q8IKVKON2G'
AGENT_ALIAS_ID = 'AZARIFKC2W'

def lambda_handler(event, context):
    try:
        # Parse the request body
        body_obj = event.get('body')
        body = json.loads(body_obj)
        user_input = body.get('input', '')
        session_id = body.get('sessionId', str(uuid.uuid4()))
        
        # Invoke the Bedrock agent
        response = bedrock_agent_runtime.invoke_agent(
            agentId=AGENT_ID,
            agentAliasId=AGENT_ALIAS_ID,
            sessionId=session_id,
            inputText=user_input
        )
        
        # Process the response
        completion = ""
        for event in response.get('completion'):
            chunk = event.get('chunk')
            if chunk:
                completion += chunk.get('bytes').decode()
        
        return {
            'statusCode': 200,
            'headers': {
                'Content-Type': 'application/json',
                'Access-Control-Allow-Origin': '*'
            },
            'body': json.dumps({
                'response': completion,
                'sessionId': session_id
            })
        }
        
    except Exception as e:
        return {
            'statusCode': 500,
            'headers': {
                'Content-Type': 'application/json',
                'Access-Control-Allow-Origin': '*'
            },
            'body': json.dumps({
                'error': str(e)
            })
        }