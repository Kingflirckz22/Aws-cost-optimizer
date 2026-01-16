"""
API Endpoint: Get Summary Statistics
GET /api/summary
"""
import boto3
import json
from datetime import datetime, timedelta
from decimal import Decimal
from collections import defaultdict

dynamodb = boto3.resource('dynamodb')
table = dynamodb.Table('cost-optimizer-scans')

def decimal_to_float(obj):
    """Convert DynamoDB Decimal to float"""
    if isinstance(obj, Decimal):
        return float(obj)
    raise TypeError

def lambda_handler(event, context):
    """Returns aggregated summary statistics"""
    
    headers = {
        'Content-Type': 'application/json',
        'Access-Control-Allow-Origin': '*',
        'Access-Control-Allow-Headers': 'Content-Type',
        'Access-Control-Allow-Methods': 'GET,OPTIONS'
    }
    
    try:
        # Get all scans
        response = table.scan()
        items = response.get('Items', [])
        
        if not items:
            return {
                'statusCode': 200,
                'headers': headers,
                'body': json.dumps({
                    'success': True,
                    'data': {
                        'message': 'No scan data available',
                        'latest_scan': None,
                        'trends': None
                    }
                })
            }
        
        # Sort by timestamp
        items.sort(key=lambda x: x.get('timestamp', ''), reverse=True)
        latest = items[0]
        
        # Calculate trends (last 7 days)
        seven_days_ago = (datetime.utcnow() - timedelta(days=7)).isoformat()
        recent_scans = [s for s in items if s.get('timestamp', '') >= seven_days_ago]
        
        # Aggregate by service
        service_breakdown = []
        try:
            detailed = latest.get('detailed_results')
            if isinstance(detailed, str):
                detailed = json.loads(detailed)
            
            if detailed and isinstance(detailed, list):
                breakdown = defaultdict(lambda: {'findings': 0, 'savings': 0})
                for result in detailed:
                    service = result.get('service', 'Unknown')
                    findings = result.get('total_findings', 0)
                    savings = float(result.get('total_monthly_savings_usd', 0))
                    breakdown[service]['findings'] += findings
                    breakdown[service]['savings'] += savings
                
                service_breakdown = [
                    {
                        'service': service,
                        'findings': data['findings'],
                        'monthly_savings_usd': round(data['savings'], 2)
                    }
                    for service, data in breakdown.items()
                ]
        except:
            pass
        
        # Calculate averages
        avg_monthly = sum(float(s.get('monthly_savings', 0)) for s in recent_scans) / len(recent_scans) if recent_scans else 0
        avg_findings = sum(int(s.get('total_findings', 0)) for s in recent_scans) / len(recent_scans) if recent_scans else 0
        
        # Generate insights
        insights = []
        total_findings = int(latest.get('total_findings', 0))
        monthly_savings = float(latest.get('monthly_savings', 0))
        
        if monthly_savings > 100:
            insights.append({
                'type': 'HIGH_SAVINGS',
                'severity': 'HIGH',
                'message': f'Significant cost savings opportunity: ${monthly_savings}/month available'
            })
        
        if total_findings > 10:
            insights.append({
                'type': 'MANY_FINDINGS',
                'severity': 'MEDIUM',
                'message': f'{total_findings} cost optimization opportunities found'
            })
        
        if total_findings == 0:
            insights.append({
                'type': 'OPTIMIZED',
                'severity': 'LOW',
                'message': 'Great! No cost optimization issues detected'
            })
        
        # Build summary
        summary = {
            'success': True,
            'data': {
                'latest_scan': {
                    'scan_id': latest.get('scan_id'),
                    'timestamp': latest.get('timestamp'),
                    'total_findings': total_findings,
                    'monthly_savings_usd': monthly_savings,
                    'annual_savings_usd': float(latest.get('annual_savings', 0)),
                    'status': latest.get('status')
                },
                'trends': {
                    'total_scans': len(items),
                    'scans_last_7_days': len(recent_scans),
                    'avg_monthly_savings': round(avg_monthly, 2),
                    'avg_findings_per_scan': round(avg_findings, 1)
                },
                'service_breakdown': service_breakdown,
                'insights': insights
            }
        }
        
        return {
            'statusCode': 200,
            'headers': headers,
            'body': json.dumps(summary, default=decimal_to_float)
        }
        
    except Exception as e:
        print(f"Error: {str(e)}")
        import traceback
        traceback.print_exc()
        return {
            'statusCode': 500,
            'headers': headers,
            'body': json.dumps({
                'success': False,
                'error': str(e)
            })
        }