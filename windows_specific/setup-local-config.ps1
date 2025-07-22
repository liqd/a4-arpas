$template = "adhocracy-plus/config/settings/local.py.template"
$output = "adhocracy-plus/config/settings/local.py"

# ========================
# DLL Configuration
# ========================

# Default DLL paths
$dllDefaults = @{
    SPATIALITE_LIBRARY_PATH = "C:/OSGeo4W/bin/mod_spatialite.dll"
    GDAL_LIBRARY_PATH       = "C:/OSGeo4W/bin/gdal311.dll"
    GEOS_LIBRARY_PATH       = "C:/OSGeo4W/bin/geos_c.dll"
}

Write-Host "`nSetting up local configuration for required DLLs..." -ForegroundColor Cyan

# Prompt user with inline defaults
$dllPaths = @{}
foreach ($key in $dllDefaults.Keys) {
    $defaultValue = $dllDefaults[$key]
    $input = Read-Host "$key (default: $defaultValue)"
    $dllPaths[$key] = if ([string]::IsNullOrWhiteSpace($input)) { $defaultValue } else { $input }
}

# Check DLL existence
$missing = @()
foreach ($key in $dllPaths.Keys) {
    if (Test-Path $dllPaths[$key]) {
        Write-Host "$key found at $($dllPaths[$key])" -ForegroundColor Green
    } else {
        Write-Host "$key not found at $($dllPaths[$key])" -ForegroundColor Red
        $missing += $key
    }
}

# ========================
# Database Configuration
# ========================

$dbDefaults = @{
    NAME     = "arpas-db"
    USER     = "postgres"
    PASSWORD = "postgres"
    HOST     = "localhost"
    PORT     = "5556"
}

Write-Host "`nSetting up local PostgreSQL database configuration..." -ForegroundColor Cyan

$dbConfig = @{}
foreach ($key in $dbDefaults.Keys) {
    $defaultValue = $dbDefaults[$key]
    $input = Read-Host "DB $key (default: $defaultValue)"
    $dbConfig[$key] = if ([string]::IsNullOrWhiteSpace($input)) { $defaultValue } else { $input }
}

# ========================
# Generate local.py
# ========================

(Get-Content $template) | ForEach-Object {
    $line = $_

    # Replace DLL paths
    foreach ($key in $dllPaths.Keys) {
        if ($line -match "$key\s*=") {
            $line = "$key = r`"$($dllPaths[$key])`""
        }
    }

    # Replace database lines
    foreach ($dbKey in $dbConfig.Keys) {
        # Match 'KEY': "" in the DATABASE config
        if ($line -match "['`"]$dbKey['`"]\s*:\s*['`"]*['`"]") {
            $line = "        `"$dbKey`": `"$($dbConfig[$dbKey])`","
        }
    }

    $line
} | Set-Content $output

# ========================
# Final Messaging
# ========================

if ($missing.Count -gt 0) {
    Write-Host "`nMissing DLLs:" -ForegroundColor Red
    $missing | ForEach-Object { Write-Host " - $_" }
    Write-Host "`nYou can install them via:" -ForegroundColor Yellow
    Write-Host "   make install-windows-specific-tools"
} else {
    Write-Host "`nAll required DLLs are present." -ForegroundColor Green
}

Write-Host "Configuration file '$output' generated successfully." -ForegroundColor Green
