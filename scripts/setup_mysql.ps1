# MySQL Server 8.4 - ilk kurulum (yalnizca bir kez calistirin)
# Yonetici PowerShell:  Set-ExecutionPolicy Bypass -Scope Process; .\scripts\setup_mysql.ps1

$ErrorActionPreference = "Stop"
$mysqlBin = "C:\Program Files\MySQL\MySQL Server 8.4\bin"
$dataDir  = "C:\ProgramData\MySQL\MySQL Server 8.4\Data"
$iniPath  = "C:\ProgramData\MySQL\MySQL Server 8.4\my.ini"
$service  = "MySQL84"
$rootPass = "proje123!"

if (-not (Test-Path "$mysqlBin\mysqld.exe")) {
    throw "MySQL bulunamadi: $mysqlBin"
}

if (-not (Test-Path $dataDir)) {
    New-Item -ItemType Directory -Path $dataDir -Force | Out-Null
}

if (-not (Test-Path $iniPath)) {
    @"
[mysqld]
basedir=C:/Program Files/MySQL/MySQL Server 8.4
datadir=$($dataDir -replace '\\','/')
port=3306
character-set-server=utf8mb4
collation-server=utf8mb4_unicode_ci

[client]
port=3306
default-character-set=utf8mb4
"@ | Set-Content -Path $iniPath -Encoding ASCII
    Write-Host "my.ini olusturuldu: $iniPath"
}

$initialized = Test-Path (Join-Path $dataDir "mysql")
if (-not $initialized) {
    Write-Host "Veritabani dizini baslatiliyor..."
    & "$mysqlBin\mysqld.exe" --defaults-file="$iniPath" --initialize-insecure
}

$existing = Get-Service -Name $service -ErrorAction SilentlyContinue
if (-not $existing) {
    & "$mysqlBin\mysqld.exe" --install $service --defaults-file="$iniPath"
    Write-Host "Servis kuruldu: $service"
}

Start-Service $service
Start-Sleep -Seconds 3

& "$mysqlBin\mysql.exe" -u root -e "ALTER USER 'root'@'localhost' IDENTIFIED BY '$rootPass'; FLUSH PRIVILEGES;"
& "$mysqlBin\mysql.exe" -u root -p"$rootPass" -e "CREATE DATABASE IF NOT EXISTS retail_perf CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;"

Write-Host "MySQL hazir. Veritabani: retail_perf | Sifre: $rootPass"
