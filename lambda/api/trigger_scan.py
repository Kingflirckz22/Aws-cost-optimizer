"""
API Endpoint: Trigger a New Scan
POST /api/scan
"""
import boto3
import json

lambda_client = boto3.client('lambda')

def lambda_handler(event, context):
    """Triggers the master scanner to run a new scan"""
    
    headers = {
        'Content-Type': 'application/json',
        'Access-Control-Allow-Origin': '*',
        'Access-Control-Allow-Headers': 'Content-Type',
        'Access-Control-Allow-Methods': 'POST,OPTIONS'
    }
    
    try:
        # Invoke the master scanner asynchronously
        response = lambda_client.invoke(
            FunctionName='cost-optimizer-master',
            InvocationType='Event'  # Asynchronous
        )
        
        if response['StatusCode'] in [200, 202]:
            return {
                'statusCode': 200,
                'headers': headers,
                'body': json.dumps({
                    'success': True,
                    'data': {
                        'message': 'Scan triggered successfully',
                        'status': 'STARTED',
                        'note': 'Scan is running in the background. Check back in a few moments for results.'
                    }
                })
            }
        else:
            return {
                'statusCode': 500,
                'headers': headers,
                'body': json.dumps({
                    'success': False,
                    'error': 'Failed to trigger scan'
                })
            }
        
    except Exception as e:
        print(f"Error: {str(e)}")
        return {
            'statusCode': 500,
            'headers': headers,
            'body': json.dumps({
                'success': False,
                'error': str(e)
            })
        }