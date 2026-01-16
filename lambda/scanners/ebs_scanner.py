import boto3
import json
from datetime import datetime
from typing import List, Dict

def lambda_handler(event, context):
    """
    Scans for unattached EBS volumes and calculates potential cost savings
    """
    ec2 = boto3.client('ec2')
    findings = []
    
    try:
        # Get all EBS volumes
        response = ec2.describe_volumes()
        
        for volume in response['Volumes']:
            # Check if volume is unattached
            if volume['State'] == 'available':
                # Calculate monthly cost (approximate)
                size_gb = volume['Size']
                volume_type = volume['VolumeType']
                monthly_cost = calculate_volume_cost(size_gb, volume_type)
                
                finding = {
                    'volume_id': volume['VolumeId'],
                    'size_gb': size_gb,
                    'volume_type': volume_type,
                    'availability_zone': volume['AvailabilityZone'],
                    'created_date': volume['CreateTime'].isoformat(),
                    'monthly_cost_usd': round(monthly_cost, 2),
                    'annual_savings_usd': round(monthly_cost * 12, 2),
                    'recommendation': 'Delete unused volume or create snapshot and delete',
                    'severity': 'MEDIUM'
                }
                
                findings.append(finding)
        
        # Calculate total potential savings
        total_monthly = sum(f['monthly_cost_usd'] for f in findings)
        total_annual = sum(f['annual_savings_usd'] for f in findings)
        
        result = {
            'scan_timestamp': datetime.utcnow().isoformat(),
            'service': 'EBS',
            'finding_type': 'Unattached Volumes',
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
        print(f"Error scanning EBS volumes: {str(e)}")
        return {
            'statusCode': 500,
            'body': json.dumps({'error': str(e)})
        }

def calculate_volume_cost(size_gb: int, volume_type: str) -> float:
    """
    Calculate approximate monthly cost for EBS volume
    Prices are approximate and based on us-east-1 region
    """
    # Approximate monthly costs per GB (as of 2024)
    pricing = {
        'gp2': 0.10,      # General Purpose SSD
        'gp3': 0.08,      # General Purpose SSD (newer)
        'io1': 0.125,     # Provisioned IOPS SSD
        'io2': 0.125,     # Provisioned IOPS SSD (newer)
        'st1': 0.045,     # Throughput Optimized HDD
        'sc1': 0.015,     # Cold HDD
        'standard': 0.05  # Magnetic (legacy)
    }
    
    price_per_gb = pricing.get(volume_type, 0.10)  # Default to gp2 pricing
    return size_gb * price_per_gb