# YouTube Music Manager

Outil CLI pour gérer tes playlists YouTube Music avec `ytmusicapi`.

Les commandes qui modifient YouTube Music sont en dry-run par défaut. Ajoute `--apply` pour appliquer les changements, et `--yes` pour éviter la confirmation interactive.

## Installation

Ouvre PowerShell, va dans le dossier du projet, puis active l'environnement virtuel :

```powershell
cd D:\Dev\ytmusic-script
.\.venv\Scripts\Activate.ps1
```

Installe ensuite les dépendances dans le venv :

```powershell
python -m pip install -r requirements.txt
```

Tu peux vérifier que le CLI répond :

```powershell
python .\ytmusic_manager.py --help
```

Une fois le venv activé, lance les commandes avec `python` :

```powershell
python .\ytmusic_manager.py list
```

Si tu ne veux pas activer le venv, utilise directement le Python du venv :

```powershell
.\.venv\Scripts\python.exe .\ytmusic_manager.py --help
```

## Configuration

La configuration locale est dans `json/config.json`.

```json
{
  "ignore_playlists": ["Perso"],
  "playlist_limit": 1000,
  "track_limit": 5000,
  "library_limit": 10000,
  "batch_size": 50,
  "pause_seconds": 0.3
}
```

Les playlists dans `ignore_playlists` sont ignorées par défaut par les commandes globales. Ajoute `--include-ignored` pour les inclure.

## Commandes

### Lister les playlists

```powershell
.\.venv\Scripts\python.exe .\ytmusic_manager.py list
```

Liste les playlists, en filtrant toujours l'ignore list.

### Chercher un titre ou un artiste

```powershell
.\.venv\Scripts\python.exe .\ytmusic_manager.py search "daft punk"
.\.venv\Scripts\python.exe .\ytmusic_manager.py search "around the world" --field title
.\.venv\Scripts\python.exe .\ytmusic_manager.py search "daft punk" --field artist
.\.venv\Scripts\python.exe .\ytmusic_manager.py search "daft punk" --export-csv .\exports\search.csv
```

Affiche les morceaux trouvés et les playlists où ils apparaissent. Si un morceau est seulement dans la bibliothèque, il est affiché sous `Bibliothèque`. La commande `search` n'applique pas l'ignore list.

Par défaut, la recherche regarde `title`, `artist` et `album`. Tu peux répéter `--field` pour limiter les champs.

### Sauvegarder les playlists

```powershell
.\.venv\Scripts\python.exe .\ytmusic_manager.py backup
```

Crée un backup JSON dans `backups/<timestamp>/`.

Options utiles :

```powershell
.\.venv\Scripts\python.exe .\ytmusic_manager.py backup --include-ignored
.\.venv\Scripts\python.exe .\ytmusic_manager.py backup --output .\backups\manuel
```

### Restaurer une playlist

```powershell
.\.venv\Scripts\python.exe .\ytmusic_manager.py restore .\backups\20260521-200000\MaPlaylist.json
```

Dry-run par défaut. Pour créer réellement la playlist :

```powershell
.\.venv\Scripts\python.exe .\ytmusic_manager.py restore .\backups\20260521-200000\MaPlaylist.json --apply
```

### Exporter une playlist

```powershell
.\.venv\Scripts\python.exe .\ytmusic_manager.py export "Ma playlist" --format csv
.\.venv\Scripts\python.exe .\ytmusic_manager.py export "Ma playlist" --format json
.\.venv\Scripts\python.exe .\ytmusic_manager.py export "Ma playlist" --format md
```

Par défaut, les exports vont dans `exports/`.

### Détecter et supprimer les doublons

```powershell
.\.venv\Scripts\python.exe .\ytmusic_manager.py duplicates
.\.venv\Scripts\python.exe .\ytmusic_manager.py duplicates "Ma playlist"
```

Pour supprimer réellement les doublons :

```powershell
.\.venv\Scripts\python.exe .\ytmusic_manager.py duplicates "Ma playlist" --apply
```

Les titres sans `videoId` ou `setVideoId` sont listés mais pas supprimés.

Si la playlist est `Liked Music`, la commande ne supprime pas le morceau de la playlist : elle retire le J'aime avec YouTube Music.

### Lister les doublons entre playlists

```powershell
.\.venv\Scripts\python.exe .\ytmusic_manager.py cross-duplicates
.\.venv\Scripts\python.exe .\ytmusic_manager.py cross-duplicates --ignore "Liked Music"
.\.venv\Scripts\python.exe .\ytmusic_manager.py cross-duplicates --ignore "Liked Music" --ignore "Perso"
.\.venv\Scripts\python.exe .\ytmusic_manager.py cross-duplicates --playlist-file .\json\playlist_group.json
.\.venv\Scripts\python.exe .\ytmusic_manager.py cross-duplicates --export-csv
.\.venv\Scripts\python.exe .\ytmusic_manager.py cross-duplicates --export-csv .\exports\cross_duplicates.csv
```

Affiche chaque morceau présent dans plusieurs playlists, puis la liste des playlists concernées.

Le fichier `--playlist-file` peut être une liste :

```json
[
  "Playlist A",
  "Playlist B",
  "PLxxxxxxxx"
]
```

Ou un objet :

```json
{
  "playlists": [
    "Playlist A",
    "Playlist B",
    "PLxxxxxxxx"
  ]
}
```

Si `json/playlist_cross_duplicate.json` existe, `cross-duplicates` l'utilise automatiquement quand `--playlist-file` n'est pas fourni.

Le CSV exporté contient deux colonnes :

```csv
titre;playlists
Artist - Song;Playlist A|Playlist B|Playlist C
```

Le fichier est écrit en UTF-8 avec BOM et utilise `;` comme séparateur de colonnes, pour s'ouvrir proprement dans Excel. Dans la colonne `playlists`, les playlists sont séparées par `|`.

Pour nettoyer, édite la colonne `playlists` et laisse seulement les playlists où le morceau doit rester. Ensuite lance l'import :

```powershell
.\.venv\Scripts\python.exe .\ytmusic_manager.py cross-duplicates --import-csv .\exports\cross_duplicates.csv
```

L'import est en dry-run par défaut. Pour supprimer réellement le morceau des playlists qui ne sont plus présentes dans la colonne `playlists` :

```powershell
.\.venv\Scripts\python.exe .\ytmusic_manager.py cross-duplicates --import-csv .\exports\cross_duplicates.csv --apply
```

Si la playlist à nettoyer est `Liked Music`, la commande ne supprime pas le morceau de la playlist : elle retire le J'aime avec YouTube Music.

Cette commande respecte `json/config.json` par défaut. `--ignore` permet d'ignorer des playlists uniquement pour cet appel, sans modifier la config.

### Synchroniser playlists vers bibliothèque

```powershell
.\.venv\Scripts\python.exe .\ytmusic_manager.py sync-library
.\.venv\Scripts\python.exe .\ytmusic_manager.py sync-library "Ma playlist"
```

Pour ajouter réellement les titres absents à la bibliothèque :

```powershell
.\.venv\Scripts\python.exe .\ytmusic_manager.py sync-library --apply
```

### Fusionner des playlists

Vers une playlist existante :

```powershell
.\.venv\Scripts\python.exe .\ytmusic_manager.py merge --source "Playlist A" --source "Playlist B" --target "Fusion"
```

Créer une nouvelle playlist cible :

```powershell
.\.venv\Scripts\python.exe .\ytmusic_manager.py merge --source "Playlist A" --source "Playlist B" --target "Fusion" --create-target --apply
```

### Copier une playlist

```powershell
.\.venv\Scripts\python.exe .\ytmusic_manager.py copy "Ma playlist" --title "Ma playlist - copie"
```

Pour créer réellement la copie :

```powershell
.\.venv\Scripts\python.exe .\ytmusic_manager.py copy "Ma playlist" --title "Ma playlist - copie" --apply
```

### Comparer deux playlists

```powershell
.\.venv\Scripts\python.exe .\ytmusic_manager.py compare "Playlist A" "Playlist B"
.\.venv\Scripts\python.exe .\ytmusic_manager.py compare "Playlist A" "Playlist B" --show
```

Affiche les titres communs et les titres présents uniquement dans chaque playlist.

### Rechercher les morceaux manquants

```powershell
.\.venv\Scripts\python.exe .\ytmusic_manager.py missing
.\.venv\Scripts\python.exe .\ytmusic_manager.py missing --search
```

`--search` propose des remplaçants possibles depuis YouTube Music.

### Ajouter des remplaçants aux morceaux manquants

```powershell
.\.venv\Scripts\python.exe .\ytmusic_manager.py recommend-missing
```

Pour ajouter réellement les remplaçants proposés aux playlists :

```powershell
.\.venv\Scripts\python.exe .\ytmusic_manager.py recommend-missing --apply
```

Pour remplacer les morceaux manquants quand c'est possible, ajoute `--replace`. La commande ajoute le remplaçant puis supprime l'ancien morceau si `videoId` et `setVideoId` sont disponibles :

```powershell
.\.venv\Scripts\python.exe .\ytmusic_manager.py recommend-missing --replace --apply
```

### Statistiques

```powershell
.\.venv\Scripts\python.exe .\ytmusic_manager.py stats
.\.venv\Scripts\python.exe .\ytmusic_manager.py stats --top 20
```

Affiche le nombre de playlists, titres en playlists, titres en bibliothèque, titres uniquement en bibliothèque, doublons globaux, durée cumulée, artistes et albums les plus présents.

### Titres de bibliothèque hors playlists

```powershell
.\.venv\Scripts\python.exe .\ytmusic_manager.py clean-library
.\.venv\Scripts\python.exe .\ytmusic_manager.py clean-library --export-csv
.\.venv\Scripts\python.exe .\ytmusic_manager.py clean-library --export-csv .\exports\clean_library.csv
```

Liste les titres présents dans la bibliothèque mais absents des playlists analysées.

Si la liste est plus longue que `--limit`, l'affichage est tronqué. `--export-csv` exporte la liste complète dans un CSV compatible Excel.

### Renommer une playlist

```powershell
.\.venv\Scripts\python.exe .\ytmusic_manager.py rename "Ancien nom" "Nouveau nom"
```

Pour renommer réellement :

```powershell
.\.venv\Scripts\python.exe .\ytmusic_manager.py rename "Ancien nom" "Nouveau nom" --apply
```

### Audit global

```powershell
.\.venv\Scripts\python.exe .\ytmusic_manager.py audit
.\.venv\Scripts\python.exe .\ytmusic_manager.py audit --details
```

Rapport global : nombre de playlists, titres en playlists, titres en bibliothèque, titres uniquement en bibliothèque, doublons, morceaux manquants, ignore list et backups récents.

### Gérer la config

```powershell
.\.venv\Scripts\python.exe .\ytmusic_manager.py config init
.\.venv\Scripts\python.exe .\ytmusic_manager.py config show
.\.venv\Scripts\python.exe .\ytmusic_manager.py config reset
.\.venv\Scripts\python.exe .\ytmusic_manager.py config ignore-add "Ma playlist"
.\.venv\Scripts\python.exe .\ytmusic_manager.py config ignore-remove "Ma playlist"
```

## Options communes

`--include-ignored` inclut les playlists de `json/config.json`.

`--track-limit` limite le nombre de titres chargés par playlist.

`--playlist-limit` limite le nombre de playlists chargées.

`--apply` applique réellement une modification.

`--yes` saute la confirmation interactive.
