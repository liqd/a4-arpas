$template = "adhocracy-plus/config/settings/local.py.template"
$output = "adhocracy-plus/config/settings/local.py"

# ========================
# DLL Configuration
# ========================

# Read current values from existing local.py if it exists
$currentDllPaths = @{}
if (Test-Path $output) {
    Write-Host "`nReading current configuration from $output..." -ForegroundColor Yellow
    $content = Get-Content $output
    foreach ($line in $content) {
        if ($line -match '^(SPATIALITE_LIBRARY_PATH|GDAL_LIBRARY_PATH|GEOS_LIBRARY_PATH)\s*=\s*r?"([^"]*)"') {
            $currentDllPaths[$matches[1]] = $matches[2]
        }
    }
}

# Default DLL paths (fallback if no current values found)
$dllDefaults = @{
    SPATIALITE_LIBRARY_PATH = "C:/OSGeo4W/bin/mod_spatialite.dll"
    GDAL_LIBRARY_PATH       = "C:/OSGeo4W/bin/gdal311.dll"
    GEOS_LIBRARY_PATH       = "C:/OSGeo4W/bin/geos_c.dll"
}

Write-Host "`nSetting up local configuration for required DLLs..." -ForegroundColor Cyan

# Check current DLL paths and only prompt if not found
$dllPaths = @{}
$missing = @()

foreach ($key in $dllDefaults.Keys) {
    $currentPath = if ($currentDllPaths.ContainsKey($key)) { 
        $currentDllPaths[$key] 
    } else { 
        $dllDefaults[$key] 
    }
    
    if (Test-Path $currentPath) {
        Write-Host "$key found at $currentPath" -ForegroundColor Green
        $dllPaths[$key] = $currentPath
    } else {
        Write-Host "$key not found at $currentPath" -ForegroundColor Red
        $input = Read-Host "Enter new path for $key (current: $currentPath)"
        $dllPaths[$key] = if ([string]::IsNullOrWhiteSpace($input)) { $currentPath } else { $input }
        
        # Verify the new path
        if (Test-Path $dllPaths[$key]) {
            Write-Host "$key found at new location: $($dllPaths[$key])" -ForegroundColor Green
        } else {
            Write-Host "$key still not found at $($dllPaths[$key])" -ForegroundColor Red
            $missing += $key
        }
    }
}

# ========================
# Database Configuration
# ========================

# Read current database values from existing local.py if it exists
$currentDbConfig = @{}
if (Test-Path $output) {
    $content = Get-Content $output
    $inDatabaseSection = $false
    foreach ($line in $content) {
        if ($line -match 'DATABASES\s*=') {
            $inDatabaseSection = $true
        }
        if ($inDatabaseSection -and $line -match '"(NAME|USER|PASSWORD|HOST|PORT)"\s*:\s*"([^"]*)"') {
            $currentDbConfig[$matches[1]] = $matches[2]
        }
        if ($inDatabaseSection -and $line -match '^\s*}') {
            $inDatabaseSection = $false
        }
    }
}

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
    $defaultValue = if ($currentDbConfig.ContainsKey($key)) { 
        $currentDbConfig[$key] 
    } else { 
        $dbDefaults[$key] 
    }
    $input = Read-Host "DB $key (current: $defaultValue)"
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
