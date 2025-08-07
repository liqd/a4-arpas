Write-Host "Updating arpas-arc package..." -ForegroundColor Green

# Save current directory
$originalDir = Get-Location

try {
    # Navigate to arpas-arc and build
    Write-Host "Building arpas-arc..." -ForegroundColor Yellow
    Set-Location "..\arpas-arc"
    npm run build
    
    if ($LASTEXITCODE -ne 0) {  
        throw "arpas-arc build failed"
    }
    
    # Navigate back to arpas directory
    Set-Location $originalDir
    
    # Force reinstall the local package
    Write-Host "Reinstalling arpas-arc package..." -ForegroundColor Yellow
    npm install arpas-arc@file:../arpas-arc --force
    
    if ($LASTEXITCODE -ne 0) {
        throw "npm install failed"
    }
    
    Write-Host "arpas-arc package updated successfully!" -ForegroundColor Green
}
catch {
    Write-Host "Error updating arpas-arc: $_" -ForegroundColor Red
    Set-Location $originalDir
    exit 1
}
finally {
    # Ensure we return to original directory
    Set-Location $originalDir
}
