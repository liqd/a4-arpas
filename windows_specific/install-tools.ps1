Write-Host "Setting up Spatialite, GDAL and OSGeo4W components..." -ForegroundColor Cyan

# Default paths
$defaultDownloadPath = "$env:USERPROFILE\Downloads\osgeo4w-setup.exe"
$defaultSetupExe = $defaultDownloadPath

# Prompt user for installer location
$inputPath = Read-Host "Path to osgeo4w-setup.exe (default: $defaultSetupExe)"
$setupExe = if ([string]::IsNullOrWhiteSpace($inputPath)) { $defaultSetupExe } else { $inputPath }

# Adjust fallback
if (!(Test-Path $setupExe)) {
    if (!(Test-Path $setupExe) -and (Test-Path $defaultDownloadPath)) {
        Write-Host "Using installer from Downloads folder instead..." -ForegroundColor Yellow
        $setupExe = $defaultDownloadPath
    } else {
        Write-Host "osgeo4w-setup.exe not found in $defaultSetupExe nor $defaultDownloadPath location." -ForegroundColor Red
        Write-Host "Download it from https://download.osgeo.org/osgeo4w/osgeo4w-setup.exe" -ForegroundColor Yellow
        exit 1
    }
}

# Launch installer
if (Test-Path $setupExe) {
    Write-Host "Launching OSGeo4W installer..." -ForegroundColor Green
    Start-Process $setupExe -ArgumentList '/install', '/quiet', '/packages:gdal,gdal-python,spatialite-tools' -Verb RunAs
}
else {
    Write-Host "osgeo4w-setup.exe not found." -ForegroundColor Red
    Write-Host "You can download it from https://download.osgeo.org/osgeo4w/osgeo4w-setup.exe" -ForegroundColor Yellow
    exit 1
}
