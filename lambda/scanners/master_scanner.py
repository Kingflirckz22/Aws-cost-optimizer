import boto3
import json
from datetime import datetime
import sys
import os

# Add scanners directory to path
sys.path.append(os.path.join(os.path.dirname(__file__), 'scanners'))

# Import all scanners
from ebs_scanner import lambda_handler as ebs_scan
from ec2_scanner import lambda_handler as ec2_scan
from eip_scanner import lambda_handler as eip_scan
from snapshot_scanner import lambda_handler as snapshot_scan

def lambda_handler(event, context):
    """
    Master scanner that runs all cost optimization checks
    and aggregates results
    """
    print("Starting comprehensive cost optimization scan...")
    
    all_results = []
    total_monthly_savings = 0
    total_annual_savings = 0
    scan_errors = []
    
    # List of all scanners to run
    scanners = [
        ('EBS Volumes', ebs_scan),
        ('EC2 Instances', ec2_scan),
        ('Elastic IPs', eip_scan),
        ('EBS Snapshots', snapshot_scan)
    ]
    
    # Run each scanner
    for scanner_name, scanner_func in scanners:
        try:
            print(f"Running {scanner_name} scanner...")
            result = scanner_func(event, context)
            
            if result['statusCode'] == 200:
                scan_data = json.loads(result['body'])
                all_results.append(scan_data)
                
                # Aggregate savings
                total_monthly_savings += scan_data.get('total_monthly_savings_usd', 0)
                total_annual_savings += scan_data.get('total_annual_savings_usd', 0)
                
                print(f"✓ {scanner_name}: Found {scan_data['total_findings']} issues")
            else:
                scan_errors.append({
                    'scanner': scanner_name,
                    'error': result.get('body', 'Unknown error')
                })
                print(f"✗ {scanner_name}: Failed with error")
                
        except Exception as e:
            scan_errors.append({
                'scanner': scanner_name,
                'error': str(e)
            })
            print(f"✗ {scanner_name}: Exception - {str(e)}")
    
    # Create consolidated report
    report = {
        'scan_timestamp': datetime.utcnow().isoformat(),
        'scan_status': 'completed' if not scan_errors else 'completed_with_errors',
        'summary': {
            'total_scanners_run': len(scanners),
            'total_scanners_succeeded': len(all_results),
            'total_scanners_failed': len(scan_errors),
            'total_findings': sum(r['total_findings'] for r in all_results),
            'total_monthly_savings_usd': round(total_monthly_savings, 2),
            'total_annual_savings_usd': round(total_annual_savings, 2)
        },
        'detailed_results': all_results,
        'errors': scan_errors
    }
    
    # Print summary
    print("\n" + "="*60)
    print("COST OPTIMIZATION SCAN SUMMARY")
    print("="*60)
    print(f"Total Findings: {report['summary']['total_findings']}")
    print(f"Potential Monthly Savings: ${report['summary']['total_monthly_savings_usd']}")
    print(f"Potential Annual Savings: ${report['summary']['total_annual_savings_usd']}")
    print("="*60)
    
    # Save to DynamoDB (if table exists)
    try:
        save_to_dynamodb(report)
    except Exception as e:
        print(f"Note: Could not save to DynamoDB (table may not exist yet): {str(e)}")
    
    return {
        'statusCode': 200,
        'body': json.dumps(report, indent=2)
    }

def save_to_dynamodb(report):
    """
    Save scan results to DynamoDB
    """
    dynamodb = boto3.resource('dynamodb')
    
    # Check if table exists, if not skip
    table_name = 'cost-optimizer-scans'
    
    try:
        table = dynamodb.Table(table_name)
        
        # Prepare item for DynamoDB
        item = {
            'scan_id': f"scan_{datetime.utcnow().strftime('%Y%m%d_%H%M%S')}",
            'timestamp': report['scan_timestamp'],
            'total_findings': report['summary']['total_findings'],
            'monthly_savings': str(report['summary']['total_monthly_savings_usd']),
            'annual_savings': str(report['summary']['total_annual_savings_usd']),
            'detailed_results': json.dumps(report['detailed_results']),
            'status': report['scan_status']
        }
        
        table.put_item(Item=item)
        print(f"✓ Results saved to DynamoDB table: {table_name}")
        
    except Exception as e:
        # Table doesn't exist yet, that's okay
        print(f"DynamoDB save skipped: {str(e)}")

# For local testing
if __name__ == "__main__":
    result = lambda_handler({}, {})
    print(json.dumps(json.loads(result['body']), indent=2))