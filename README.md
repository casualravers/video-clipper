# 🎬 VHS Glitch Video Generator - Guide d'utilisation

Guide complet pour générer des vidéos VHS Glitch randomisées avec PowerShell et FFmpeg.

---

## ⚙️ Installation & Setup

### Prérequis

- **FFmpeg** : `ffmpeg-8.0.1-essentials_build` installé à `C:\Users\vivie\Videos\Mix\`
- **yt-dlp** : `yt-dlp.exe` dans `C:\Users\vivie\Videos\Mix\`
- **PowerShell** : Version 5.0 ou supérieure

### Configuration PowerShell

Si vous avez une erreur d'exécution de scripts, lancez ceci UNE SEULE FOIS :

```powershell
Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser
```

Répondez **Y** (Yes).

---

## 🚀 Démarrage Rapide

### Étape 1 : Télécharger les playlists

```powershell
.\download_playlists_480p.ps1
```

**Ce que ça fait** :
- Télécharge 4 playlists YouTube en 480p
- Crée les dossiers automatiquement
- Nettoie les noms (accents, caractères spéciaux)
- ⏱️ Durée : 30-60 minutes

**Playlists téléchargées** :
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
- Génère 1920x1080, 30fps, H.264

**Types de clips générés** (4/8/16/32 beats au tempo 150 BPM) :
```
4 beats   = 1.6s   (20% des clips)
8 beats   = 3.2s   (35% des clips)
16 beats  = 6.4s   (30% des clips)
32 beats  = 12.8s  (15% des clips)
```

- ⏱️ Durée : 30-45 minutes
- 📁 Sortie : `C:\Users\vivie\Videos\Mix\edits\Projet_VHS_Glitch_ALL_poids\final_mix.mp4`

---

## 🎞️ Scripts Additionnels (Optionnels/Obsolètes)

- **`cut_clips_random_10s.ps1`** - Génère 60 min de clips 10s fixes (sans sync BPM) *(alternative pour source unique)*
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
$sourceFolders = @(
    @{ path = "C:\Users\vivie\Videos\Mix\VHS_Glitch_Bank"; weight = 0.20 },
    @{ path = "C:\Users\vivie\Videos\Mix\Casual_Ravers - CARTOON"; weight = 0.35 },
    @{ path = "C:\Users\vivie\Videos\Mix\Casual_Ravers - GLITCH"; weight = 0.15 },
    @{ path = "C:\Users\vivie\Videos\Mix\Casual_Ravers - RANDOM"; weight = 0.30 }
)
```

---

## 🚀 Améliorations à Venir

### 1. Interface de Configuration Interactive

**Objectif** : Remplacer la modification manuelle de fichiers PS1 par une **interface graphique** ou **menu interactif**.

**À configurer facilement** :

```
┌─────────────────────────────────────┐
│   VHS GLITCH GENERATOR CONFIG       │
├─────────────────────────────────────┤
│                                     │
│ 📁 Dossier de sortie                │
│    C:\Users\vivie\Videos\Mix\edits\ │
│                                     │
│ ⏱️  Durée finale (min)              │
│    80                               │
│                                     │
│ 🎵 BPM                              │
│    150                              │
│                                     │
│ 📊 Poids des playlists              │
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
│                                     │
│ [DÉMARRER] [ANNULER]                │
└─────────────────────────────────────┘
```

**Implémentation suggérée** :
- PowerShell WinForms ou `Out-GridView`
- Validation des entrées (BPM > 0, poids = 100%, durée > 10min)
- Présets sauvegardés (VHS Classic, Hardbounce, etc.)

---

### 2. Gestion des Téléchargements sans Stockage Local

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

### 3. Proposition d'Architecture Améliorée

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

- [ ] GUI PowerShell avec formulaire de configuration
- [ ] Charger/sauvegarder configurations en JSON
- [ ] Implémenter cache temporaire pour YouTube
- [ ] Auto-nettoyage après génération
- [ ] Barre de progression améliorée
- [ ] Export en plusieurs formats (MP4, WebM, ProRes)
- [ ] Support des sous-titres/métadonnées
- [ ] Multi-threading pour plus de vitesse
- [ ] Logs détaillés en fichier
- [ ] Support de playlists Vimeo/autres

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
| 1️⃣ Télécharger | `download_playlists_480p.ps1` | 30-60 min |
| 2️⃣ Générer | `cut_clips_random.ps1` | 30-45 min |
| ✅ Résultat | `final_mix.mp4` | 80 min de vidéo |

**Temps total** : ~1h30 à 2h de traitement

---

## 🎯 Prochaine Étape

Voulez-vous que je développe :
1. **GUI de configuration** (PowerShell WinForms)
2. **Cache temporaire** (téléchargement intelligent)
3. **Export de presets** (sauvegarder vos configs)
4. **Autre** ?

