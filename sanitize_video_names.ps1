# ======== CONFIGURATION 480P ========

# VAR
$baseDir = "C:\Users\vivie\Videos\Mix"

$playlists = @(
    # @{
    #     playlistUrl = "https://www.youtube.com/playlist?list=PLUj2G-D5BOkOUeCGerNiWKiDnME_bRcXk"
    #     folderName = "VHS_Glitch_Bank"
    # },
    # @{
    #     playlistUrl = "https://www.youtube.com/playlist?list=PLytgPQg7TYsNhY-U8mBrJ5-6GFAS_vQ_G"
    #     folderName = "Casual_Ravers - CARTOON"
    # },
    # @{
    #     playlistUrl = "https://www.youtube.com/playlist?list=PLytgPQg7TYsPDLNbyN8rI1Z2RK0Cz-kUR"
    #     folderName = "Casual_Ravers - GLITCH"
    # },
    # @{
    #     playlistUrl = "https://www.youtube.com/playlist?list=PLytgPQg7TYsO_WABZbdGtfkSLkFI9PtwD"
    #     folderName = "Casual_Ravers - RANDOM"
    # }
    @{
        playlistUrl = "https://www.youtube.com/playlist?list=PLytgPQg7TYsPmripa3HQ_dt1DdFvG2GT8"
        folderName = "Casual_Ravers - ORGANIC"
    }
)

Write-Host "========== TELECHARGEMENT 480P ==========" -ForegroundColor Cyan
Write-Host ""

foreach ($playlist in $playlists) {
    # DOSSIER DE BASE
    $outputDir = "$baseDir\$($playlist.folderName)"
    
    # Creer le dossier
    New-Item -ItemType Directory -Path $outputDir -Force | Out-Null
    Write-Host "Telechargement dans: $outputDir" -ForegroundColor Green
    
    # Telecharger en 480p
    .\yt-dlp.exe -f "best[height<=480]" -o "$outputDir/%(title)s.%(ext)s" -i "$($playlist.playlistUrl)"
    
    # Renommer les fichiers - STRICT (pas d'espaces, pas de caracteres speciaux)
    Write-Host "Nettoyage des noms..." -ForegroundColor Yellow
    Get-ChildItem -Path $outputDir -File | ForEach-Object {
        $newName = $_.BaseName `
            -replace '[^\w]', '' `
            -replace '^_+|_+$', ''
        $newName = $newName + $_.Extension
        if ($newName -ne $_.Name) {
            Rename-Item -LiteralPath $_.FullName -NewName $newName
            Write-Host "  OK - $($_.Name) -> $newName" -ForegroundColor Gray
        }
    }
    
    Write-Host "Fini!" -ForegroundColor Green
    Write-Host ""
}

Write-Host "========== TERMINE ==========" -ForegroundColor Green
Write-Host "Pret pour cut_clips_random.ps1"