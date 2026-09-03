# Builds the deployable pages from src/templates into the repo root.
# Run:  powershell -File build.ps1      (or double-click build.cmd)
#
# Templates are written artifact-style (title/link/style first, then markup);
# this wraps each one in a full HTML document and swaps the asset placeholders
# for real file paths under /assets.

$ErrorActionPreference = 'Stop'
$root = Split-Path -Parent $MyInvocation.MyCommand.Path
$src  = Join-Path $root 'src\templates'

$assets = @{
  'data:font/woff2;base64,{{KAIO}}'          = 'assets/fonts/Kaio-Black.woff2'
  'data:image/jpeg;base64,{{HEROCROP}}'      = 'assets/img/hero-map-phone.jpg'
  'data:image/jpeg;base64,{{APPSHOT}}'       = 'assets/img/app-map.jpg'
  'data:image/jpeg;base64,{{MAGICAL}}'       = 'assets/img/magical-cafe.jpg'
  'data:image/jpeg;base64,{{ORANGERIE}}'     = 'assets/img/orangerie-elfenau.jpg'
  'data:image/png;base64,{{SPIELKISTE}}'     = 'assets/img/spielkiste.png'
  'data:image/svg+xml;base64,{{WIDE}}'       = 'assets/logos/friendly-spaces.svg'
  'data:image/svg+xml;base64,{{L_ORANGERIE}}'= 'assets/logos/partners/orangerie-elfenau.svg'
  'data:image/svg+xml;base64,{{L_MARKTHALLE}}'= 'assets/logos/partners/markthalle.svg'
  'data:image/svg+xml;base64,{{L_KLARA}}'    = 'assets/logos/partners/klara.svg'
  'data:image/svg+xml;base64,{{L_MAGICAL}}'  = 'assets/logos/partners/magical-cafe.svg'
  'data:image/svg+xml;base64,{{L_SEMPRE}}'   = 'assets/logos/partners/sempre-berna.svg'
  'data:image/svg+xml;base64,{{L_LIS}}'      = 'assets/logos/partners/lis-atelier.svg'
  'data:image/svg+xml;base64,{{L_CRAFTY}}'   = 'assets/logos/partners/crafty-crew.svg'
}

$pages = @(
  # Keep these strings ASCII (use HTML entities): Windows PowerShell 5.1 reads
  # this file as ANSI and would double-encode any raw accented characters.
  @{ template = 'homepage.html';   out = 'index.html';
     title = 'Friendly Spaces &mdash; Switzerland&#39;s family-friendly label &amp; app';
     description = 'Friendly Spaces certifies caf&eacute;s, shops and cultural spaces where families are truly welcome &mdash; and puts every one of them on the map.' },
  @{ template = 'sponsoring.html'; out = 'sponsoring.html';
     title = 'Sponsoring &mdash; Friendly Spaces';
     description = 'Back Switzerland&#39;s family-friendly movement. Sponsoring and partnership opportunities with Friendly Spaces.' }
)

foreach ($p in $pages) {
  $html = [IO.File]::ReadAllText((Join-Path $src $p.template))
  foreach ($k in $assets.Keys) { $html = $html.Replace($k, $assets[$k]) }

  # split the artifact-style template into head bits and body markup
  $cut = $html.IndexOf('</style>') + '</style>'.Length
  $head = $html.Substring(0, $cut) -replace '<title>.*?</title>', ''
  $body = $html.Substring($cut)

  $doc = @"
<!doctype html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>$($p.title)</title>
<meta name="description" content="$($p.description)">
<link rel="icon" href="assets/favicon.png" type="image/png">
$($head.Trim())
</head>
<body>
$($body.Trim())
</body>
</html>
"@
  [IO.File]::WriteAllText((Join-Path $root $p.out), $doc, (New-Object System.Text.UTF8Encoding($false)))
  Write-Host "built $($p.out)"
}
