# MongoDB sorun teshisi - Yonetici PowerShell
Write-Host "=== MongoDB Teshis ===" -ForegroundColor Cyan

$mongod = "C:\Program Files\MongoDB\Server\8.3\bin\mongod.exe"
Write-Host "mongod var:" (Test-Path $mongod)

Write-Host "`n--- Servis ---"
sc.exe query MongoDB
sc.exe qc MongoDB | Select-String "BINARY_PATH_NAME|SERVICE_START_NAME"

Write-Host "`n--- Port 27017 ---"
netstat -ano | findstr ":27017"

Write-Host "`n--- Process ---"
Get-Process mongod -ErrorAction SilentlyContinue | Format-Table Id, CPU, StartTime

$logs = @(
    "C:\ProgramData\MongoDB\log\mongod.log",
    "C:\Program Files\MongoDB\Server\8.3\log\mongod.log"
)
foreach ($log in $logs) {
    if (Test-Path $log) {
        Write-Host "`n--- Log: $log (son 25 satir) ---"
        Get-Content $log -Tail 25
    }
}

Write-Host "`n--- Son MongoDB olaylari ---"
Get-WinEvent -LogName Application -MaxEvents 100 -ErrorAction SilentlyContinue |
    Where-Object { $_.Message -match 'MongoDB|mongod' } |
    Select-Object -First 5 TimeCreated, Id, @{n='Msg';e={$_.Message.Substring(0,[Math]::Min(300,$_.Message.Length))}} |
    Format-List
