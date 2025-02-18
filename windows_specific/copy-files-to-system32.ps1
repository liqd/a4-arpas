param(
	[string]$sourcePath = $PSScriptRoot
)

# Function to log the result of the copy operation
function Log-CopyResult {
	param (
		[string]$filePath,
		[bool]$isCopied
	)
	if ($isCopied) {
		Write-Host "Successfully copied $filePath to C:\Windows\System32" -ForegroundColor Green
	} else {
		Write-Host "Failed to copy $filePath to C:\Windows\System32" -ForegroundColor Red
	}
}

# Function to copy a file to System32
function Copy-FileToSystem32 {
	param (
		[string]$fileName
	)
	$sourceFile = Join-Path -Path $sourcePath -ChildPath $fileName
	$destinationFile = Join-Path -Path "C:\Windows\System32" -ChildPath $fileName

	if (!(Test-Path $destinationFile)) {
		Copy-Item -Path $sourceFile -Destination $destinationFile -Force -Verbose
		Log-CopyResult -filePath $fileName -isCopied $true
	} else {
		Write-Host "File $fileName already exists in System32" -ForegroundColor Yellow
	}
}

# List of files to copy
$filesToCopy = @("magic1.dll", "libgnurx-0.dll", "magic.mgc")

Write-Host 'Start copy process for windows specific magic files...'
# Copy each file and log the result
foreach ($file in $filesToCopy) {
	Copy-FileToSystem32 -fileName $file
}

Write-Host 'Copy process completed.'
if (Test-Path 'C:/Windows/System32/magic1.dll') { Write-Host 'magic1.dll available in System32.' -ForegroundColor Green } else { Write-Host 'magic1.dll missing! Check for errors!' -ForegroundColor Red }
if (Test-Path 'C:/Windows/System32/libgnurx-0.dll') { Write-Host 'libgnurx-0.dll available in System32.' -ForegroundColor Green } else { Write-Host 'libgnurx-0.dll missing! Check for errors!' -ForegroundColor Red }
if (Test-Path 'C:/Windows/System32/magic.mgc') { Write-Host 'magic.mgc available in System32.' -ForegroundColor Green } else { Write-Host 'magic.mgc missing! Check for errors!' -ForegroundColor Red }


pause
