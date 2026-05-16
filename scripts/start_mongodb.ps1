# MongoDB arka planda baslat (servis yoksa)
$mongod = Get-ChildItem "C:\Program Files\MongoDB\Server" -Recurse -Filter "mongod.exe" -ErrorAction SilentlyContinue |
    Sort-Object { try { [version]($_.Directory.Parent.Name) } catch { [version]"0.0" } } -Descending |
    Select-Object -First 1

if (-not $mongod) { throw "mongod.exe yok. install_mongodb7.ps1 calistirin." }
$mongod = $mongod.FullName
$cfgPath = "C:\ProgramData\MongoDB\mongod.cfg"

if (Get-Process mongod -ErrorAction SilentlyContinue) {
    Write-Host "MongoDB zaten calisiyor."
    exit 0
}
if (-not (Test-Path $cfgPath)) {
    throw "Once setup_mongodb.ps1 calistirin."
}

Start-Process -FilePath $mongod -ArgumentList @("--config", $cfgPath) -WindowStyle Hidden
Start-Sleep -Seconds 3
if (-not (Get-Process mongod -ErrorAction SilentlyContinue)) {
    throw "Baslatilamadi. Log: C:\ProgramData\MongoDB\log\mongod.log"
}
Write-Host "MongoDB calisiyor."
