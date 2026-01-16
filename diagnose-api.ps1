# Diagnose API Gateway Issues

$API_ID = "6ht92lu3ib"

Write-Host "Diagnosing API Gateway Setup..." -ForegroundColor Cyan
Write-Host ""

# Check if API exists
Write-Host "1. Checking API exists..." -ForegroundColor Yellow
$api = aws apigateway get-rest-api --rest-api-id $API_ID 2>&1
if ($LASTEXITCODE -eq 0) {
    Write-Host "   [OK] API exists" -ForegroundColor Green
} else {
    Write-Host "   [FAIL] API not found" -ForegroundColor Red
    exit
}

# Get all resources
Write-Host "2. Checking resources..." -ForegroundColor Yellow
$resources = aws apigateway get-resources --rest-api-id $API_ID | ConvertFrom-Json
Write-Host "   Found $($resources.items.Count) resources:" -ForegroundColor Green
foreach ($resource in $resources.items) {
    Write-Host "      - $($resource.path)" -ForegroundColor Gray
    if ($resource.resourceMethods) {
        $methods = $resource.resourceMethods | Get-Member -MemberType NoteProperty | Select-Object -ExpandProperty Name
        Write-Host "        Methods: $($methods -join ', ')" -ForegroundColor Gray
    }
}

Write-Host ""
Write-Host "3. Expected resources:" -ForegroundColor Yellow
Write-Host "   - /" -ForegroundColor Gray
Write-Host "   - /api" -ForegroundColor Gray
Write-Host "   - /api/latest (GET)" -ForegroundColor Gray
Write-Host "   - /api/scans (GET)" -ForegroundColor Gray
Write-Host "   - /api/summary (GET)" -ForegroundColor Gray
Write-Host "   - /api/scan (POST)" -ForegroundColor Gray

Write-Host ""
Write-Host "4. Checking deployments..." -ForegroundColor Yellow
$deployments = aws apigateway get-deployments --rest-api-id $API_ID | ConvertFrom-Json
if ($deployments.items.Count -gt 0) {
    Write-Host "   [OK] Found $($deployments.items.Count) deployment(s)" -ForegroundColor Green
    Write-Host "   Latest deployment: $($deployments.items[0].id)" -ForegroundColor Gray
} else {
    Write-Host "   [FAIL] No deployments found - you need to deploy the API!" -ForegroundColor Red
}

Write-Host ""
Write-Host "5. Correct API URL should be:" -ForegroundColor Yellow
Write-Host "   https://$API_ID.execute-api.us-east-1.amazonaws.com/prod/api/latest" -ForegroundColor Cyan
Write-Host "   https://$API_ID.execute-api.us-east-1.amazonaws.com/prod/api/scans" -ForegroundColor Cyan
Write-Host "   https://$API_ID.execute-api.us-east-1.amazonaws.com/prod/api/summary" -ForegroundColor Cyan
Write-Host "   https://$API_ID.execute-api.us-east-1.amazonaws.com/prod/api/scan" -ForegroundColor Cyan

Write-Host ""
Write-Host "6. Quick test..." -ForegroundColor Yellow
Write-Host "   Testing: /api/latest" -ForegroundColor Gray
try {
    $response = Invoke-RestMethod -Uri "https://$API_ID.execute-api.us-east-1.amazonaws.com/prod/api/latest" -Method GET
    Write-Host "   [OK] API is working!" -ForegroundColor Green
} catch {
    Write-Host "   [ERROR] Error: $($_.Exception.Message)" -ForegroundColor Red
    Write-Host ""
    Write-Host "Common issues:" -ForegroundColor Yellow
    Write-Host "   1. API Gateway doesn't have Lambda invoke permissions" -ForegroundColor White
    Write-Host "   2. Resources not properly created" -ForegroundColor White
    Write-Host "   3. Integration not set up correctly" -ForegroundColor White
    Write-Host "   4. API not deployed to prod stage" -ForegroundColor White
}