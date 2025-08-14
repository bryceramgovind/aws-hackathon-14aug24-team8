import boto3
import os
import json

def retrieve_from_knowledge_base(query, knowledge_base_id, region='us-east-1'):
    """
    Retrieve information from AWS Bedrock Knowledge Base
    
    Args:
        query (str): The search query
        knowledge_base_id (str): Your Knowledge Base ID
        region (str): AWS region
    
    Returns:
        dict: Retrieved results
    """
    
    # Initialize Bedrock Agent Runtime client
    client = boto3.client('bedrock-agent-runtime', region_name=region)
    
    try:
        # Call the retrieve API
        response = client.retrieve(
            knowledgeBaseId=knowledge_base_id,
            retrievalQuery={
                'text': query
            },
            retrievalConfiguration={
                'vectorSearchConfiguration': {
                    'numberOfResults': 5  # Number of results to return
                }
            }
        )
        
        return response
        
    except Exception as e:
        print(f"Error retrieving from knowledge base: {e}")
        return None

def retrieve_and_generate(query, knowledge_base_id, model_arn, region='us-east-1'):
    """
    Retrieve from Knowledge Base and generate response using a model
    
    Args:
        query (str): The search query
        knowledge_base_id (str): Your Knowledge Base ID
        model_arn (str): Model ARN (e.g., 'arn:aws:bedrock:us-east-1::foundation-model/anthropic.claude-3-sonnet-20240229-v1:0')
        region (str): AWS region
    
    Returns:
        dict: Generated response with citations
    """
    
    client = boto3.client('bedrock-agent-runtime', region_name=region)
    
    try:
        response = client.retrieve_and_generate(
            input={
                'text': query
            },
            retrieveAndGenerateConfiguration={
                'type': 'KNOWLEDGE_BASE',
                'knowledgeBaseConfiguration': {
                    'knowledgeBaseId': knowledge_base_id,
                    'modelArn': model_arn,
                    'retrievalConfiguration': {
                        'vectorSearchConfiguration': {
                            'numberOfResults': 5
                        }
                    }
                }
            }
        )
        
        return response
        
    except Exception as e:
        print(f"Error in retrieve and generate: {e}")
        return None

# Example usage
if __name__ == "__main__":
    # Replace with your actual Knowledge Base ID
    KB_ID = os.getenv('KB_ID')
    MODEL_ARN = os.getenv('MODEL_ARN')

    query = "What are the network security best practices?"
    
    print("=== Retrieve Only ===")
    results = retrieve_from_knowledge_base(query, KB_ID)
    
    if results:
        print(f"Found {len(results['retrievalResults'])} results:")
        for i, result in enumerate(results['retrievalResults'], 1):
            print(f"\nResult {i}:")
            print(f"Score: {result['score']}")
            print(f"Content: {result['content']['text'][:200]}...")
            if 'location' in result:
                print(f"Source: {result['location']['s3Location']['uri']}")
    
    print("\n=== Retrieve and Generate ===")
    response = retrieve_and_generate(query, KB_ID, MODEL_ARN)
    
    if response:
        print(f"Generated Answer: {response['output']['text']}")
        
        if 'citations' in response:
            print(f"\nCitations ({len(response['citations'])}):")
            for i, citation in enumerate(response['citations'], 1):
                for ref in citation['retrievedReferences']:
                    print(f"{i}. {ref['location']['s3Location']['uri']}")
