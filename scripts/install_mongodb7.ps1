# MongoDB 8.3 Windows 10 uyumsuz -> 7.0.34 kurar
# Yonetici PowerShell gerekir.

$ErrorActionPreference = "Stop"
$version = "7.0.34"
$msiUrl  = "https://fastdl.mongodb.org/windows/mongodb-windows-x86_64-$version-signed.msi"
$msiPath = "$env:TEMP\mongodb-$version.msi"
$service = "MongoDB"

Write-Host "MongoDB 8.3 kaldiriliyor..." -ForegroundColor Yellow
winget uninstall MongoDB.Server --accept-source-agreements --disable-interactivity 2>$null
Stop-Service $service -Force -ErrorAction SilentlyContinue
Get-Process mongod -ErrorAction SilentlyContinue | Stop-Process -Force
sc.exe delete $service 2>$null | Out-Null
Start-Sleep -Seconds 3

Write-Host "MongoDB $version indiriliyor (~600 MB)..." -ForegroundColor Cyan
Invoke-WebRequest -Uri $msiUrl -OutFile $msiPath -UseBasicParsing

Write-Host "Kuruluyor..." -ForegroundColor Cyan
$proc = Start-Process msiexec.exe -ArgumentList "/i", "`"$msiPath`"", "/qn", "ADDLOCAL=all" -Wait -PassThru
if ($proc.ExitCode -notin 0, 3010) {
    throw "MSI kurulum hatasi. Exit code: $($proc.ExitCode)"
}

$mongod = Get-ChildItem "C:\Program Files\MongoDB\Server" -Recurse -Filter "mongod.exe" |
    Sort-Object { [version]($_.Directory.Parent.Name) } -Descending |
    Select-Object -First 1

if (-not $mongod) { throw "mongod.exe bulunamadi." }

Write-Host "mongod: $($mongod.FullName)" -ForegroundColor Green
& $mongod.FullName --version

Write-Host "`nYapilandirma icin: .\scripts\setup_mongodb.ps1" -ForegroundColor Cyan
