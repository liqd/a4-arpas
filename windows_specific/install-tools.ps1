Write-Host "`nChecking for required DLLs to determine if installation is needed..." -ForegroundColor Cyan

# Check if local.py exists and read DLL paths
$localConfigPath = "adhocracy-plus/config/settings/local.py"
$requiredDlls = @()
$missingDlls = @()

if (Test-Path $localConfigPath) {
    Write-Host "`nReading DLL paths from $localConfigPath..." -ForegroundColor Yellow
    $content = Get-Content $localConfigPath
    foreach ($line in $content) {
        if ($line -match '^(SPATIALITE_LIBRARY_PATH|GDAL_LIBRARY_PATH|GEOS_LIBRARY_PATH)\s*=\s*r?"([^"]*)"') {
            $dllName = $matches[1]
            $dllPath = $matches[2]
            $requiredDlls += @{ Name = $dllName; Path = $dllPath }
            
            if (Test-Path $dllPath) {
                # Write-Host "$dllName found at $dllPath" -ForegroundColor Green
            } else {
                Write-Host "$dllName not found at $dllPath" -ForegroundColor Red
                $missingDlls += $dllName
            }
        }
    }
} else {
    Write-Host "No local.py found. Using default DLL locations to check..." -ForegroundColor Yellow
    $defaultPaths = @{
        "SPATIALITE_LIBRARY_PATH" = "C:/OSGeo4W/bin/mod_spatialite.dll"
        "GDAL_LIBRARY_PATH" = "C:/OSGeo4W/bin/gdal311.dll"
        "GEOS_LIBRARY_PATH" = "C:/OSGeo4W/bin/geos_c.dll"
    }
    
    foreach ($dll in $defaultPaths.Keys) {
        $path = $defaultPaths[$dll]
        $requiredDlls += @{ Name = $dll; Path = $path }
        
        if (Test-Path $path) {
            # Write-Host "$dll found at $path" -ForegroundColor Green
        } else {
            Write-Host "$dll not found at $path" -ForegroundColor Red
            $missingDlls += $dll
        }
    }
}

if ($missingDlls.Count -eq 0) {
    Write-Host "`nAll required DLLs are already available. No installation needed." -ForegroundColor Green
    exit 0
}

Write-Host "`nMissing DLLs: $($missingDlls -join ', ')" -ForegroundColor Red
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
        Write-Host "Install the following packages: gdal, geos" -ForegroundColor Yellow
        exit 1
    }
}

# Launch installer
if (Test-Path $setupExe) {
    Write-Host "Launching OSGeo4W installer..." -ForegroundColor Green
    Start-Process $setupExe -ArgumentList '/install', '/quiet', '/packages:gdal,geos' -Verb RunAs
}
else {
    Write-Host "osgeo4w-setup.exe not found." -ForegroundColor Red
    Write-Host "You can download it from https://download.osgeo.org/osgeo4w/osgeo4w-setup.exe" -ForegroundColor Yellow
    exit 1
}
