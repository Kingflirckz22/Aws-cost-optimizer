import boto3
import json
from datetime import datetime, timedelta
from typing import List, Dict

def lambda_handler(event, context):
    """
    Scans for idle or underutilized EC2 instances
    """
    ec2 = boto3.client('ec2')
    cloudwatch = boto3.client('cloudwatch')
    findings = []
    
    try:
        # Get all running instances
        response = ec2.describe_instances(
            Filters=[{'Name': 'instance-state-name', 'Values': ['running']}]
        )
        
        for reservation in response['Reservations']:
            for instance in reservation['Instances']:
                instance_id = instance['InstanceId']
                instance_type = instance['InstanceType']
                
                # Get CPU utilization for last 7 days
                avg_cpu = get_average_cpu_utilization(cloudwatch, instance_id, days=7)
                
                # Flag if CPU usage is consistently low
                if avg_cpu is not None and avg_cpu < 5.0:
                    monthly_cost = estimate_instance_cost(instance_type)
                    
                    finding = {
                        'instance_id': instance_id,
                        'instance_type': instance_type,
                        'availability_zone': instance['Placement']['AvailabilityZone'],
                        'launch_time': instance['LaunchTime'].isoformat(),
                        'average_cpu_percent': round(avg_cpu, 2),
                        'monthly_cost_usd': round(monthly_cost, 2),
                        'annual_savings_usd': round(monthly_cost * 12, 2),
                        'recommendation': 'Consider stopping or downsizing this instance due to low utilization',
                        'severity': 'HIGH' if avg_cpu < 2.0 else 'MEDIUM'
                    }
                    
                    # Add tags if available
                    if 'Tags' in instance:
                        tags = {tag['Key']: tag['Value'] for tag in instance['Tags']}
                        finding['tags'] = tags
                    
                    findings.append(finding)
        
        # Calculate total potential savings
        total_monthly = sum(f['monthly_cost_usd'] for f in findings)
        total_annual = sum(f['annual_savings_usd'] for f in findings)
        
        result = {
            'scan_timestamp': datetime.utcnow().isoformat(),
            'service': 'EC2',
            'finding_type': 'Idle Instances',
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
        print(f"Error scanning EC2 instances: {str(e)}")
        return {
            'statusCode': 500,
            'body': json.dumps({'error': str(e)})
        }

def get_average_cpu_utilization(cloudwatch, instance_id: str, days: int = 7) -> float:
    """
    Get average CPU utilization for an instance over the specified period
    """
    try:
        end_time = datetime.utcnow()
        start_time = end_time - timedelta(days=days)
        
        response = cloudwatch.get_metric_statistics(
            Namespace='AWS/EC2',
            MetricName='CPUUtilization',
            Dimensions=[{'Name': 'InstanceId', 'Value': instance_id}],
            StartTime=start_time,
            EndTime=end_time,
            Period=86400,  # 1 day
            Statistics=['Average']
        )
        
        if response['Datapoints']:
            datapoints = response['Datapoints']
            avg_cpu = sum(dp['Average'] for dp in datapoints) / len(datapoints)
            return avg_cpu
        
        return None
        
    except Exception as e:
        print(f"Error getting CloudWatch metrics for {instance_id}: {str(e)}")
        return None

def estimate_instance_cost(instance_type: str) -> float:
    """
    Estimate monthly cost for EC2 instance type
    Prices are approximate for us-east-1 on-demand pricing
    """
    # Simplified pricing (actual prices vary by region and may change)
    pricing = {
        't2.micro': 8.50,
        't2.small': 17.00,
        't2.medium': 34.00,
        't2.large': 68.00,
        't3.micro': 7.60,
        't3.small': 15.20,
        't3.medium': 30.40,
        't3.large': 60.80,
        'm5.large': 70.00,
        'm5.xlarge': 140.00,
        'm5.2xlarge': 280.00,
        'c5.large': 62.00,
        'c5.xlarge': 124.00,
        'r5.large': 92.00,
        'r5.xlarge': 184.00,
    }
    
    # Return estimate or default if type not in our list
    return pricing.get(instance_type, 100.00)