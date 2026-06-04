[CmdletBinding()]
param(
    [Alias("Host")]
    [string]$BindHost = "127.0.0.1",
    [int]$Port = 5001,
    [string]$Version = "1.9.6",
    [ValidateSet("daily", "extended", "all")]
    [string]$Profile = "daily",
    [string]$LoadOnly = "",
    [int]$Threads = 2
)

$ErrorActionPreference = "Stop"

$projectRoot = Split-Path -Parent $PSScriptRoot
$venvPath = Join-Path $projectRoot ".venv-libretranslate"
$venvPython = Join-Path $venvPath "Scripts\python.exe"
$libreTranslate = Join-Path $venvPath "Scripts\libretranslate.exe"

if (-not (Test-Path -LiteralPath $venvPython)) {
    Write-Host "Creating LibreTranslate environment at $venvPath"
    python -m venv $venvPath
    if ($LASTEXITCODE -ne 0) {
        throw "Could not create the LibreTranslate virtual environment."
    }
}

$hasLibre = & $venvPython -c "import importlib.util; print(importlib.util.find_spec('libretranslate') is not None)"
$installedVersion = ""
if ($hasLibre.Trim() -eq "True") {
    $installedVersion = & $venvPython -c "import importlib.metadata as metadata; print(metadata.version('libretranslate'))" 2>$null
}
if ($installedVersion.Trim() -ne $Version) {
    Write-Host "Installing LibreTranslate $Version"
    & $venvPython -m pip install --upgrade "libretranslate==$Version"
    if ($LASTEXITCODE -ne 0) {
        throw "Could not install LibreTranslate $Version."
    }
}

if (-not (Test-Path -LiteralPath $libreTranslate)) {
    throw "LibreTranslate executable was not found at $libreTranslate."
}

$profiles = @{
    daily = "en,es,pt,pb,id,hi,tl"
    extended = "en,es,pt,pb,id,hi,tl,vi,th,ja,zh,ar,ca,fr,pl,ru"
    all = ""
}

if (-not $LoadOnly) {
    $LoadOnly = $profiles[$Profile]
}
if (-not $env:ARGOS_CHUNK_TYPE) {
    $env:ARGOS_CHUNK_TYPE = "MINISBD"
}
$env:PYTHONIOENCODING = "utf-8"

$arguments = @(
    "--host", $BindHost,
    "--port", "$Port",
    "--threads", "$Threads",
    "--disable-web-ui",
    "--disable-files-translation"
)
if ($LoadOnly) {
    $arguments += @("--load-only", $LoadOnly)
}

Write-Host "Starting LibreTranslate $Version at http://${BindHost}:$Port"
Write-Host "Profile: $Profile | Models: $(if ($LoadOnly) { $LoadOnly } else { 'all' }) | Threads: $Threads"
Write-Host "Leave this terminal open while running the ASO pipeline."
& $libreTranslate @arguments
exit $LASTEXITCODE
