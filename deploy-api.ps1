# Deploy Cost Optimizer API
# Run this from the project root directory

Write-Host "================================" -ForegroundColor Cyan
Write-Host "Deploying Cost Optimizer API" -ForegroundColor Cyan
Write-Host "================================" -ForegroundColor Cyan
Write-Host ""

$ACCOUNT_ID = (aws sts get-caller-identity --query Account --output text)
$ROLE_ARN = "arn:aws:iam::${ACCOUNT_ID}:role/cost-optimizer-lambda-role"
$REGION = "us-east-1"

# API endpoints to deploy
$endpoints = @(
    @{Name="get-latest"; File="get_latest.py"; Handler="get_latest.lambda_handler"; Description="Get latest scan results"},
    @{Name="get-scans"; File="get_scans.py"; Handler="get_scans.lambda_handler"; Description="Get scan history"},
    @{Name="get-summary"; File="get_summary.py"; Handler="get_summary.lambda_handler"; Description="Get summary statistics"},
    @{Name="trigger-scan"; File="trigger_scan.py"; Handler="trigger_scan.lambda_handler"; Description="Trigger new scan"}
)

# Create deployment packages
Write-Host "Creating deployment packages..." -ForegroundColor Yellow
Set-Location lambda

foreach ($endpoint in $endpoints) {
    Write-Host "  Packaging $($endpoint.Name)..." -ForegroundColor Gray
    
    # Create temp directory
    $tempDir = "temp_$($endpoint.Name)"
    New-Item -ItemType Directory -Force -Path $tempDir | Out-Null
    
    # Copy API file and utils
    Copy-Item "api\$($endpoint.File)" -Destination "$tempDir\"
    Copy-Item -Recurse "utils" -Destination "$tempDir\"
    
    # Create zip
    Set-Location $tempDir
    Compress-Archive -Path * -DestinationPath "..\api-$($endpoint.Name).zip" -Force
    Set-Location ..
    
    # Cleanup temp directory
    Remove-Item -Recurse -Force $tempDir
}

Set-Location ..

Write-Host "[OK] Packages created" -ForegroundColor Green
Write-Host ""

# Deploy each API endpoint
foreach ($endpoint in $endpoints) {
    $functionName = "cost-optimizer-api-$($endpoint.Name)"
    
    Write-Host "Deploying: $functionName" -ForegroundColor Cyan
    
    # Check if function exists
    $ErrorActionPreference = 'SilentlyContinue'
    $exists = aws lambda get-function --function-name $functionName --region $REGION 2>$null
    $functionExists = $LASTEXITCODE -eq 0
    $ErrorActionPreference = 'Continue'
    
    $zipFile = "fileb://lambda/api-" + $endpoint.Name + ".zip"
    $handler = $endpoint.Handler
    $description = $endpoint.Description
    
    if ($functionExists) {
        # Update existing function
        Write-Host "  Updating..." -ForegroundColor Yellow
        aws lambda update-function-code --function-name $functionName --zip-file $zipFile --region $REGION | Out-Null
        Write-Host "  [OK] Updated" -ForegroundColor Green
    }
    
    if (-not $functionExists) {
        # Create new function
        Write-Host "  Creating..." -ForegroundColor Yellow
        aws lambda create-function --function-name $functionName --runtime python3.9 --role $ROLE_ARN --handler $handler --zip-file $zipFile --timeout 30 --memory-size 256 --description $description --region $REGION | Out-Null
        Write-Host "  [OK] Created" -ForegroundColor Green
    }
}

Write-Host ""
Write-Host "================================" -ForegroundColor Green
Write-Host "API Deployment Complete!" -ForegroundColor Green
Write-Host "================================" -ForegroundColor Green
Write-Host ""

Write-Host "Deployed API Functions:" -ForegroundColor Yellow
foreach ($endpoint in $endpoints) {
    Write-Host "  • cost-optimizer-api-$($endpoint.Name)" -ForegroundColor White
}

Write-Host ""
Write-Host "Next Steps:" -ForegroundColor Yellow
Write-Host "1. Create API Gateway to expose these endpoints" -ForegroundColor White
Write-Host "2. Test the API endpoints" -ForegroundColor White
Write-Host "3. Build the React dashboard" -ForegroundColor White
Write-Host ""

# Test one endpoint
Write-Host "Testing get-latest endpoint..." -ForegroundColor Cyan
aws lambda invoke --function-name cost-optimizer-api-get-latest --region $REGION api-test-output.json

Write-Host ""
if (Test-Path api-test-output.json) {
    $result = Get-Content api-test-output.json | ConvertFrom-Json
    if ($result.statusCode -eq 200) {
        Write-Host "[OK] API is working!" -ForegroundColor Green
        $body = $result.body | ConvertFrom-Json
        if ($body.success) {
            Write-Host "  Found scan data" -ForegroundColor Gray
        }
    }
    
    if ($result.statusCode -ne 200) {
        Write-Host "[WARNING] API returned error" -ForegroundColor Yellow
    }
}