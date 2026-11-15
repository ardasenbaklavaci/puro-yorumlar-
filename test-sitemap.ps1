#!/usr/bin/env powershell
# Puro Blogu - Sitemap Diagnostic

Write-Host "Puro Blogu Sitemap Diagnostic" -ForegroundColor Cyan
Write-Host "=============================" -ForegroundColor Cyan
Write-Host ""

$baseUrl = "https://puroyorumlari.pages.dev"
$urls = @("sitemap.xml", "robots.txt", "_headers")

foreach ($file in $urls) {
    $url = "$baseUrl/$file"
    Write-Host "Testing: $file" -ForegroundColor Yellow
    
    try {
        $response = Invoke-WebRequest -Uri $url -UseBasicParsing -ErrorAction Stop
        Write-Host "  Status: $($response.StatusCode)"
        Write-Host "  Content-Type: $($response.Headers['Content-Type'])"
        Write-Host "  Cache-Control: $($response.Headers['Cache-Control'])"
        
        if ($response.Headers['Cache-Control'] -like "*max-age=0*") {
            Write-Host "  WARNING: Cache issue detected!" -ForegroundColor Red
        }
    } catch {
        Write-Host "  ERROR: $_" -ForegroundColor Red
    }
    Write-Host ""
}
