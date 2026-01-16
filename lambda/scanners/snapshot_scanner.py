import boto3
import json
from datetime import datetime, timedelta
from typing import List, Dict

def lambda_handler(event, context):
    """
    Scans for old EBS snapshots that can be deleted
    """
    ec2 = boto3.client('ec2')
    findings = []
    
    # Define age threshold (e.g., snapshots older than 180 days)
    age_threshold_days = 180
    threshold_date = datetime.utcnow() - timedelta(days=age_threshold_days)
    
    try:
        # Get all snapshots owned by this account
        response = ec2.describe_snapshots(OwnerIds=['self'])
        
        for snapshot in response['Snapshots']:
            snapshot_age = datetime.utcnow() - snapshot['StartTime'].replace(tzinfo=None)
            
            # Check if snapshot is older than threshold
            if snapshot['StartTime'].replace(tzinfo=None) < threshold_date:
                # Calculate storage cost
                size_gb = snapshot['VolumeSize']
                monthly_cost = size_gb * 0.05  # $0.05 per GB-month for snapshots
                
                finding = {
                    'snapshot_id': snapshot['SnapshotId'],
                    'volume_id': snapshot.get('VolumeId', 'N/A'),
                    'size_gb': size_gb,
                    'start_time': snapshot['StartTime'].isoformat(),
                    'age_days': snapshot_age.days,
                    'description': snapshot.get('Description', 'No description'),
                    'monthly_cost_usd': round(monthly_cost, 2),
                    'annual_savings_usd': round(monthly_cost * 12, 2),
                    'recommendation': f'Consider deleting snapshot older than {age_threshold_days} days',
                    'severity': 'LOW' if snapshot_age.days < 365 else 'MEDIUM'
                }
                
                # Add tags if available
                if 'Tags' in snapshot:
                    tags = {tag['Key']: tag['Value'] for tag in snapshot['Tags']}
                    finding['tags'] = tags
                
                findings.append(finding)
        
        # Calculate total potential savings
        total_monthly = sum(f['monthly_cost_usd'] for f in findings)
        total_annual = sum(f['annual_savings_usd'] for f in findings)
        
        result = {
            'scan_timestamp': datetime.utcnow().isoformat(),
            'service': 'EC2',
            'finding_type': 'Old Snapshots',
            'age_threshold_days': age_threshold_days,
            'total_findings': len(findings),
            'total_monthly_savings_usd': round(total_monthly, 2),
            'total_annual_savings_usd': round(total_annual, 2),
            'findings': findings
        }
        
        print(json.dumps(result, indent=2))
        
        return {
            'statusCode': 200,
            'body': json.dumps(result)
        }
        
    except Exception as e:
        print(f"Error scanning snapshots: {str(e)}")
        return {
            'statusCode': 500,
            'body': json.dumps({'error': str(e)})
        }