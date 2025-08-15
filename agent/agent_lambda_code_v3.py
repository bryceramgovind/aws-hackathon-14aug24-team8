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
s3_folder = 'conversations/'

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
        s3_folder = body.get('s3_folder', 'conversations_test')

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
        
        # List files in the specified S3 folder
        try:
            s3_prefix = s3_folder.rstrip('/') + '/'
            file_list = []
            paginator = s3_client.get_paginator('list_objects_v2')
            for page in paginator.paginate(Bucket=s3_bucket, Prefix=s3_prefix):
                for obj in page.get('Contents', []):
                    if not obj['Key'].endswith('/'):  # Skip folders
                        file_list.append(obj['Key'])
            print(f"Files found in S3 folder '{s3_prefix}': {file_list}")
        except Exception as list_error:
            print(f"Error listing S3 files: {list_error}")
            return {
                'statusCode': 500,
                'headers': {
                    'Content-Type': 'application/json',
                    'Access-Control-Allow-Origin': '*'
                },
                'body': json.dumps({
                    'error': 'Error listing S3 files',
                    'details': str(list_error)
                })
            }

        # Track all processed files and their S3 locations
        processed_files = []
        all_message_responses = []
        processed_files_summary = []
        total_messages_processed = 0

        for file in file_list:
            print(f"Found file: {file}")
            file_clean = file.replace('/', '_').replace('.json', '').replace('conversations_test_','')

            try:
                # Read file content from S3
                file_obj = s3_client.get_object(Bucket=s3_bucket, Key=file)
                file_content = file_obj['Body'].read().decode('utf-8')
                
                # Parse JSON content
                messages = json.loads(file_content)
                
                # Ensure it's a list
                if not isinstance(messages, list):
                    print(f"Warning: {file} does not contain a JSON array, skipping")
                    continue
                
                print(f"Found {len(messages)} messages in {file}")
                file_message_responses = []

            # Process each message individually
                for msg_index, message in enumerate(messages):
                    print(f"Processing message {msg_index + 1}/{len(messages)} from {file}")
                    
                    # Create input for agent with message content
                    message_input = f"{user_input}\n\nMessage data: {json.dumps(message, indent=2)}"
                    
                    # Invoke the agent for this specific message
                    response = bedrock_agent_runtime.invoke_agent(
                        agentId=agent_id,
                        agentAliasId=agent_alias_id,
                        sessionId=session_id,
                        inputText=message_input,
                        enableTrace=True,
                        endSession=False,
                        streamingConfigurations={
                            "streamFinalResponse": True
                        }
                    )

                    # Process the streaming response
                    full_response = ""
                    if 'completion' in response:
                        for event_chunk in response['completion']:
                            if 'chunk' in event_chunk:
                                chunk = event_chunk['chunk']
                                if 'bytes' in chunk:
                                    full_response += chunk['bytes'].decode('utf-8')
                    
                    # Store this message's response
                    message_response = {
                        "file": file,
                        "message_index": msg_index,
                        "message_data": message,
                        "agent_response": full_response,
                        "processed_at": datetime.now().isoformat()
                    }
                    
                    file_message_responses.append(message_response)
                    all_message_responses.append(message_response)
                    total_messages_processed += 1
                    
                    print(f"Processed message {msg_index + 1}: {len(full_response)} chars response")
                
                # Track file processing summary
                processed_files_summary.append({
                    "file": file,
                    "messages_count": len(messages),
                    "messages_processed": len(file_message_responses),
                    "processed_at": datetime.now().isoformat()
                })
                
            except json.JSONDecodeError as json_error:
                print(f"JSON parsing error for file {file}: {json_error}")
                processed_files_summary.append({
                    "file": file,
                    "error": f"JSON parsing error: {str(json_error)}",
                    "processed_at": datetime.now().isoformat()
                })
                
            except Exception as file_error:
                print(f"Error processing file {file}: {file_error}")
                processed_files_summary.append({
                    "file": file,
                    "error": str(file_error),
                    "processed_at": datetime.now().isoformat()
                })
        
            # Create combined response data
            combined_response_data = {
                "batch_info": {
                    "timestamp": datetime.now().isoformat(),
                    "session_id": session_id,
                    "s3_folder": s3_folder,
                    "total_files_processed": len(file_list),
                    "total_messages_processed": total_messages_processed,
                    "user_input": user_input,
                    "status": "batch_complete"
                },
                "files_summary": processed_files_summary,
                "all_message_responses": all_message_responses
            }
            
            # Generate S3 key
            timestamp = datetime.now().strftime('%Y/%m/%d/%H%M%S')
            s3_key = f"agent-responses/{timestamp}-{session_id[:8]}-{file_clean}.json"
            
            # Save to S3 (optional - comment out if not needed)
            try:
                s3_client.put_object(
                    Bucket=s3_bucket,
                    Key=s3_key,
                    Body=json.dumps(combined_response_data, indent=2, ensure_ascii=False),
                    ContentType='application/json'
                )
                print(f"Response saved to S3: s3://{s3_bucket}/{s3_key}")
                combined_response_data['s3_location'] = f"s3://{s3_bucket}/{s3_key}"

                # Track this processed file
                processed_files.append({
                    "source_file": file,
                    "s3_location": f"s3://{s3_bucket}/{s3_key}",
                    "response_length": len(full_response),
                    "processed_at": datetime.now().isoformat()
                })
            except Exception as s3_error:
                print(f"S3 save error (non-critical): {s3_error}")
                # Don't fail the whole function for S3 errors
        
        summary_data = {
            "timestamp": datetime.now().isoformat(),
            "session_id": session_id,
            "s3_folder": s3_folder,
            "total_files_processed": len(file_list),
            "successful_files": len([f for f in processed_files if 'error' not in f]),
            "failed_files": len([f for f in processed_files if 'error' in f]),
            "processed_files": processed_files,
            "status": "batch_complete"
        }

        # Return proper API Gateway response
        return {
            'statusCode': 200,
            'headers': {
                'Content-Type': 'application/json',
                'Access-Control-Allow-Origin': '*'
            },
            'body': json.dumps(summary_data)
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