"""
API Endpoint: Get All Scan History
GET /api/scans?limit=10
"""
import boto3
import json
from decimal import Decimal

dynamodb = boto3.resource('dynamodb')
table = dynamodb.Table('cost-optimizer-scans')

def decimal_to_float(obj):
    """Convert DynamoDB Decimal to float"""
    if isinstance(obj, Decimal):
        return float(obj)
    raise TypeError

def lambda_handler(event, context):
    """Returns historical scan results with optional pagination"""
    
    headers = {
        'Content-Type': 'application/json',
        'Access-Control-Allow-Origin': '*',
        'Access-Control-Allow-Headers': 'Content-Type',
        'Access-Control-Allow-Methods': 'GET,OPTIONS'
    }
    
    try:
        # Get query parameters
        query_params = event.get('queryStringParameters', {}) or {}
        limit = int(query_params.get('limit', 10))
        sort_order = query_params.get('sort', 'desc')
        
        # Scan table
        response = table.scan()
        items = response.get('Items', [])
        
        if not items:
            return {
                'statusCode': 200,
                'headers': headers,
                'body': json.dumps({
                    'success': True,
                    'data': {
                        'scans': [],
                        'total_count': 0,
                        'message': 'No scans found'
                    }
                })
            }
        
        # Sort by timestamp
        reverse = (sort_order == 'desc')
        items.sort(key=lambda x: x.get('timestamp', ''), reverse=reverse)
        
        # Limit results
        limited_items = items[:limit]
        
        # Format response
        scans = []
        for item in limited_items:
            scans.append({
                'scan_id': item.get('scan_id'),
                'timestamp': item.get('timestamp'),
                'status': item.get('status'),
                'total_findings': int(item.get('total_findings', 0)),
                'monthly_savings_usd': float(item.get('monthly_savings', 0)),
                'annual_savings_usd': float(item.get('annual_savings', 0))
            })
        
        result = {
            'success': True,
            'data': {
                'scans': scans,
                'total_count': len(items),
                'returned_count': len(scans),
                'limit': limit
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