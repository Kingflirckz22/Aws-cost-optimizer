# Quick Fix - Deploy simplified API functions

Write-Host "Deploying simplified API functions..." -ForegroundColor Cyan
Write-Host ""

$REGION = "us-east-1"

# Navigate to api folder
cd lambda\api

Write-Host "Step 1: Creating deployment packages..." -ForegroundColor Yellow
Write-Host ""

# Package each function individually (no utils needed)
$functions = @(
    @{Name="get-latest"; File="get_latest.py"; LambdaName="cost-optimizer-api-get-latest"},
    @{Name="get-scans"; File="get_scans.py"; LambdaName="cost-optimizer-api-get-scans"},
    @{Name="get-summary"; File="get_summary.py"; LambdaName="cost-optimizer-api-get-summary"},
    @{Name="trigger-scan"; File="trigger_scan.py"; LambdaName="cost-optimizer-api-trigger-scan"}
)

foreach ($func in $functions) {
    Write-Host "  Packaging $($func.File)..." -ForegroundColor Gray
    
    # Create zip with just the single Python file
    if (Test-Path "$($func.Name).zip") {
        Remove-Item "$($func.Name).zip"
    }
    Compress-Archive -Path $func.File -DestinationPath "$($func.Name).zip" -Force
    
    Write-Host "    [OK] Created $($func.Name).zip" -ForegroundColor Green
}

Write-Host ""
Write-Host "Step 2: Updating Lambda functions..." -ForegroundColor Yellow
Write-Host ""

foreach ($func in $functions) {
    Write-Host "  Updating $($func.LambdaName)..." -ForegroundColor Gray
    
    aws lambda update-function-code `
        --function-name $func.LambdaName `
        --zip-file "fileb://$($func.Name).zip" `
        --region $REGION | Out-Null
    
    if ($LASTEXITCODE -eq 0) {
        Write-Host "    [OK] Updated successfully" -ForegroundColor Green
    }
    else {
        Write-Host "    [ERROR] Update failed" -ForegroundColor Red
    }
}

# Go back to project root
cd ..\..

Write-Host ""
Write-Host "Step 3: Waiting for functions to be ready..." -ForegroundColor Yellow
Start-Sleep -Seconds 10
Write-Host "  [OK] Ready" -ForegroundColor Green

Write-Host ""
Write-Host "================================" -ForegroundColor Green
Write-Host "API Functions Updated!" -ForegroundColor Green
Write-Host "================================" -ForegroundColor Green
Write-Host ""

# Test immediately
Write-Host "Testing API..." -ForegroundColor Yellow
Write-Host ""

try {
    $response = Invoke-RestMethod -Uri "https://6ht92lu3ib.execute-api.us-east-1.amazonaws.com/prod/api/latest" -Method GET
    
    if ($response.success) {
        Write-Host "[OK] API is working!" -ForegroundColor Green
        Write-Host ""
        
        if ($response.data.scan) {
            Write-Host "Latest scan found:" -ForegroundColor Cyan
            Write-Host "  Scan ID: $($response.data.scan_id)" -ForegroundColor Gray
            Write-Host "  Findings: $($response.data.summary.total_findings)" -ForegroundColor Gray
            Write-Host "  Monthly Savings: `$$($response.data.summary.monthly_savings_usd)" -ForegroundColor Gray
        }
        else {
            Write-Host "No scans found in database yet." -ForegroundColor Gray
            Write-Host "Run a scan first:" -ForegroundColor Yellow
            Write-Host "  aws lambda invoke --function-name cost-optimizer-master output.json" -ForegroundColor Cyan
        }
    }
    else {
        Write-Host "[WARNING] API returned error: $($response.error)" -ForegroundColor Yellow
    }
}
catch {
    Write-Host "[ERROR] Error: $($_.Exception.Message)" -ForegroundColor Red
    Write-Host ""
    Write-Host "Check CloudWatch logs:" -ForegroundColor Yellow
    Write-Host "  aws logs tail /aws/lambda/cost-optimizer-api-get-latest --follow" -ForegroundColor Cyan
}

Write-Host ""
Write-Host "Run full API test:" -ForegroundColor Yellow
Write-Host "  .\test-api.ps1 -ApiUrl 'https://6ht92lu3ib.execute-api.us-east-1.amazonaws.com/prod/api'" -ForegroundColor Cyan