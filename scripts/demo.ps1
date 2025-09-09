$ErrorActionPreference = 'Stop'
$base = 'http://127.0.0.1:8000'
function POST($p,$o){Invoke-RestMethod -Method Post -Uri ($base+$p) -Body ($o|ConvertTo-Json) -ContentType 'application/json'}
function GET($p){Invoke-RestMethod -Method Get -Uri ($base+$p)}

Write-Host 'Seeding KB...' -ForegroundColor Cyan
$kb=POST '/kb/' @{question='What are your hours?'; answer='9am-6pm Mon-Sat.'}
$kb | ConvertTo-Json -Compress | Write-Host

Write-Host 'Known question call (should resolve)...' -ForegroundColor Cyan
$known=POST '/agent/receive' @{caller_id='+15550001'; question='What are your hours?'; timeout_seconds=10}
$known | ConvertTo-Json -Compress | Write-Host

Write-Host 'Unknown question call (should pend)...' -ForegroundColor Cyan
$unknown=POST '/agent/receive' @{caller_id='+15550002'; question='Do you do nails?'; timeout_seconds=5}
$unknown | ConvertTo-Json -Compress | Write-Host

Write-Host 'Pending list...' -ForegroundColor Cyan
$pending=GET '/supervisor/pending'
$pending | ConvertTo-Json -Compress | Write-Host

if($pending.Length -gt 0){
  $rid=$pending[0].id
  Write-Host "Answering request #$rid ..." -ForegroundColor Cyan
  $ans=POST ("/supervisor/$rid/answer") @{answer='No, we do not offer nails currently.'}
  $ans | ConvertTo-Json -Compress | Write-Host
}

Write-Host 'History...' -ForegroundColor Cyan
$history=GET '/supervisor/history'
$history | ConvertTo-Json -Compress | Write-Host
