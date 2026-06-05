[CmdletBinding()]
param(
  [int] $Port = 8790,
  [int] $MaxPort = 8800,
  [string] $BindAddress = "0.0.0.0",
  [switch] $Restart
)

$ErrorActionPreference = "Stop"

$requestRoot = Resolve-Path (Join-Path $PSScriptRoot "..")
$sourceWebRoot = Resolve-Path (Join-Path $requestRoot "web")
$sourceAssetsRoot = Resolve-Path (Join-Path $requestRoot "assets")
$serverScript = Resolve-Path (Join-Path $PSScriptRoot "intranet_preview_server.py")
$evidenceRoot = Join-Path $requestRoot "evidence"
$pidFile = Join-Path $evidenceRoot "intranet-preview.pid"
$portFile = Join-Path $evidenceRoot "intranet-preview.port"
$stdoutLog = Join-Path $evidenceRoot "intranet-preview.stdout.log"
$stderrLog = Join-Path $evidenceRoot "intranet-preview.stderr.log"

if (-not (Test-Path -LiteralPath $evidenceRoot)) {
  New-Item -ItemType Directory -Force -Path $evidenceRoot | Out-Null
}

function Get-PythonExecutable {
  $python = Get-Command python -ErrorAction SilentlyContinue
  if ($python) {
    return $python.Source
  }

  $py = Get-Command py -ErrorAction SilentlyContinue
  if ($py) {
    return $py.Source
  }

  throw "Python executable was not found. Install Python 3 or add python.exe to PATH."
}

function Test-PortInUse([int] $TargetPort) {
  $connection = Get-NetTCPConnection -State Listen -LocalPort $TargetPort -ErrorAction SilentlyContinue |
    Select-Object -First 1
  return [bool] $connection
}

function Get-ExistingPreviewProcess {
  if (-not (Test-Path -LiteralPath $pidFile)) {
    return $null
  }

  $rawPid = (Get-Content -LiteralPath $pidFile -ErrorAction SilentlyContinue | Select-Object -First 1)
  $processId = 0
  if (-not [int]::TryParse([string] $rawPid, [ref] $processId)) {
    return $null
  }

  return Get-Process -Id $processId -ErrorAction SilentlyContinue
}

function Get-LanUrls([int] $TargetPort) {
  $addresses = Get-NetIPAddress -AddressFamily IPv4 |
    Where-Object {
      $_.IPAddress -notlike "127.*" -and
      $_.IPAddress -notlike "169.254.*" -and
      $_.IPAddress -notlike "172.17.*"
    } |
    Sort-Object InterfaceMetric, InterfaceAlias |
    Select-Object -ExpandProperty IPAddress -Unique

  return @($addresses | ForEach-Object { "http://$($_):$TargetPort/web/index.html" })
}

$existing = Get-ExistingPreviewProcess
if ($existing -and $Restart) {
  Stop-Process -Id $existing.Id -Force
  Start-Sleep -Milliseconds 500
  $existing = $null
}

if ($existing -and -not $Restart) {
  $activePort = $Port
  if (Test-Path -LiteralPath $portFile) {
    $savedPort = 0
    $rawPort = Get-Content -LiteralPath $portFile -ErrorAction SilentlyContinue | Select-Object -First 1
    if ([int]::TryParse([string] $rawPort, [ref] $savedPort)) {
      $activePort = $savedPort
    }
  }
  Set-Content -LiteralPath $portFile -Encoding ASCII -Value $activePort
  $lanUrls = Get-LanUrls $activePort
  $result = [ordered]@{
    status = "already-running"
    pid = $existing.Id
    port = $activePort
    bindAddress = $BindAddress
    localUrl = "http://127.0.0.1:$activePort/web/index.html"
    lanUrls = @($lanUrls)
    servedRoots = @($sourceWebRoot.Path, $sourceAssetsRoot.Path)
    stdoutLog = $stdoutLog
    stderrLog = $stderrLog
    note = "같은 사내망에서 LAN URL로 접속할 수 있습니다. Windows 방화벽이 차단하면 개인/사내 네트워크 허용이 필요합니다."
  } | ConvertTo-Json -Depth 4
  Write-Output $result
  exit 0
}

$selectedPort = $null
foreach ($candidate in $Port..$MaxPort) {
  if (-not (Test-PortInUse $candidate)) {
    $selectedPort = $candidate
    break
  }
}

if (-not $selectedPort) {
  throw "No available port between $Port and $MaxPort."
}

$python = Get-PythonExecutable
$arguments = @("-u", $serverScript.Path, $BindAddress, [string] $selectedPort, $sourceWebRoot.Path, $sourceAssetsRoot.Path)

$process = Start-Process `
  -FilePath $python `
  -ArgumentList $arguments `
  -WorkingDirectory $sourceWebRoot.Path `
  -PassThru `
  -WindowStyle Hidden `
  -RedirectStandardOutput $stdoutLog `
  -RedirectStandardError $stderrLog

Set-Content -LiteralPath $pidFile -Encoding ASCII -Value $process.Id
Set-Content -LiteralPath $portFile -Encoding ASCII -Value $selectedPort
Start-Sleep -Milliseconds 800

if ($process.HasExited) {
  $stderr = if (Test-Path -LiteralPath $stderrLog) { Get-Content -Raw -LiteralPath $stderrLog } else { "" }
  throw "Intranet preview server exited early. $stderr"
}

$lanUrls = Get-LanUrls $selectedPort

$result = [ordered]@{
  status = "started"
  pid = $process.Id
  port = $selectedPort
  bindAddress = $BindAddress
  localUrl = "http://127.0.0.1:$selectedPort/web/index.html"
  lanUrls = @($lanUrls)
  servedRoots = @($sourceWebRoot.Path, $sourceAssetsRoot.Path)
  stdoutLog = $stdoutLog
  stderrLog = $stderrLog
  note = "같은 사내망에서 LAN URL로 접속할 수 있습니다. Windows 방화벽이 차단하면 개인/사내 네트워크 허용이 필요합니다."
} | ConvertTo-Json -Depth 4

Write-Output $result
