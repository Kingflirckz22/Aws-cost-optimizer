# AWS Cost Optimizer

> A serverless application that automatically identifies and reports AWS cost optimization opportunities, helping reduce cloud spending through automated resource scanning and intelligent recommendations.

## Project Overview

AWS Cost Optimizer is a production-ready serverless solution that scans your AWS infrastructure to detect wasteful spending across multiple services. It provides actionable insights through an interactive dashboard, helping cloud engineers and FinOps teams optimize their AWS costs.

### Key Features

- **Multi-Service Scanning:** EBS volumes, EC2 instances, Elastic IPs, and Snapshots
- **Cost Calculation:** Accurate monthly and annual savings estimates
- **Interactive Dashboard:** Real-time visualization of cost optimization opportunities
- **Automated Scans:** Schedule daily or on-demand scans
- **Trend Analysis:** Track optimization progress over time
- **Detailed Reports:** Export findings to CSV for stakeholder reporting
- **Serverless Architecture:** Low-cost, scalable, and maintenance-free

### What It Detects

| Resource Type | Detection Criteria | Typical Monthly Savings |
|--------------|-------------------|------------------------|
| **Unattached EBS Volumes** | Volumes in "available" state | $8-125 per volume |
| **Idle EC2 Instances** | <5% CPU utilization over 7 days | $50-500 per instance |
| **Unattached Elastic IPs** | IPs without AssociationId | $3.60 per IP |
| **Old Snapshots** | Snapshots >180 days old | $0.05/GB-month |

## Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                    AWS Cost Optimizer                        │
└─────────────────────────────────────────────────────────────┘

  EventBridge               Master Scanner              DynamoDB
  (Scheduler)          ────▶  (Lambda)           ────▶  (Storage)
                              │
                 ┌────────────┼────────────┐
                 ▼            ▼            ▼
           EBS Scanner   EC2 Scanner   EIP Scanner
           (Lambda)      (Lambda)      (Lambda)

  API Gateway          API Lambda              React Dashboard
  (REST API)    ────▶  Functions      ◀────   (S3+CloudFront)
```

### Technology Stack

**Backend:**
- AWS Lambda (Python 3.9)
- Amazon DynamoDB
- API Gateway
- Amazon EventBridge
- CloudWatch Logs

**Frontend:**
- React 18
- Recharts (Data Visualization)
- Tailwind CSS
- Lucide React (Icons)
- S3 + CloudFront (Hosting)

**Infrastructure:**
- Terraform (IaC)
- PowerShell (Deployment Scripts)
- Git/GitHub (Version Control)

## Project Structure

```
aws-cost-optimizer/
├── README.md
├── .gitignore
├── lambda/
│   ├── scanners/
│   │   ├── ebs_scanner.py           # Unattached EBS volumes
│   │   ├── ec2_scanner.py           # Idle EC2 instances
│   │   ├── eip_scanner.py           # Unattached Elastic IPs
│   │   ├── snapshot_scanner.py      # Old snapshots
│   │   └── master_scanner.py        # Orchestrator
│   └── api/
│       ├── get_latest.py            # GET /api/latest
│       ├── get_scans.py             # GET /api/scans
│       ├── get_summary.py           # GET /api/summary
│       └── trigger_scan.py          # POST /api/scan
├── frontend/
│   ├── src/
│   │   ├── App.jsx                  # Main dashboard
│   │   ├── config.js                # API configuration
│   │   └── services/
│   │       └── api.js               # API service layer
│   ├── public/
│   │   └── index.html
│   └── package.json
├── scripts/
│   ├── deploy-scanners.ps1          # Deploy Lambda functions
│   ├── deploy-api.ps1               # Deploy API
│   ├── deploy-dashboard.ps1         # Deploy frontend
│   ├── setup-api-gateway.ps1        # Configure API Gateway
│   └── test-api.ps1                 # Test API endpoints
└── docs/
    ├── PRD.md                       # Product Requirements
    └── API_REFERENCE.md             # API Documentation
```

## Quick Start

### Prerequisites

- AWS Account with appropriate permissions
- AWS CLI configured (`aws configure`)
- Python 3.9+
- Node.js 18+
- PowerShell (Windows) or Bash (Mac/Linux)

### Installation (15 minutes)

#### 1. Clone Repository

```bash
git clone https://github.com/Kingflirckz22/Aws-cost-optimizer.git
cd aws-cost-optimizer
```

#### 2. Create IAM Role

```powershell
# Create trust policy
aws iam create-role `
  --role-name cost-optimizer-lambda-role `
  --assume-role-policy-document file://lambda-trust-policy.json

# Attach permissions
aws iam put-role-policy `
  --role-name cost-optimizer-lambda-role `
  --policy-name CostOptimizerPermissions `
  --policy-document file://lambda-permissions-policy.json
```

#### 3. Create DynamoDB Table

```powershell
aws dynamodb create-table `
  --table-name cost-optimizer-scans `
  --attribute-definitions AttributeName=scan_id,AttributeType=S `
  --key-schema AttributeName=scan_id,KeyType=HASH `
  --billing-mode PAY_PER_REQUEST
```

#### 4. Deploy Lambda Functions

```powershell
.\deploy-scanners.ps1
```

Deploys:
- `cost-optimizer-ebs-scanner`
- `cost-optimizer-ec2-scanner`
- `cost-optimizer-eip-scanner`
- `cost-optimizer-snapshot-scanner`
- `cost-optimizer-master`

#### 5. Deploy API

```powershell
.\deploy-api.ps1
.\setup-api-gateway.ps1
```

Creates REST API with endpoints:
- `GET /api/latest` - Most recent scan
- `GET /api/scans` - Scan history
- `GET /api/summary` - Statistics & insights
- `POST /api/scan` - Trigger new scan

#### 6. Deploy Dashboard

```powershell
# Update API URL in frontend/src/config.js first!
.\deploy-dashboard.ps1
```

## Usage

### Running a Scan

**Manual Trigger:**
```powershell
aws lambda invoke `
  --function-name cost-optimizer-master `
  output.json
```

**Via API:**
```powershell
curl -X POST https://YOUR-API-ID.execute-api.us-east-1.amazonaws.com/prod/api/scan
```

**Via Dashboard:**
Click "Run Scan" button

### Viewing Results

**API:**
```powershell
# Get latest scan
curl https://YOUR-API-ID.execute-api.us-east-1.amazonaws.com/prod/api/latest

# Get summary
curl https://YOUR-API-ID.execute-api.us-east-1.amazonaws.com/prod/api/summary
```

**Dashboard:**
Open `https://YOUR-CLOUDFRONT-URL` or `http://YOUR-BUCKET.s3-website-us-east-1.amazonaws.com`

### Scheduling Automated Scans

```powershell
# Create EventBridge rule for daily scans at 9 AM UTC
aws events put-rule `
  --name cost-optimizer-daily-scan `
  --schedule-expression "cron(0 9 * * ? *)"

# Add Lambda as target
aws events put-targets `
  --rule cost-optimizer-daily-scan `
  --targets "Id=1,Arn=arn:aws:lambda:us-east-1:YOUR-ACCOUNT-ID:function:cost-optimizer-master"

# Grant EventBridge permission to invoke Lambda
aws lambda add-permission `
  --function-name cost-optimizer-master `
  --statement-id AllowEventBridge `
  --action lambda:InvokeFunction `
  --principal events.amazonaws.com `
  --source-arn arn:aws:events:us-east-1:YOUR-ACCOUNT-ID:rule/cost-optimizer-daily-scan
```

## Dashboard Features

### Overview Page
- Summary cards showing total findings and potential savings
- Donut chart: Savings breakdown by service
- Line chart: Savings trend over last 14 scans
- Insights panel with actionable recommendations

### Findings Table
- Sortable columns (severity, service, cost)
- Filter by service type
- Search functionality
- Color-coded severity (RED/YELLOW/BLUE)
- Export to CSV

### Actions
- **Run Scan:** Trigger new optimization scan
- **Refresh:** Reload latest data
- **Export:** Download CSV report

##  Testing

### Test Individual Scanners

```powershell
# Test EBS scanner
aws lambda invoke --function-name cost-optimizer-ebs-scanner output-ebs.json
cat output-ebs.json

# Test EC2 scanner
aws lambda invoke --function-name cost-optimizer-ec2-scanner output-ec2.json
cat output-ec2.json
```

### Test API Endpoints

```powershell
.\test-api.ps1 -ApiUrl "https://YOUR-API-ID.execute-api.us-west-2.amazonaws.com/prod/api"
```

### Test Dashboard Locally

```powershell
cd frontend
npm start
# Opens http://localhost:3000
```

## Cost Analysis

### Monthly Operating Cost

| Service | Usage | Cost |
|---------|-------|------|
| Lambda (Scanners) | ~1,000 invocations/month | $0.20 |
| Lambda (API) | ~5,000 invocations/month | $0.10 |
| DynamoDB | 30 scans/month (on-demand) | $0.25 |
| API Gateway | ~5,000 requests/month | $0.10 |
| S3 (Dashboard) | 1GB storage + transfers | $0.10 |
| CloudFront (Optional) | 10GB transfer/month | $0.85 |
| **Total (with CloudFront)** | | **~$1.60/month** |
| **Total (S3 only)** | | **~$0.75/month** |

### ROI Example

If the tool identifies:
- 5 unattached EBS volumes (500GB total) = **$40/month**
- 2 idle t3.medium instances = **$60/month**
- 10 unattached Elastic IPs = **$36/month**

**Total Potential Savings:** $136/month ($1,632/year)  
**Tool Cost:** $1.60/month ($19.20/year)  
**ROI:** 8,400%

## Security

### IAM Permissions (Least Privilege)

Lambda functions use read-only permissions:
```json
{
  "Version": "2012-10-17",
  "Statement": [
    {
      "Effect": "Allow",
      "Action": [
        "ec2:Describe*",
        "cloudwatch:GetMetricStatistics"
      ],
      "Resource": "*"
    }
  ]
}
```

### Best Practices Implemented

- ✅ No hardcoded credentials
- ✅ HTTPS-only API endpoints
- ✅ CORS properly configured
- ✅ DynamoDB encryption at rest
- ✅ CloudWatch logging enabled
- ✅ Least-privilege IAM roles
- ✅ Input validation on API

##  Roadmap

### v1.1 (Planned)
- [ ] RDS instance optimization
- [ ] Load Balancer idle detection
- [ ] SNS email notifications
- [ ] Slack/Teams integration

### v1.2 (Future)
- [ ] S3 storage class recommendations
- [ ] Lambda function cost analysis
- [ ] Multi-account support (AWS Organizations)
- [ ] Custom threshold configuration

### v2.0 (Vision)
- [ ] Automated remediation
- [ ] Cost forecasting
- [ ] Reserved Instance recommendations
- [ ] Savings Plans analysis
- [ ] AI-powered insights

## Contributing

This is a portfolio project, but contributions are welcome!

1. Fork the repository
2. Create your feature branch (`git checkout -b feature/AmazingFeature`)
3. Commit your changes (`git commit -m 'Add some AmazingFeature'`)
4. Push to the branch (`git push origin feature/AmazingFeature`)
5. Open a Pull Request

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## Acknowledgments

- AWS Documentation and best practices
- React and Recharts communities
- Cloud cost optimization resources

## Contact

[LinkedIn](https://www.linkedin.com/in/anjorin-olayemi-enitan-0121ab210/)
[Email](Kingflirckz22@gmail.com)

**Project Link:** [(https://github.com/Kingflirckz22/Aws-cost-optimizer.git)]


---

*Star this repository if you find it helpful!*