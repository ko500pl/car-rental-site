$ErrorActionPreference = 'Continue'
$project = 'rentup-ge'
$pkg     = 'ge.archi.rentupleasor'
$sha1    = '658bba107cde9725e19ec780303effb15b2a684e'
$appId   = '1:24636304417:android:808c1ecad430ca131d8760'

Write-Output "=============================================================="
Write-Output " RENTUP LEASOR - nabiji 2: SHA-1 da angarishebi"
Write-Output "=============================================================="

# --- SHA-1 -----------------------------------------------------------------
# Google Sign-In matches the (package name, signing fingerprint) pair against
# the OAuth client Firebase provisions for the Android app. Without the
# fingerprint the pair never matches and every sign-in fails with
# clientConfigurationError - the „SHA-1 ან პაკეტის სახელი არ ემთხვევა" message.
Write-Output ""
Write-Output "--- SHA-1 ---"
& firebase apps:android:sha:create $appId $sha1 --project $project 2>&1 | Out-String | Write-Output

Write-Output "--- registered fingerprints ---"
& firebase apps:android:sha:list $appId --project $project 2>&1 | Out-String | Write-Output

# --- who has actually signed in, and when ----------------------------------
Write-Output ""
Write-Output "--- accounts, newest login first ---"
$raw = Join-Path $PSScriptRoot 'auth_raw.json'
$out = Join-Path $PSScriptRoot 'auth-users.txt'
& firebase auth:export $raw --format=json --project $project 2>&1 | Out-String | Write-Output
if (Test-Path $raw) {
  try {
    $users = (Get-Content $raw -Raw | ConvertFrom-Json).users
    $rows = foreach ($u in $users) {
      if (-not $u.email) { continue }
      $last = 0
      if ($u.lastLoginAt) { $last = [int64]$u.lastLoginAt }
      elseif ($u.lastRefreshAt) { $last = [int64]([datetimeoffset]::Parse($u.lastRefreshAt)).ToUnixTimeMilliseconds() }
      [pscustomobject]@{
        uid   = $u.localId
        email = $u.email
        ms    = $last
        when  = if ($last -gt 0) { ([datetimeoffset]::FromUnixTimeMilliseconds($last)).ToLocalTime().ToString('yyyy-MM-dd HH:mm') } else { '(never)' }
      }
    }
    $sorted = $rows | Sort-Object -Property ms -Descending
    $lines = $sorted | ForEach-Object { "{0}`t{1}`t{2}" -f $_.uid, $_.email, $_.when }
    $lines | Set-Content -Path $out -Encoding UTF8
    $lines | Write-Output
  } catch { Write-Output "parse failed: $_" }
  Remove-Item $raw -Force
  Write-Output "(raw export deleted)"
}
Write-Output ""
Write-Output "=== DONE ==="
