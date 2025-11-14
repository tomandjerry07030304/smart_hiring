# MongoDB Installation Helper for Windows
Write-Host "Checking MongoDB Installation..." -ForegroundColor Cyan

# Check if MongoDB is already installed
$mongoPath = "C:\Program Files\MongoDB\Server"
if (Test-Path $mongoPath) {
    Write-Host "MongoDB found at: $mongoPath" -ForegroundColor Green
    
    # Find mongod.exe
    $mongodExe = Get-ChildItem -Path $mongoPath -Recurse -Filter "mongod.exe" -ErrorAction SilentlyContinue | Select-Object -First 1
    
    if ($mongodExe) {
        Write-Host "mongod.exe found at: $($mongodExe.FullName)" -ForegroundColor Green
        
        # Create data directory
        $dataPath = "C:\data\db"
        if (-not (Test-Path $dataPath)) {
            Write-Host "Creating data directory: $dataPath" -ForegroundColor Yellow
            New-Item -ItemType Directory -Path $dataPath -Force | Out-Null
            Write-Host "Data directory created!" -ForegroundColor Green
        }
        
        Write-Host ""
        Write-Host "Starting MongoDB server..." -ForegroundColor Cyan
        Write-Host "Keep this window open while using the app!" -ForegroundColor Yellow
        Write-Host "Press Ctrl+C to stop MongoDB when done." -ForegroundColor Yellow
        Write-Host ""
        
        # Start MongoDB
        & $mongodExe.FullName --dbpath $dataPath
        
    } else {
        Write-Host "ERROR: mongod.exe not found in MongoDB installation" -ForegroundColor Red
    }
    
} else {
    Write-Host "ERROR: MongoDB NOT installed at $mongoPath" -ForegroundColor Red
    Write-Host ""
    Write-Host "Download MongoDB Community Edition from:" -ForegroundColor Yellow
    Write-Host "https://www.mongodb.com/try/download/community" -ForegroundColor Cyan
}
