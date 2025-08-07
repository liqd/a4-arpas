#!/usr/bin/env node

const { execSync } = require('child_process')
const path = require('path')
const os = require('os')

const isWindows = os.platform().startsWith('win')

// Get the project root directory (one level up from scripts)
const projectRoot = path.join(__dirname, '..')

try {
  if (isWindows) {
    // Windows: Use PowerShell script
    const scriptPath = path.join(__dirname, '../windows_specific', 'update-local-arpas-arc.ps1')
    execSync('powershell -ExecutionPolicy Bypass -File "' + scriptPath + '"', {
      stdio: 'inherit',
      cwd: projectRoot // Run from project root
    })
  } else {
    // Unix-like: Use bash script
    const scriptPath = path.join(__dirname, 'update-local-arpas-arc.sh')
    execSync('bash "' + scriptPath + '"', {
      stdio: 'inherit',
      cwd: projectRoot // Run from project root
    })
  }
} catch (error) {
  console.error('Failed to update arpas-arc:', error.message)
  process.exit(1)
}
