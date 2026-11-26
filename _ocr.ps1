# WinRT OCR via PowerShell: ocr.ps1 <image> -> text
param([string]$path)
Add-Type -AssemblyName System.Runtime.WindowsRuntime
$asyncOp = [Windows.Media.Ocr.OcrEngine]::RecognizeAsync
$engine = [Windows.Media.Ocr.OcrEngine]::TryCreateFromLanguage([Windows.Globalization.Language]::new("en-US"))
$sf = [Windows.Storage.StorageFile]::GetFileFromPathAsync($path).GetAwaiter().GetResult()
$stream = $sf.OpenAsync([Windows.Storage.FileAccessMode]::Read).GetAwaiter().GetResult()
$bmp = [Windows.Graphics.Imaging.BitmapDecoder]::CreateAsync($stream).GetAwaiter().GetResult()
$sw = $bmp.GetSoftwareBitmapAsync().GetAwaiter().GetResult()
$result = $engine.RecognizeAsync($sw).GetAwaiter().GetResult()
$result.Text
