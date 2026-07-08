# Publish freeproxydb SDK to PyPI (or TestPyPI).
#
# Usage:
#   .\publish.ps1              # build + upload to PyPI
#   .\publish.ps1 -Test        # upload to TestPyPI
#   .\publish.ps1 -DryRun      # build only, no upload
#   .\publish.ps1 -Yes         # skip confirmation
#
# Credentials:
#   $env:TWINE_USERNAME = "__token__"
#   $env:TWINE_PASSWORD = "pypi-AgEI..."
#   or %USERPROFILE%\.pypirc

param(
    [switch]$Test,
    [switch]$DryRun,
    [switch]$Yes
)

$ErrorActionPreference = "Stop"
Set-Location $PSScriptRoot

function Get-Python {
    foreach ($cmd in @("python", "python3", "py")) {
        if (Get-Command $cmd -ErrorAction SilentlyContinue) {
            if ($cmd -eq "py") { return @("py", "-3") }
            return @($cmd)
        }
    }
    throw "Python not found. Install Python 3.9+ and ensure it is on PATH."
}

$py = Get-Python

$version = & $py @("-c", @"
import pathlib, re
text = pathlib.Path('pyproject.toml').read_text(encoding='utf-8')
m = re.search(r'^version\s*=\s*\"([^\"]+)\"', text, re.M)
print(m.group(1) if m else '?')
"@)

$repo = if ($Test) { "TestPyPI" } else { "PyPI" }
$repoUrl = if ($Test) { "https://test.pypi.org/legacy/" } else { "https://upload.pypi.org/legacy/" }

Write-Host "========================================"
Write-Host " freeproxydb SDK publish"
Write-Host " version : $version"
Write-Host " target  : $repo"
Write-Host " dir     : $PSScriptRoot"
Write-Host "========================================"

if (-not $Yes) {
    $ans = Read-Host "Continue? [y/N]"
    if ($ans -notmatch '^(y|yes)$') {
        Write-Host "Cancelled."
        exit 0
    }
}

Write-Host "[1/4] Installing build tools..."
& $py @("-m", "pip", "install", "-U", "pip", "build", "twine") | Out-Null

Write-Host "[2/4] Cleaning old artifacts..."
@("dist", "build") | ForEach-Object {
    if (Test-Path $_) { Remove-Item $_ -Recurse -Force }
}
Get-ChildItem -Filter "*.egg-info" -ErrorAction SilentlyContinue | Remove-Item -Recurse -Force
if (Test-Path "freeproxydb\*.egg-info") {
    Remove-Item "freeproxydb\*.egg-info" -Recurse -Force -ErrorAction SilentlyContinue
}

Write-Host "[3/4] Building sdist + wheel..."
& $py @("-m", "build")
if ($LASTEXITCODE -ne 0) { throw "build failed" }

Write-Host "Built artifacts:"
Get-ChildItem dist | Format-Table Name, Length

if ($DryRun) {
    Write-Host "Dry run complete (upload skipped)."
    exit 0
}

if (-not $env:TWINE_USERNAME -or -not $env:TWINE_PASSWORD) {
    $pypirc = Join-Path $env:USERPROFILE ".pypirc"
    if (-not (Test-Path $pypirc)) {
        throw "Set TWINE_USERNAME and TWINE_PASSWORD, or configure $pypirc"
    }
}

Write-Host "[4/4] Uploading to $repo..."
& $py @("-m", "twine", "upload", "--non-interactive", "--repository-url", $repoUrl, "dist/*")
if ($LASTEXITCODE -ne 0) { throw "twine upload failed" }

Write-Host "Done. Install with:"
if ($Test) {
    Write-Host "  pip install -i https://test.pypi.org/simple/ freeproxydb==$version"
} else {
    Write-Host "  pip install freeproxydb==$version"
}
