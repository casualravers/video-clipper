# ======== CONFIGURATION 480P ========

. "$PSScriptRoot\resolve_tools.ps1"

# VAR - par defaut : %USERPROFILE%\Videos\VHS-Glitch-Mix\downloads (modifiable ci-dessous,
# ou en definissant $env:VHS_MIX_HOME avant de lancer le script)
$baseDir = Join-Path $MixHome "downloads"

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
    
    # Telecharger en 480p (bv*+ba : YouTube ne fournit quasiment plus de flux pre-merges
    # au-dela de 360p, "best[height<=480]" seul echoue desormais avec "Requested format
    # is not available" sur la plupart des videos). --merge-output-format force mp4 car
    # les scripts suivants ne scannent que *.mp4. --download-archive fait qu'un re-lancement
    # sur la meme playlist ne re-telecharge que les videos absentes de l'archive (suivi par
    # ID video, insensible au renommage ci-dessous) - un fichier d'archive par dossier.
    $ffmpegDir = Split-Path $FfmpegPath -Parent
    $archiveFile = Join-Path $outputDir ".download_archive.txt"
    & $YtDlpPath -f "bv*[height<=480]+ba/b[height<=480]" --merge-output-format mp4 --ffmpeg-location "$ffmpegDir" --download-archive "$archiveFile" -o "$outputDir/%(title)s.%(ext)s" -i "$($playlist.playlistUrl)"

    # Renommer les fichiers - STRICT (pas d'espaces, pas de caracteres speciaux)
    # (le fichier d'archive est exclu : le renommer casserait le suivi au prochain lancement)
    Write-Host "Nettoyage des noms..." -ForegroundColor Yellow
    Get-ChildItem -Path $outputDir -File | Where-Object { $_.Name -ne ".download_archive.txt" } | ForEach-Object {
        $newStem = $_.BaseName `
            -replace '[^\w]', '' `
            -replace '^_+|_+$', ''
        $newName = $newStem + $_.Extension
        if ($newName -ne $_.Name) {
            # Sanitizing strips spaces/punctuation, so two differently-titled videos can
            # collide onto the same sanitized name - disambiguate instead of letting
            # Rename-Item fail on an existing target.
            $n = 2
            while (Test-Path (Join-Path $outputDir $newName)) {
                $newName = "$newStem`_$n$($_.Extension)"
                $n++
            }
            Rename-Item -LiteralPath $_.FullName -NewName $newName
            Write-Host "  OK - $($_.Name) -> $newName" -ForegroundColor Gray
        }
    }
    
    Write-Host "Fini!" -ForegroundColor Green
    Write-Host ""
}

Write-Host "========== TERMINE ==========" -ForegroundColor Green
Write-Host "Pret pour cut_clips_random.ps1"