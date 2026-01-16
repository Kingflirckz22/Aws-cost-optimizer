# Deploy All Cost Optimizer Scanners
# Run this script from the project root directory

Write-Host "================================" -ForegroundColor Cyan
Write-Host "AWS Cost Optimizer Deployment" -ForegroundColor Cyan
Write-Host "================================" -ForegroundColor Cyan
Write-Host ""

# Configuration
$REGION = "us-east-1"
$ROLE_NAME = "cost-optimizer-lambda-role"

# Get AWS Account ID
Write-Host "Getting AWS Account ID..." -ForegroundColor Yellow
$ACCOUNT_ID = (aws sts get-caller-identity --query Account --output text)
$ROLE_ARN = "arn:aws:iam::${ACCOUNT_ID}:role/${ROLE_NAME}"

Write-Host "Account ID: $ACCOUNT_ID" -ForegroundColor Green
Write-Host "Role ARN: $ROLE_ARN" -ForegroundColor Green
Write-Host ""

# Array of scanners to deploy
$scanners = @(
    @{Name="ebs-scanner"; File="ebs_scanner.py"; Handler="ebs_scanner.lambda_handler"; Description="Scans for unattached EBS volumes"},
    @{Name="ec2-scanner"; File="ec2_scanner.py"; Handler="ec2_scanner.lambda_handler"; Description="Scans for idle EC2 instances"},
    @{Name="eip-scanner"; File="eip_scanner.py"; Handler="eip_scanner.lambda_handler"; Description="Scans for unattached Elastic IPs"},
    @{Name="snapshot-scanner"; File="snapshot_scanner.py"; Handler="snapshot_scanner.lambda_handler"; Description="Scans for old EBS snapshots"}
)

# Deploy each scanner
foreach ($scanner in $scanners) {
    $functionName = "cost-optimizer-$($scanner.Name)"
    
    Write-Host "Deploying: $functionName" -ForegroundColor Cyan
    
    # Create deployment package
    Write-Host "  Creating package..." -ForegroundColor Yellow
    cd lambda\scanners
    Compress-Archive -Path $scanner.File -DestinationPath "$($scanner.Name).zip" -Force
    cd ..\..
    
    # Check if function exists
    $functionExists = aws lambda get-function --function-name $functionName 2>$null
    
    if ($functionExists) {
        # Update existing function
        Write-Host "  Updating existing function..." -ForegroundColor Yellow
        aws lambda update-function-code `
            --function-name $functionName `
            --zip-file "fileb://lambda/scanners/$($scanner.Name).zip" `
            --region $REGION
        
        Write-Host "  ✓ Function updated" -ForegroundColor Green
    } else {
        # Create new function
        Write-Host "  Creating new function..." -ForegroundColor Yellow
        aws lambda create-function `
            --function-name $functionName `
            --runtime python3.9 `
            --role $ROLE_ARN `
            --handler $scanner.Handler `
            --zip-file "fileb://lambda/scanners/$($scanner.Name).zip" `
            --timeout 60 `
            --memory-size 256 `
            --description $scanner.Description `
            --region $REGION
        
        Write-Host "  ✓ Function created" -ForegroundColor Green
    }
    
    Write-Host ""
}

# Deploy master orchestrator
Write-Host "Deploying: Master Orchestrator" -ForegroundColor Cyan

# Create master orchestrator package with all scanners
Write-Host "  Creating master package..." -ForegroundColor Yellow
cd lambda
Compress-Archive -Path scanners\*.py -DestinationPath master-scanner.zip -Force
cd ..

$masterFunctionName = "cost-optimizer-master"
$masterExists = aws lambda get-function --function-name $masterFunctionName 2>$null

if ($masterExists) {
    Write-Host "  Updating master function..." -ForegroundColor Yellow
    aws lambda update-function-code `
        --function-name $masterFunctionName `
        --zip-file "fileb://lambda/master-scanner.zip" `
        --region $REGION
    Write-Host "  ✓ Master function updated" -ForegroundColor Green
} else {
    Write-Host "  Creating master function..." -ForegroundColor Yellow
    aws lambda create-function `
        --function-name $masterFunctionName `
        --runtime python3.9 `
        --role $ROLE_ARN `
        --handler master_scanner.lambda_handler `
        --zip-file "fileb://lambda/master-scanner.zip" `
        --timeout 300 `
        --memory-size 512 `
        --description "Master orchestrator that runs all cost optimization scans" `
        --region $REGION
    Write-Host "  ✓ Master function created" -ForegroundColor Green
}

Write-Host ""
Write-Host "================================" -ForegroundColor Cyan
Write-Host "Deployment Complete!" -ForegroundColor Green
Write-Host "================================" -ForegroundColor Cyan
Write-Host ""
Write-Host "Deployed Functions:" -ForegroundColor Yellow
foreach ($scanner in $scanners) {
    Write-Host "  • cost-optimizer-$($scanner.Name)" -ForegroundColor White
}
Write-Host "  • cost-optimizer-master (orchestrator)" -ForegroundColor White
Write-Host ""

# Test the master function
Write-Host "Would you like to test the master scanner now? (Y/N): " -ForegroundColor Yellow -NoNewline
$response = Read-Host

if ($response -eq "Y" -or $response -eq "y") {
    Write-Host ""
    Write-Host "Testing master scanner..." -ForegroundColor Cyan
    aws lambda invoke `
        --function-name cost-optimizer-master `
        --log-type Tail `
        --region $REGION `
        output.json
    
    Write-Host ""
    Write-Host "Results saved to output.json" -ForegroundColor Green
    Write-Host ""
    Get-Content output.json | ConvertFrom-Json | ConvertTo-Json -Depth 10
}

Write-Host ""
Write-Host "Next Steps:" -ForegroundColor Yellow
Write-Host "1. Set up EventBridge rule for scheduled scans" -ForegroundColor White
Write-Host "2. Build REST API for dashboard access" -ForegroundColor White
Write-Host "3. Create React dashboard for visualization" -ForegroundColor White