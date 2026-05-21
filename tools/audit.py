from collections import Counter

from common.client import get_ytmusic
from common.config import BACKUP_DIR, get_ignore_playlists
from common.utils import iter_selected_playlists, track_key, track_label


def cmd_audit(args):
    yt = get_ytmusic()
    ignored = set() if args.include_ignored else get_ignore_playlists()
    playlists = list(iter_selected_playlists(yt, args.playlist, ignored, args.track_limit))

    total_tracks = 0
    missing = []
    duplicate_rows = []
    global_counter = Counter()

    for playlist, details in playlists:
        seen = set()
        for track in details.get("tracks", []):
            total_tracks += 1
            key = track_key(track)
            global_counter[key] += 1
            if key in seen:
                duplicate_rows.append((playlist["title"], track))
            seen.add(key)
            if not track.get("videoId") or track.get("isAvailable") is False:
                missing.append((playlist["title"], track))

    global_duplicates = sum(count - 1 for count in global_counter.values() if count > 1)

    print("Audit YouTube Music")
    print(f"Playlists analysées : {len(playlists)}")
    print(f"Titres analysés : {total_tracks}")
    print(f"Doublons dans une même playlist : {len(duplicate_rows)}")
    print(f"Doublons globaux entre playlists : {global_duplicates}")
    print(f"Morceaux manquants ou indisponibles : {len(missing)}")
    print(f"Playlists ignorées : {', '.join(sorted(ignored)) if ignored else 'aucune'}")

    if BACKUP_DIR.exists():
        backups = sorted(
            [path for path in BACKUP_DIR.iterdir() if path.is_dir()],
            key=lambda path: path.stat().st_mtime,
            reverse=True,
        )
        print("Backups récents :")
        for path in backups[:5]:
            print(f"  - {path.name}")
    else:
        print("Backups récents : aucun")

    if args.details:
        print("\nDoublons dans une même playlist :")
        for playlist_title, track in duplicate_rows[:args.limit]:
            print(f"  - {playlist_title} : {track_label(track)}")

        print("\nMorceaux manquants :")
        for playlist_title, track in missing[:args.limit]:
            print(f"  - {playlist_title} : {track_label(track)}")
