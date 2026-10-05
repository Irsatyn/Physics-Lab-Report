param([Parameter(Mandatory=$true)][string]$InputDocx,
      [Parameter(Mandatory=$true)][string]$OutputPdf)
# Windows with an existing Microsoft Word installation. No macros or input writes.
$ErrorActionPreference = 'Stop'
$wordApp = $null
$openedDoc = $null
$inputFile = (Resolve-Path -LiteralPath $InputDocx).Path
$outputFile = [System.IO.Path]::GetFullPath($OutputPdf)
if ($inputFile -eq $outputFile -or [System.IO.Path]::GetExtension($outputFile) -ne '.pdf') {
    throw 'Output must be a separate PDF file'
}
if (Test-Path -LiteralPath $outputFile) { throw 'Output exists; choose a fresh PDF path' }
try {
    $wordApp = New-Object -ComObject Word.Application
    $wordApp.Visible = $false
    $wordApp.DisplayAlerts = 0
    $wordApp.AutomationSecurity = 3
    $openedDoc = $wordApp.Documents.Open($inputFile, $false, $true)
    $openedDoc.ExportAsFixedFormat($outputFile, 17)
    Write-Output "Exported read-only report PDF: $outputFile"
} finally {
    if ($null -ne $openedDoc) { $openedDoc.Close(0); [void][Runtime.InteropServices.Marshal]::ReleaseComObject($openedDoc) }
    if ($null -ne $wordApp) { $wordApp.Quit(0); [void][Runtime.InteropServices.Marshal]::ReleaseComObject($wordApp) }
}
