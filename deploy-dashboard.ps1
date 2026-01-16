# Quick Update Dashboard Script
# Updates the UI files and restarts the dev server

Write-Host "🎨 Updating Dashboard UI..." -ForegroundColor Cyan
Write-Host ""

# Check if we're in the right directory
if (!(Test-Path "frontend")) {
    Write-Host "❌ Error: frontend folder not found" -ForegroundColor Red
    Write-Host "Please run this script from the project root" -ForegroundColor Yellow
    exit 1
}

# Check if node_modules exists
if (!(Test-Path "frontend/node_modules")) {
    Write-Host "📦 Installing dependencies..." -ForegroundColor Yellow
    cd frontend
    npm install
    cd ..
    Write-Host "✅ Dependencies installed" -ForegroundColor Green
    Write-Host ""
}

# Check if dev server is running
$processRunning = Get-Process -Name "node" -ErrorAction SilentlyContinue | Where-Object { $_.MainWindowTitle -like "*localhost:3000*" }

if ($processRunning) {
    Write-Host "🔄 Stopping existing dev server..." -ForegroundColor Yellow
    Stop-Process -Name "node" -Force -ErrorAction SilentlyContinue
    Start-Sleep -Seconds 2
    Write-Host "✅ Server stopped" -ForegroundColor Green
    Write-Host ""
}

# Start dev server
Write-Host "🚀 Starting development server..." -ForegroundColor Green
Write-Host ""
Write-Host "Dashboard will open at: http://localhost:3000" -ForegroundColor Cyan
Write-Host "Press Ctrl+C to stop the server" -ForegroundColor Gray
Write-Host ""

cd frontend
npm start