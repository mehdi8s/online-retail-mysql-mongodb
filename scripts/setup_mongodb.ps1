# MongoDB servisini ProgramData ile kurar
# Yonetici PowerShell gerekir.

$ErrorActionPreference = "Stop"
$service  = "MongoDB"
$dataDir  = "C:\ProgramData\MongoDB\data"
$logDir   = "C:\ProgramData\MongoDB\log"
$cfgPath  = "C:\ProgramData\MongoDB\mongod.cfg"
$logFile  = "$logDir\mongod.log"

$mongod = Get-ChildItem "C:\Program Files\MongoDB\Server" -Recurse -Filter "mongod.exe" -ErrorAction SilentlyContinue |
    Sort-Object { try { [version]($_.Directory.Parent.Name) } catch { [version]"0.0" } } -Descending |
    Select-Object -First 1

if (-not $mongod) {
    throw "mongod.exe yok. Once: .\scripts\install_mongodb7.ps1"
}
$mongod = $mongod.FullName
Write-Host "Kullanilan: $mongod"

# Binary calisiyor mu?
$ver = & $mongod --version 2>&1
if ($LASTEXITCODE -ne 0 -and -not $ver) {
    throw "mongod calismiyor. MongoDB 7 kurun: .\scripts\install_mongodb7.ps1"
}
Write-Host $ver

New-Item -ItemType Directory -Force -Path $dataDir, $logDir | Out-Null

@"
storage:
  dbPath: $($dataDir -replace '\\','/')
systemLog:
  destination: file
  logAppend: true
  path: $($logFile -replace '\\','/')
net:
  port: 27017
  bindIp: 127.0.0.1
"@ | Set-Content -Path $cfgPath -Encoding ASCII

foreach ($acct in @("NT AUTHORITY\NETWORK SERVICE", "NT AUTHORITY\SYSTEM")) {
    icacls $dataDir /grant "${acct}:(OI)(CI)F" /T | Out-Null
    icacls $logDir  /grant "${acct}:(OI)(CI)F" /T | Out-Null
}

Stop-Service $service -Force -ErrorAction SilentlyContinue
Get-Process mongod -ErrorAction SilentlyContinue | Stop-Process -Force
Start-Sleep -Seconds 2
& $mongod --remove --serviceName $service 2>$null
sc.exe delete $service 2>$null | Out-Null
Start-Sleep -Seconds 2

Push-Location (Split-Path $mongod)
& .\mongod.exe --config $cfgPath --install --serviceName $service
Pop-Location
Start-Sleep -Seconds 2

Start-Service $service
Start-Sleep -Seconds 4

if ((Get-Service $service).Status -ne "Running") {
    if (Test-Path $logFile) { Get-Content $logFile -Tail 20 }
    throw "Servis baslamadi. Log: $logFile"
}

Write-Host "MongoDB hazir (port 27017)" -ForegroundColor Green
