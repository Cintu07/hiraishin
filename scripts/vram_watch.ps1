# Run a command while sampling per-process dedicated/shared GPU memory once a second.
# Shared usage that grows during the run means WDDM is spilling VRAM to system RAM (sysmem fallback).
# usage: powershell -File scripts/vram_watch.ps1 -Exe <exe> -ArgLine "<args>" -Out <log prefix>
param([string]$Exe, [string]$ArgLine, [string]$Out)

$p = Start-Process -FilePath $Exe -ArgumentList $ArgLine -NoNewWindow -PassThru `
    -RedirectStandardOutput "$Out.out" -RedirectStandardError "$Out.err"
$null = $p.Handle  # keep a handle so ExitCode is readable after exit
$rows = @("t_s,pid_dedicated_MiB,pid_shared_MiB,smi_used_MiB")
$t0 = Get-Date
while (-not $p.HasExited) {
    $ded = 0; $sh = 0
    try {
        $c = Get-Counter -Counter "\GPU Process Memory(pid_$($p.Id)*)\Dedicated Usage", "\GPU Process Memory(pid_$($p.Id)*)\Shared Usage" -ErrorAction Stop
        foreach ($s in $c.CounterSamples) {
            if ($s.Path -like "*dedicated usage") { $ded += $s.CookedValue } else { $sh += $s.CookedValue }
        }
    } catch {}
    $smi = (nvidia-smi --query-gpu=memory.used --format=csv,noheader,nounits).Trim()
    $rows += "{0:F1},{1:F0},{2:F0},{3}" -f ((Get-Date) - $t0).TotalSeconds, ($ded / 1MB), ($sh / 1MB), $smi
    Start-Sleep -Milliseconds 1000
}
$rows | Out-File -Encoding utf8 "$Out.vram.csv"
"exit=$($p.ExitCode)"

