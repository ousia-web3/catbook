[CmdletBinding()]
param()

$ErrorActionPreference = "Stop"

$requestRoot = Resolve-Path (Join-Path $PSScriptRoot "..")
$pidFile = Join-Path $requestRoot "evidence/intranet-preview.pid"

if (-not (Test-Path -LiteralPath $pidFile)) {
  [ordered]@{
    status = "not-running"
    detail = "PID 파일이 없습니다."
  } | ConvertTo-Json -Depth 3
  exit 0
}

$rawPid = Get-Content -LiteralPath $pidFile | Select-Object -First 1
$processId = 0
if (-not [int]::TryParse([string] $rawPid, [ref] $processId)) {
  Remove-Item -LiteralPath $pidFile -Force
  [ordered]@{
    status = "not-running"
    detail = "PID 파일이 손상되어 정리했습니다."
  } | ConvertTo-Json -Depth 3
  exit 0
}

$process = Get-Process -Id $processId -ErrorAction SilentlyContinue
if ($process) {
  Stop-Process -Id $process.Id -Force
  Remove-Item -LiteralPath $pidFile -Force
  [ordered]@{
    status = "stopped"
    pid = $processId
  } | ConvertTo-Json -Depth 3
  exit 0
}

Remove-Item -LiteralPath $pidFile -Force
[ordered]@{
  status = "not-running"
  detail = "프로세스는 이미 종료되어 PID 파일만 정리했습니다."
} | ConvertTo-Json -Depth 3
