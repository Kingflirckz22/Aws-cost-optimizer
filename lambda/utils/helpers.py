"""
Shared utility functions for Cost Optimizer API
"""
import json
from decimal import Decimal

def decimal_to_float(obj):
    """
    Convert DynamoDB Decimal types to float for JSON serialization
    """
    if isinstance(obj, Decimal):
        return float(obj)
    raise TypeError

def create_response(status_code, body, headers=None):
    """
    Create API Gateway response with proper CORS headers
    """
    default_headers = {
        'Content-Type': 'application/json',
        'Access-Control-Allow-Origin': '*',  # For CORS
        'Access-Control-Allow-Headers': 'Content-Type,X-Amz-Date,Authorization,X-Api-Key,X-Amz-Security-Token',
        'Access-Control-Allow-Methods': 'GET,POST,OPTIONS'
    }
    
    if headers:
        default_headers.update(headers)
    
    return {
        'statusCode': status_code,
        'headers': default_headers,
        'body': json.dumps(body, default=decimal_to_float)
    }

def create_error_response(status_code, error_message):
    """
    Create standardized error response
    """
    return create_response(status_code, {
        'error': error_message,
        'success': False
    })

def create_success_response(data):
    """
    Create standardized success response
    """
    return create_response(200, {
        'data': data,
        'success': True
    })