$ppt = New-Object -ComObject PowerPoint.Application
$pres = $ppt.Presentations.Open("C:\Users\shivangi\Dropbox\My PC (LAPTOP-Q3DGSR28)\Downloads\Mini_SIEM_Midterm_Theme.pptx")
$out = "C:\Users\shivangi\Projects\marketforensics\docs\presentation_assets\siem_preview.pdf"
$pres.SaveAs($out, 32)
$pres.Close()
$ppt.Quit()
Write-Output $out
