# 🎬 VHS Glitch Video Generator - Guide d'utilisation

Guide complet pour générer des vidéos VHS Glitch randomisées avec PowerShell et FFmpeg.

---

## 🖥️ Interface Graphique

Une GUI desktop (Python + pywebview) remplace maintenant l'édition manuelle des scripts `.ps1` : 3 onglets (Téléchargement, Génération, Effet Glitch), configuration sauvegardée dans `config.json`, progression et logs en direct.

```powershell
py -m pip install -r requirements.txt   # une seule fois
py gui\app.py                           # ou double-clic sur run_gui.bat
```

Les scripts `.ps1` ci-dessous restent utilisables tels quels pour un usage en ligne de commande — voir [CLAUDE.md](CLAUDE.md) pour le détail de l'architecture de la GUI.

---

## ⚙️ Installation & Setup

### Prérequis

- **FFmpeg** : soit le dossier `ffmpeg-8.0.1-essentials_build` à la racine du repo (à côté des scripts), soit déjà installé et accessible dans le PATH système (winget, choco, scoop...) — détecté automatiquement dans les deux cas, aucun chemin à modifier.
- **yt-dlp** : `yt-dlp.exe` est déjà fourni à la racine du repo ; sinon, une installation dans le PATH système est aussi détectée automatiquement.
- **PowerShell** : Version 5.0 ou supérieure

Les dossiers de téléchargement/sortie par défaut sont créés sous `%USERPROFILE%\Videos\VHS-Glitch-Mix\` (scripts comme GUI) — rien à configurer pour un premier essai. Modifiable par script en éditant la variable correspondante, ou globalement en définissant `$env:VHS_MIX_HOME` avant de lancer un script `.ps1`.

### Configuration PowerShell

Si vous avez une erreur d'exécution de scripts, lancez ceci UNE SEULE FOIS :

```powershell
Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser
```

Répondez **Y** (Yes).

---

## 🚀 Démarrage Rapide (usage avancé — scripts individuels)

> La GUI (section ci-dessus) couvre ce même workflow avec une interface graphique. Cette section reste utile pour un usage en ligne de commande ou pour comprendre/modifier la logique sous-jacente.

### Étape 1 : Télécharger les playlists

```powershell
.\sanitize_video_names.ps1
```

**Ce que ça fait** :
- Télécharge la/les playlist(s) YouTube configurées en 480p
- Crée les dossiers automatiquement
- Nettoie les noms (accents, caractères spéciaux)
- ⏱️ Durée : 30-60 minutes

**Exemple de configuration multi-playlists** (les 3 premières sont commentées par défaut dans le script — seule `Casual_Ravers - ORGANIC` est active) :
```
VHS_Glitch_Bank         (20% utilisation)
Casual_Ravers - CARTOON (35% utilisation)
Casual_Ravers - GLITCH  (15% utilisation)
Casual_Ravers - RANDOM  (30% utilisation)
```

---

### Étape 2 : Générer 80 minutes de vidéo

```powershell
.\cut_clips_random.ps1
```

**Ce que ça fait** :
- Découpe des clips de durée aléatoire (synchronisés au BPM 150)
- Réassemble aléatoirement pour faire 80 minutes
- Génère 1920x1080, 30fps, H.264, **sans piste audio** (le mix final n'a pas besoin de son — pensé pour être mixé/projeté avec sa propre source audio)

**Types de clips générés** (4/8/16/32 beats au tempo 150 BPM) :
```
4 beats   = 1.6s   (20% des clips)
8 beats   = 3.2s   (35% des clips)
16 beats  = 6.4s   (30% des clips)
32 beats  = 12.8s  (15% des clips)
```

- ⏱️ Durée : 30-45 minutes
- 📁 Sortie : `%USERPROFILE%\Videos\VHS-Glitch-Mix\edits\Projet_VHS_Glitch_ALL_poids\final_mix.mp4`

---

## 🎞️ Scripts Additionnels (Optionnels/Obsolètes)

- **`cut_clips_10s.ps1`** - Génère 60 min de clips 10s fixes (sans sync BPM) *(alternative pour source unique)*
- **`sanitize_video_names.ps1`** - Nettoie les noms manuellement *(déjà inclus dans le download)*
- **`add_glitch_effect.ps1`** - Effet glitch post-production *(en test, non recommandé)*

---

## 🔧 Configurations Disponibles

### Dans `cut_clips_random.ps1`

```powershell
$finalVideoDuration = 80        # Durée finale (minutes)
$bpm = 150                      # Tempo (beats par minute)
$skipStart = 5                  # Éviter début (secondes)
$skipEnd = 5                    # Éviter fin (secondes)
$width = 1920                   # Largeur vidéo
$height = 1080                  # Hauteur vidéo
$fps = 30                       # Framerate
```

### Poids des dossiers

```powershell
# $MixHome vient de resolve_tools.ps1 — %USERPROFILE%\Videos\VHS-Glitch-Mix par defaut
$sourceFolders = @(
    @{ path = Join-Path $downloadsDir "VHS_Glitch_Bank"; weight = 0.20 },
    @{ path = Join-Path $downloadsDir "Casual_Ravers - CARTOON"; weight = 0.35 },
    @{ path = Join-Path $downloadsDir "Casual_Ravers - GLITCH"; weight = 0.15 },
    @{ path = Join-Path $downloadsDir "Casual_Ravers - RANDOM"; weight = 0.30 }
)
```

---

## 🚀 Améliorations à Venir

### 1. Interface de Configuration Interactive ✅ Fait

> Implémenté dans `gui/` (Python + pywebview, voir la section "Interface Graphique" en haut de ce document et [CLAUDE.md](CLAUDE.md)). Formulaire complet (dossiers pondérés, types de clips, BPM, etc.), pas de menu `Out-GridView` — une vraie fenêtre desktop avec logs/progression en direct à la place.

**Objectif initial** : Remplacer la modification manuelle de fichiers PS1 par une **interface graphique** ou **menu interactif**.

**À configurer facilement** :

```
┌─────────────────────────────────────┐
│   VHS GLITCH GENERATOR CONFIG       │
├─────────────────────────────────────┤
│                                     │
│ 📁 Dossier de sortie                │
│    + AJOUTER UN DOSSIER             │
│                                     │
│ 📁 Dossier de sortie                │
│    C:\Users\vivie\Videos\Mix\edits\ │
│                                     │
│ ⏱️  Durée finale (min)              │
│    80                               │
│                                     │
│ 🎵 BPM voulu moyen                  │
│    150                              │
│                                     │
│ 📊 Poids des playlists séléctio...  │
│    ☑ VHS_Glitch_Bank       20%      │
│    ☑ CARTOON               35%      │
│    ☑ GLITCH                15%      │
│    ☑ RANDOM                30%      │
│                                     │
│ 🎬 Durée des clips                  │
│    ☑ 4beats   1.6s (20%)            │
│    ☑ 8beats   3.2s (35%)            │
│    ☑ 16beats  6.4s (30%)            │
│    ☑ 32beats 12.8s (15%)            │
│    + Ajouter une échantillonnage    │
│                                     │
│ [DÉMARRER] [ANNULER]                │
└─────────────────────────────────────┘
```

**Implémentation suggérée** :
- PowerShell WinForms ou `Out-GridView`
- Validation des entrées (BPM > 0, poids = 100%, durée > 10min)
- Présets sauvegardés (VHS Classic, Hardbounce, etc.)

---

### 2. Gestion des Téléchargements sans Stockage Local — toujours hors périmètre

> Non implémenté par la GUI actuelle : le téléchargement des playlists se fait toujours intégralement sur disque local (`config.json` → `download.baseDir`), comme avec les scripts `.ps1` d'origine. Les options streaming/cache/CDN ci-dessous restent des pistes futures.

**Problème actuel** : Les vidéos YouTube prennent ~50-100GB d'espace disque.

**Solutions possibles** :

#### Option A : Streaming direct (Recommandé)
```powershell
# Au lieu de télécharger et sauvegarder :
# ffmpeg -i "https://youtube.com/watch?v=XXX" -t 10s -f pipe:1 | ffmpeg -i pipe:0 ...

# Avantages :
# ✅ Pas de stockage disque
# ✅ Accès instantané aux playlists
# ❌ Nécessite bande passante constante pendant la génération
```

#### Option B : Cache temporaire + nettoyage auto
```powershell
# Télécharger temporairement dans C:\Temp\yt_cache\
# Générer les clips
# Supprimer auto après génération

# Avantages :
# ✅ Économise 90% d'espace disque
# ✅ Transparent pour l'utilisateur
# ❌ Plus lent (re-téléchargement si crash)
```

#### Option C : CDN / Cloud Storage
```powershell
# Utiliser Google Drive, AWS S3, ou Backblaze B2
# ffmpeg -i "https://drive.google.com/..." -t 10s

# Avantages :
# ✅ Pas d'espace disque local
# ✅ Playlists synchronisées globalement
# ❌ Complexe à implémenter
# ❌ Nécessite API credentials
```

**Recommendation** : Implémenter **Option B** (cache temporaire)

---

### 3. Proposition d'Architecture Améliorée ✅ Largement implémenté

> La structure réelle (`gui/` + `config.json` à la racine) suit cette proposition d'assez près — voir [CLAUDE.md](CLAUDE.md) pour le détail exact. Différences : Python plutôt que PowerShell pour la GUI, pas de dossier `presets/` (pas de présets sauvegardés pour l'instant), pas de `cleanup.ps1` séparé (nettoyage des clips temporaires via un bouton dans l'onglet Génération).

```
vhs-glitch-generator/
├── config.json
│   ├── outputFolder: "C:\Videos\Mix\edits"
│   ├── finalDuration: 80
│   ├── bpm: 150
│   ├── skipStart: 5
│   ├── skipEnd: 5
│   ├── sourceFolders: {...}
│   └── clipTypes: {...}
│
├── gui.ps1                    # Interface de config
├── download.ps1               # Avec cache temporaire
├── generate.ps1               # Génération vidéo
├── cleanup.ps1                # Nettoyer cache
│
└── presets/
    ├── vhs-classic.json
    ├── hardbounce.json
    └── glitch-extreme.json
```

---

### 4. Checklist des Améliorations

- [x] GUI avec formulaire de configuration *(Python + pywebview plutôt que PowerShell, voir `gui/`)*
- [x] Charger/sauvegarder configurations en JSON
- [ ] Implémenter cache temporaire pour YouTube — hors périmètre
- [x] Auto-nettoyage après génération *(bouton manuel dans l'onglet Génération, pas automatique)*
- [x] Barre de progression améliorée
- [ ] Export en plusieurs formats (MP4, WebM, ProRes) — hors périmètre
- [ ] Support des sous-titres/métadonnées — hors périmètre
- [ ] Multi-threading pour plus de vitesse — hors périmètre
- [ ] Logs détaillés en fichier — hors périmètre (logs affichés en direct dans la GUI, non persistés)
- [ ] Support de playlists Vimeo/autres — hors périmètre

---

## 🐛 Troubleshooting

### ❌ "Impossible de charger le fichier..."
```powershell
Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser
```

### ❌ "ffmpeg.exe" introuvable
Téléchargez depuis : https://ffmpeg.org/download.html

### ❌ "Aucune video trouvee"
```powershell
.\sanitize_video_names.ps1
```

### ❌ Le script prend trop longtemps
- Baissez la résolution (`$width = 1280, $height = 720`)
- Réduisez la durée finale (`$finalVideoDuration = 40`)

---

## 📊 Résumé Rapide

| Étape | Script | Durée |
|-------|--------|-------|
| 1️⃣ Télécharger | `sanitize_video_names.ps1` | 30-60 min |
| 2️⃣ Générer | `cut_clips_random.ps1` | 30-45 min |
| ✅ Résultat | `final_mix.mp4` | 80 min de vidéo |

**Temps total** : ~1h30 à 2h de traitement (ou via la GUI, voir en haut de ce document)

