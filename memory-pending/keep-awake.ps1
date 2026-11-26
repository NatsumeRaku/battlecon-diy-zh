# 防睡眠守护：挂着期间系统不睡眠；退出即归还控制权给电源计划
$sig = '[DllImport("kernel32.dll")] public static extern uint SetThreadExecutionState(uint esFlags);'
$t = Add-Type -MemberDefinition $sig -Name ES -Namespace WK -PassThru
# 0x80000000=ES_CONTINUOUS 0x00000001=ES_SYSTEM_REQUIRED 0x00000002=ES_DISPLAY_REQUIRED(不关屏,屏幕交给电源计划)
$flags = 0x80000001
$t::SetThreadExecutionState($flags) | Out-Null
$deadline = Get-Date '2026-11-27 17:40'
while ((Get-Date) -lt $deadline) {
    Start-Sleep -Seconds 60
    $t::SetThreadExecutionState($flags) | Out-Null
}
$t::SetThreadExecutionState(0x80000000) | Out-Null
Write-Output "keep-awake expired, control returned to power plan"
