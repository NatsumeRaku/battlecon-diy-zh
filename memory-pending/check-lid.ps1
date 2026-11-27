Get-ChildItem 'HKLM:\SYSTEM\CurrentControlSet\Control\Power\User\PowerSchemes\381b4222-f694-41f0-9685-ff5bb260df2e\4f971e89-eebd-4455-a8de-9e59040e7347' | ForEach-Object {
    $v = Get-ItemProperty $_.PSPath
    $name = $_.PSChildName
    if ($name -eq '5ca83367-6e45-459f-a27b-476b1d01c936') { $name = 'LIDACTION(合盖)' }
    elseif ($name -eq '7648efa3-dd9c-4e3e-b566-50f929386280') { $name = 'PBUTTONACTION(电源键)' }
    elseif ($name -eq 'a7066653-8d6c-40a8-910e-a1f54b84c7e5') { $name = 'UIBUTTON_ACTION' }
    elseif ($name -eq '96996bc0-ad50-47ec-923b-6f41874dd9eb') { $name = 'SBUTTONACTION(睡眠键)' }
    Write-Output ($name + ' AC=' + $v.ACSettingIndex + ' DC=' + $v.DCSettingIndex)
}
