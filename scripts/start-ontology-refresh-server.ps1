[CmdletBinding()]
param(
  [int] $Port = 8798,
  [string] $BindAddress = "127.0.0.1"
)

$ErrorActionPreference = "Stop"

$scriptRoot = Split-Path -Parent $MyInvocation.MyCommand.Path
$repoRoot = Resolve-Path (Join-Path $scriptRoot "..\..")
$tmpDir = Join-Path $repoRoot "tmp"
$url = "http://$BindAddress`:$Port/api/ontology-refresh/status"

if (-not (Test-Path -LiteralPath $tmpDir)) {
  New-Item -ItemType Directory -Force -Path $tmpDir | Out-Null
}

function Get-PythonSpec {
  $python = Get-Command python -ErrorAction SilentlyContinue
  if ($python) {
    return [pscustomobject]@{ File = $python.Source; Args = @() }
  }

  $py = Get-Command py -ErrorAction SilentlyContinue
  if ($py) {
    return [pscustomobject]@{ File = $py.Source; Args = @("-3") }
  }

  throw "Python is required to run the ontology refresh server."
}

function Test-RefreshServer {
  try {
    $response = Invoke-WebRequest -Uri $url -UseBasicParsing -TimeoutSec 2
    return $response.StatusCode -eq 200 -and $response.Content -match '"status"'
  } catch {
    return $false
  }
}

if (Test-RefreshServer) {
  [ordered]@{
    status = "reused"
    url = $url
    port = $Port
    processId = $null
  } | ConvertTo-Json -Depth 3
  exit 0
}

$python = Get-PythonSpec
$serverLog = Join-Path $tmpDir "ontology-refresh-server-$Port.out.log"
$serverErrorLog = Join-Path $tmpDir "ontology-refresh-server-$Port.err.log"
$serverScript = Join-Path $scriptRoot "ontology_refresh_server.py"
$arguments = @($python.Args) + @($serverScript, "--host", $BindAddress, "--port", [string] $Port)

$process = Start-Process `
  -FilePath $python.File `
  -ArgumentList $arguments `
  -WorkingDirectory $repoRoot `
  -WindowStyle Hidden `
  -PassThru `
  -RedirectStandardOutput $serverLog `
  -RedirectStandardError $serverErrorLog

for ($attempt = 0; $attempt -lt 24; $attempt++) {
  Start-Sleep -Milliseconds 250
  if (Test-RefreshServer) {
    [ordered]@{
      status = "started"
      url = $url
      port = $Port
      processId = $process.Id
      serverLog = $serverLog
      serverErrorLog = $serverErrorLog
    } | ConvertTo-Json -Depth 3
    exit 0
  }
}

if (-not $process.HasExited) {
  Stop-Process -Id $process.Id -Force -ErrorAction SilentlyContinue
}

throw "Ontology refresh server did not become ready on port $Port. See $serverErrorLog."
