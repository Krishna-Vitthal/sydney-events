# Sydney Events Application - PowerShell Startup Script
# This script starts both the backend (FastAPI) and frontend (React) servers

param(
    [switch]$SetupOnly,
    [switch]$BackendOnly,
    [switch]$FrontendOnly
)

$ErrorActionPreference = "Stop"
$ProjectRoot = $PSScriptRoot

Write-Host ""
Write-Host "========================================" -ForegroundColor Cyan
Write-Host "   Sydney Events Application Launcher  " -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""

# Function to check if a command exists
function Test-Command($command) {
    try {
        if (Get-Command $command -ErrorAction Stop) {
            return $true
        }
    } catch {
        return $false
    }
}

# Function to setup Python virtual environment
function Setup-Backend {
    Write-Host "[Backend] Setting up Python environment..." -ForegroundColor Yellow
    
    $backendPath = Join-Path $ProjectRoot "backend"
    $venvPath = Join-Path $backendPath "venv"
    
    Push-Location $backendPath
    
    # Create virtual environment if it doesn't exist
    if (-not (Test-Path $venvPath)) {
        Write-Host "[Backend] Creating virtual environment..." -ForegroundColor Gray
        python -m venv venv
    }
    
    # Activate and install dependencies
    $activateScript = Join-Path $venvPath "Scripts\Activate.ps1"
    . $activateScript
    
    Write-Host "[Backend] Installing dependencies..." -ForegroundColor Gray
    pip install -r requirements.txt --quiet
    
    # Create .env from example if it doesn't exist
    $envFile = Join-Path $backendPath ".env"
    $envExample = Join-Path $backendPath ".env.example"
    if (-not (Test-Path $envFile) -and (Test-Path $envExample)) {
        Copy-Item $envExample $envFile
        Write-Host "[Backend] Created .env file - Please configure your Google OAuth credentials!" -ForegroundColor Magenta
    }
    
    Pop-Location
    Write-Host "[Backend] Setup complete!" -ForegroundColor Green
}

# Function to setup frontend
function Setup-Frontend {
    Write-Host "[Frontend] Setting up Node.js environment..." -ForegroundColor Yellow
    
    $frontendPath = Join-Path $ProjectRoot "frontend"
    $nodeModulesPath = Join-Path $frontendPath "node_modules"
    
    Push-Location $frontendPath
    
    # Install dependencies if node_modules doesn't exist
    if (-not (Test-Path $nodeModulesPath)) {
        Write-Host "[Frontend] Installing dependencies..." -ForegroundColor Gray
        npm install
    }
    
    Pop-Location
    Write-Host "[Frontend] Setup complete!" -ForegroundColor Green
}

# Function to start backend server
function Start-Backend {
    Write-Host "[Backend] Starting FastAPI server..." -ForegroundColor Yellow
    
    $backendPath = Join-Path $ProjectRoot "backend"
    $venvPython = Join-Path $backendPath "venv\Scripts\python.exe"
    
    $job = Start-Job -ScriptBlock {
        param($path, $python)
        Set-Location $path
        & $python -m uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
    } -ArgumentList $backendPath, $venvPython
    
    return $job
}

# Function to start frontend server
function Start-Frontend {
    Write-Host "[Frontend] Starting Vite dev server..." -ForegroundColor Yellow
    
    $frontendPath = Join-Path $ProjectRoot "frontend"
    
    $job = Start-Job -ScriptBlock {
        param($path)
        Set-Location $path
        npm run dev
    } -ArgumentList $frontendPath
    
    return $job
}

# Check prerequisites
Write-Host "Checking prerequisites..." -ForegroundColor Gray

if (-not (Test-Command "python")) {
    Write-Host "ERROR: Python is not installed or not in PATH" -ForegroundColor Red
    exit 1
}

if (-not (Test-Command "node")) {
    Write-Host "ERROR: Node.js is not installed or not in PATH" -ForegroundColor Red
    exit 1
}

if (-not (Test-Command "npm")) {
    Write-Host "ERROR: npm is not installed or not in PATH" -ForegroundColor Red
    exit 1
}

Write-Host "All prerequisites met!" -ForegroundColor Green
Write-Host ""

# Setup
Setup-Backend
Setup-Frontend

if ($SetupOnly) {
    Write-Host ""
    Write-Host "Setup complete! Run this script again without -SetupOnly to start the servers." -ForegroundColor Cyan
    exit 0
}

Write-Host ""
Write-Host "Starting servers..." -ForegroundColor Cyan
Write-Host ""

# Start servers based on parameters
$backendJob = $null
$frontendJob = $null

if (-not $FrontendOnly) {
    # Start backend in a new PowerShell window
    $backendPath = Join-Path $ProjectRoot "backend"
    Start-Process powershell -ArgumentList "-NoExit", "-Command", "cd '$backendPath'; .\venv\Scripts\Activate.ps1; python -m uvicorn app.main:app --reload --host 0.0.0.0 --port 8000"
    Write-Host "[Backend] Started on http://localhost:8000" -ForegroundColor Green
    Write-Host "[Backend] API docs available at http://localhost:8000/docs" -ForegroundColor Gray
}

if (-not $BackendOnly) {
    # Give backend a moment to start
    Start-Sleep -Seconds 2
    
    # Start frontend in a new PowerShell window
    $frontendPath = Join-Path $ProjectRoot "frontend"
    Start-Process powershell -ArgumentList "-NoExit", "-Command", "cd '$frontendPath'; npm run dev"
    Write-Host "[Frontend] Started on http://localhost:5173" -ForegroundColor Green
}

Write-Host ""
Write-Host "========================================" -ForegroundColor Cyan
Write-Host "   Application is running!            " -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""
Write-Host "Frontend: http://localhost:5173" -ForegroundColor White
Write-Host "Backend:  http://localhost:8000" -ForegroundColor White
Write-Host "API Docs: http://localhost:8000/docs" -ForegroundColor White
Write-Host ""
Write-Host "IMPORTANT: Configure Google OAuth credentials in backend/.env" -ForegroundColor Yellow
Write-Host ""
Write-Host "Press any key to exit this launcher (servers will keep running)..." -ForegroundColor Gray
$null = $Host.UI.RawUI.ReadKey("NoEcho,IncludeKeyDown")
