import boto3
import json
from datetime import datetime
from typing import List, Dict

def lambda_handler(event, context):
    """
    Scans for unattached Elastic IPs (which incur charges)
    """
    ec2 = boto3.client('ec2')
    findings = []
    
    try:
        # Get all Elastic IPs
        response = ec2.describe_addresses()
        
        for address in response['Addresses']:
            # Check if EIP is not associated with any instance
            if 'AssociationId' not in address:
                # Unattached EIPs cost money!
                monthly_cost = 3.60  # ~$0.005 per hour
                
                finding = {
                    'allocation_id': address['AllocationId'],
                    'public_ip': address['PublicIp'],
                    'domain': address.get('Domain', 'vpc'),
                    'monthly_cost_usd': monthly_cost,
                    'annual_savings_usd': round(monthly_cost * 12, 2),
                    'recommendation': 'Release this Elastic IP if not needed, or associate it with an instance',
                    'severity': 'LOW'
                }
                
                # Add tags if available
                if 'Tags' in address:
                    tags = {tag['Key']: tag['Value'] for tag in address['Tags']}
                    finding['tags'] = tags
                
                findings.append(finding)
        
        # Calculate total potential savings
        total_monthly = sum(f['monthly_cost_usd'] for f in findings)
        total_annual = sum(f['annual_savings_usd'] for f in findings)
        
        result = {
            'scan_timestamp': datetime.utcnow().isoformat(),
            'service': 'EC2',
            'finding_type': 'Unattached Elastic IPs',
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
        print(f"Error scanning Elastic IPs: {str(e)}")
        return {
            'statusCode': 500,
            'body': json.dumps({'error': str(e)})
        }