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

$dbDefaults = [ordered]@{
    NAME     = "arpas-db"
    USER     = "postgres"
    PASSWORD = "postgres"
    HOST     = "localhost"
    PORT     = "5556"
}

Write-Host "`nSetting up local PostgreSQL database configuration..." -ForegroundColor Cyan

$dbConfig = @{}
foreach ($key in $dbDefaults.Keys) {
    $defaultValue = if ($currentDbConfig.ContainsKey($key) -and -not [string]::IsNullOrWhiteSpace($currentDbConfig[$key])) { 
        $currentDbConfig[$key] 
    } else { 
        $dbDefaults[$key] 
    }
    $input = Read-Host "DB $key (current: $defaultValue)"
    $dbConfig[$key] = if ([string]::IsNullOrWhiteSpace($input)) { $defaultValue } else { $input }
}

# Show Database Configuration Summary
Write-Host ""
Write-Host "Database Configuration:" -ForegroundColor Green
Write-Host "DATABASES = {" -ForegroundColor Green
Write-Host "    `"default`": {" -ForegroundColor Green
Write-Host "        `"ENGINE`": `"django.contrib.gis.db.backends.postgis`"," -ForegroundColor Green
foreach ($key in @("NAME", "USER", "PASSWORD", "HOST", "PORT")) {
    Write-Host "        `"$key`": `"$($dbConfig[$key])`"," -ForegroundColor Green
}
Write-Host "        `"OPTIONS`": {}," -ForegroundColor Green
Write-Host "    }" -ForegroundColor Green
Write-Host "}" -ForegroundColor Green

# ========================
# MinIO Configuration
# ========================

# Read current MinIO values from existing local.py if it exists
$currentMinioConfig = @{}
if (Test-Path $output) {
    $content = Get-Content $output
    $inMinioSection = $false
    foreach ($line in $content) {
        if ($line -match 'MINIO_DATA\s*=') {
            $inMinioSection = $true
        }
        if ($inMinioSection -and $line -match '"(endpoint|region|accessKey|secretKey)"\s*:\s*"([^"]*)"') {
            $currentMinioConfig[$matches[1]] = $matches[2]
        }
        if ($inMinioSection -and $line -match '"allowed_buckets"\s*:\s*\[([^\]]*)\]') {
            # Extract bucket names from array format ["bucket1","bucket2","bucket3"]
            $bucketsString = $matches[1]
            $buckets = @()
            if ($bucketsString -match '"([^"]+)"') {
                $buckets = [regex]::Matches($bucketsString, '"([^"]+)"') | ForEach-Object { $_.Groups[1].Value }
            }
            $currentMinioConfig["allowed_buckets"] = $buckets -join ","
        }
        if ($inMinioSection -and $line -match '^\s*}') {
            $inMinioSection = $false
        }
    }
}

$minioDefaults = [ordered]@{
    endpoint = "https://minio.liqd.net"
    region = "eu-central-1"
    allowed_buckets = ""
    accessKey = ""
    secretKey = ""
}

Write-Host "`nSetting up MinIO configuration..." -ForegroundColor Cyan

$minioConfig = @{}
foreach ($key in $minioDefaults.Keys) {
    $defaultValue = if ($currentMinioConfig.ContainsKey($key) -and -not [string]::IsNullOrWhiteSpace($currentMinioConfig[$key])) { 
        $currentMinioConfig[$key] 
    } else { 
        $minioDefaults[$key] 
    }
    
    if ($key -eq "allowed_buckets") {
        $input = Read-Host "MinIO $key - comma-separated list (current: $defaultValue)"
    } else {
        $input = Read-Host "MinIO $key (current: $defaultValue)"
    }
    
    $minioConfig[$key] = if ([string]::IsNullOrWhiteSpace($input)) { $defaultValue } else { $input }
}

# Show MinIO Configuration Summary
Write-Host ""
Write-Host "MinIO Configuration:" -ForegroundColor Green
Write-Host "MINIO_DATA = {" -ForegroundColor Green
Write-Host "    `"endpoint`": `"$($minioConfig['endpoint'])`"," -ForegroundColor Green
Write-Host "    `"region`": `"$($minioConfig['region'])`"," -ForegroundColor Green

# Format allowed_buckets array
$bucketValue = $minioConfig["allowed_buckets"]
if ([string]::IsNullOrWhiteSpace($bucketValue)) {
    Write-Host "    `"allowed_buckets`": [""]," -ForegroundColor Green
} else {
    $buckets = $bucketValue.Split(',') | ForEach-Object { "`"$($_.Trim())`"" }
    $bucketsArray = $buckets -join ","
    Write-Host "    `"allowed_buckets`": [$bucketsArray]," -ForegroundColor Green
}

Write-Host "    `"accessKey`": `"$($minioConfig['accessKey'])`"," -ForegroundColor Green
Write-Host "    `"secretKey`": `"$($minioConfig['secretKey'])`"" -ForegroundColor Green
Write-Host "}" -ForegroundColor Green

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

    # Replace MinIO lines
    foreach ($minioKey in $minioConfig.Keys) {
        if ($minioKey -eq "allowed_buckets") {
            # Special handling for allowed_buckets array
            if ($line -match "['`"]allowed_buckets['`"]\s*:\s*\[.*\]") {
                $bucketValue = $minioConfig[$minioKey]
                if ([string]::IsNullOrWhiteSpace($bucketValue)) {
                    $line = "    `"allowed_buckets`": [`"`"],"
                } else {
                    # Split by comma and create array format ["bucket1","bucket2","bucket3"]
                    $buckets = $bucketValue.Split(',') | ForEach-Object { "`"$($_.Trim())`"" }
                    $bucketsArray = $buckets -join ","
                    $line = "    `"allowed_buckets`": [$bucketsArray],"
                }
            }
        } else {
            # Handle other MinIO keys (endpoint, region, accessKey, secretKey)
            if ($line -match "['`"]$minioKey['`"]\s*:\s*['`"]*['`"]") {
                $line = "    `"$minioKey`": `"$($minioConfig[$minioKey])`","
            }
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
