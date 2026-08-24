# ======== CONFIGURATION ========
$ffmpegPath = "C:\Users\vivie\Videos\Mix\ffmpeg-8.0.1-essentials_build\bin\ffmpeg.exe"

# VIDEO D'ENTREE
$inputVideo = "C:\Users\vivie\Videos\Mix\edits\Projet_VHS_Glitch_ALL_poids\final_mix.mp4"

# VIDEO DE SORTIE
$outputVideo = "C:\Users\vivie\Videos\Mix\edits\Projet_VHS_Glitch_ALL_poids\final_mix_glitch.mp4"

# ======== EFFET GLITCH LEGER ========
# Combine :
# - Horizontal scan lines (effet VHS)
# - Slight color shift (RGB offset)
# - Random noise
# - Subtle distortion

$glitchFilter = "scale=1920:1080,fps=30,hue=s=1.2,noise=alls=0.05:allf=t"

Write-Host "Application de l'effet glitch..."

& $ffmpegPath -i "$inputVideo" `
    -vf "$glitchFilter" `
    -c:v libx264 -preset medium -crf 18 `
    -c:a aac -b:a 192k `
    "$outputVideo"

if (Test-Path $outputVideo) {
    Write-Host "OK - Glitch applique : $outputVideo"
} else {
    Write-Host "ERREUR - Impossible de creer la video"
}