$k = 'HKLM:\SYSTEM\CurrentControlSet\Control\Power\User\PowerSchemes\381b4222-f694-41f0-9685-ff5bb260df2e\4f971e89-eebd-4455-a8de-9e59040e7347\5ca83367-6e45-459f-a27b-476b1d01c936'
Set-ItemProperty $k -Name ACSettingIndex -Value 0
Set-ItemProperty $k -Name DCSettingIndex -Value 0
$v = Get-ItemProperty $k
Write-Output ('LIDACTION now AC=' + $v.ACSettingIndex + ' DC=' + $v.DCSettingIndex)
