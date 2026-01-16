"""
API Endpoint: Get Latest Scan Results
GET /api/latest
"""
import boto3
import json
from decimal import Decimal

dynamodb = boto3.resource('dynamodb')
table = dynamodb.Table('cost-optimizer-scans')

def decimal_to_float(obj):
    #Convert DynamoDB Decimal to float
    if isinstance(obj, Decimal):
        return float(obj)
    raise TypeError

def lambda_handler(event, context):
    #Returns the most recent scan results
    
    headers = {
        'Content-Type': 'application/json',
        'Access-Control-Allow-Origin': '*',
        'Access-Control-Allow-Headers': 'Content-Type',
        'Access-Control-Allow-Methods': 'GET,OPTIONS'
    }
    
    try:
        # Scan table and get all items
        response = table.scan()
        items = response.get('Items', [])
        
        if not items:
            return {
                'statusCode': 200,
                'headers': headers,
                'body': json.dumps({
                    'success': True,
                    'data': {
                        'message': 'No scans found',
                        'scan': None
                    }
                })
            }
        
        # Sort by timestamp (most recent first)
        items.sort(key=lambda x: x.get('timestamp', ''), reverse=True)
        latest_scan = items[0]
        
        # Parse detailed results if stored as JSON string
        detailed_results = latest_scan.get('detailed_results', [])
        if isinstance(detailed_results, str):
            try:
                detailed_results = json.loads(detailed_results)
            except:
                detailed_results = []
        
        # Format response
        result = {
            'success': True,
            'data': {
                'scan_id': latest_scan.get('scan_id'),
                'timestamp': latest_scan.get('timestamp'),
                'status': latest_scan.get('status'),
                'summary': {
                    'total_findings': int(latest_scan.get('total_findings', 0)),
                    'monthly_savings_usd': float(latest_scan.get('monthly_savings', 0)),
                    'annual_savings_usd': float(latest_scan.get('annual_savings', 0))
                },
                'detailed_results': detailed_results
            }
        }
        
        return {
            'statusCode': 200,
            'headers': headers,
            'body': json.dumps(result, default=decimal_to_float)
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