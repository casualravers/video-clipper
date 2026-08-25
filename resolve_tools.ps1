# Dot-sourced by every pipeline script (`. "$PSScriptRoot\resolve_tools.ps1"`) to locate
# ffmpeg/ffprobe/yt-dlp without hardcoding a machine-specific path. Lookup order:
#   1. Bundled next to this script (ffmpeg-8.0.1-essentials_build\bin\..., yt-dlp.exe)
#   2. System PATH (covers winget/choco/scoop installs)
# Exits with a clear message if neither is found, since every calling script needs these
# tools before it can do anything useful.

function Resolve-ToolPath {
    param(
        [Parameter(Mandatory)] [string] $BundledRelativePath,
        [Parameter(Mandatory)] [string] $CommandName
    )

    $bundled = Join-Path $PSScriptRoot $BundledRelativePath
    if (Test-Path $bundled) {
        return $bundled
    }

    $cmd = Get-Command $CommandName -ErrorAction SilentlyContinue
    if ($cmd) {
        return $cmd.Source
    }

    Write-Host "[ERREUR] '$CommandName' introuvable." -ForegroundColor Red
    Write-Host "  Cherche a : $bundled" -ForegroundColor Red
    Write-Host "  Et dans le PATH systeme (commande '$CommandName')." -ForegroundColor Red
    Write-Host "  -> Installez $CommandName, ou placez-le a l'emplacement ci-dessus." -ForegroundColor Red
    exit 1
}

$FfmpegPath = Resolve-ToolPath "ffmpeg-8.0.1-essentials_build\bin\ffmpeg.exe" "ffmpeg"
$FfprobePath = Resolve-ToolPath "ffmpeg-8.0.1-essentials_build\bin\ffprobe.exe" "ffprobe"
$YtDlpPath = Resolve-ToolPath "yt-dlp.exe" "yt-dlp"

# Shared default location for downloads/edits so all scripts (and the GUI) agree on where
# things live unless the user overrides it below. Override by setting $env:VHS_MIX_HOME
# before running a script, or by editing the path directly in the script's CONFIGURATION block.
$MixHome = if ($env:VHS_MIX_HOME) { $env:VHS_MIX_HOME } else { Join-Path $env:USERPROFILE "Videos\VHS-Glitch-Mix" }
