# AWS Cost Optimization Tool

A serverless tool to identify and report cloud cost optimization opportunities.

## Project Structure

```
aws-cost-optimizer/
├── README.md
├── .gitignore
├── requirements.txt
├── lambda/
│   ├── scanners/
│   │   ├── ebs_scanner.py          # Unattached EBS volumes
│   │   ├── ec2_scanner.py          # Idle EC2 instances
│   │   ├── eip_scanner.py          # Unattached Elastic IPs
│   │   └── snapshot_scanner.py     # Old snapshots
│   ├── api/
│   │   └── cost_api.py             # API Gateway handlers
│   └── utils/
│       └── helpers.py              # Shared utilities
├── terraform/
│   ├── main.tf
│   ├── variables.tf
│   ├── outputs.tf
│   ├── lambda.tf
│   ├── dynamodb.tf
│   ├── eventbridge.tf
│   └── iam.tf
├── frontend/
│   └── (React app - to be added)
└── tests/
    └── test_scanners.py
```

## Quick Start

### Prerequisites

- AWS Account with appropriate permissions
- Python 3.9 or higher
- AWS CLI configured
- Terraform installed (optional, for infrastructure)

### Step 1: Clone and Setup

```bash
# Create project directory
mkdir aws-cost-optimizer
cd aws-cost-optimizer

# Create virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install boto3 pytest
```

### Step 2: Create requirements.txt

```
boto3==1.34.14
pytest==7.4.3
pytest-mock==3.12.0
```

### Step 3: Test Scanner Locally

Create a test file `test_local.py`:

```python
import sys
sys.path.append('lambda/scanners')
from ebs_scanner import lambda_handler

# Run the scanner
result = lambda_handler({}, {})
print(result)
```

Run it:
```bash
python test_local.py
```

### Step 4: Create IAM Policy for Lambda

The Lambda function needs these permissions:

```json
{
  "Version": "2012-10-17",
  "Statement": [
    {
      "Effect": "Allow",
      "Action": [
        "ec2:DescribeVolumes",
        "ec2:DescribeInstances",
        "ec2:DescribeAddresses",
        "ec2:DescribeSnapshots",
        "cloudwatch:GetMetricStatistics",
        "ce:GetCostAndUsage"
      ],
      "Resource": "*"
    },
    {
      "Effect": "Allow",
      "Action": [
        "dynamodb:PutItem",
        "dynamodb:GetItem",
        "dynamodb:Query",
        "dynamodb:Scan"
      ],
      "Resource": "arn:aws:dynamodb:*:*:table/cost-optimizer-*"
    },
    {
      "Effect": "Allow",
      "Action": [
        "logs:CreateLogGroup",
        "logs:CreateLogStream",
        "logs:PutLogEvents"
      ],
      "Resource": "arn:aws:logs:*:*:*"
    }
  ]
}
```

## What We've Built So Far

✅ **EBS Volume Scanner** - Detects unattached EBS volumes and calculates savings

## Next Steps

1. **Add More Scanners** (EC2, EIP, Snapshots)
2. **Create DynamoDB Table** to store findings
3. **Add EventBridge Rule** for scheduled scans
4. **Build REST API** for dashboard
5. **Create Frontend Dashboard**
6. **Add Terraform Infrastructure**

## Testing Your Scanner

### Manual AWS CLI Test

Check what the scanner will find:

```bash
# List all available (unattached) volumes
aws ec2 describe-volumes --filters Name=status,Values=available
```

### Deploy to Lambda (Manual)

1. Package the code:
```bash
cd lambda/scanners
zip function.zip ebs_scanner.py
```

2. Create Lambda function in AWS Console:
   - Runtime: Python 3.9
   - Handler: ebs_scanner.lambda_handler
   - Timeout: 60 seconds
   - Memory: 256 MB

3. Upload the zip file

4. Attach IAM role with required permissions

5. Test the function

## Environment Variables

Add these to your Lambda function:

- `REGION`: AWS region to scan (default: us-east-1)
- `TABLE_NAME`: DynamoDB table name (for storing results)

## Contributing

This is a portfolio project. Feel free to extend with additional scanners and features!

## License

MIT License