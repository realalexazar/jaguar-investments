# Simple static file server for local preview (no installs required).
# Usage:  powershell -ExecutionPolicy Bypass -File .\serve.ps1
# Then open http://localhost:8765/ in a browser. Ctrl+C to stop.

$port = 8765
$root = $PSScriptRoot

$mime = @{
  ".html" = "text/html; charset=utf-8"
  ".css"  = "text/css; charset=utf-8"
  ".js"   = "text/javascript; charset=utf-8"
  ".json" = "application/json"
  ".svg"  = "image/svg+xml"
  ".png"  = "image/png"
  ".jpg"  = "image/jpeg"
  ".jpeg" = "image/jpeg"
  ".webp" = "image/webp"
  ".ico"  = "image/x-icon"
  ".woff" = "font/woff"
  ".woff2" = "font/woff2"
}

$listener = New-Object System.Net.HttpListener
$listener.Prefixes.Add("http://localhost:$port/")
$listener.Start()
Write-Host "Serving $root at http://localhost:$port/  (Ctrl+C to stop)"

while ($listener.IsListening) {
  $context = $listener.GetContext()
  $reqPath = [System.Uri]::UnescapeDataString($context.Request.Url.AbsolutePath)
  if ($reqPath -eq "/") { $reqPath = "/index.html" }
  $filePath = Join-Path $root ($reqPath.TrimStart("/") -replace "/", "\")

  if ((Test-Path $filePath -PathType Leaf) -and ((Resolve-Path $filePath).Path.StartsWith($root))) {
    $bytes = [System.IO.File]::ReadAllBytes($filePath)
    $ext = [System.IO.Path]::GetExtension($filePath).ToLower()
    $context.Response.ContentType = if ($mime.ContainsKey($ext)) { $mime[$ext] } else { "application/octet-stream" }
    $context.Response.ContentLength64 = $bytes.Length
    $context.Response.OutputStream.Write($bytes, 0, $bytes.Length)
  } else {
    $context.Response.StatusCode = 404
    $msg = [System.Text.Encoding]::UTF8.GetBytes("404 Not Found")
    $context.Response.OutputStream.Write($msg, 0, $msg.Length)
  }
  $context.Response.OutputStream.Close()
}
