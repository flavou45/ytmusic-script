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
    playlist_video_ids = set()

    for playlist, details in playlists:
        seen = set()
        for track in details.get("tracks", []):
            total_tracks += 1
            key = track_key(track)
            global_counter[key] += 1
            if track.get("videoId"):
                playlist_video_ids.add(track["videoId"])
            if key in seen:
                duplicate_rows.append((playlist["title"], track))
            seen.add(key)
            if not track.get("videoId") or track.get("isAvailable") is False:
                missing.append((playlist["title"], track))

    library_songs = yt.get_library_songs(limit=args.library_limit)
    library_only_tracks = [
        song
        for song in library_songs
        if song.get("videoId") and song.get("videoId") not in playlist_video_ids
    ]
    global_duplicates = sum(count - 1 for count in global_counter.values() if count > 1)

    print("Audit YouTube Music")
    print(f"Playlists analysées : {len(playlists)}")
    print(f"Titres analysés en playlists : {total_tracks}")
    print(f"Titres en bibliothèque : {len(library_songs)}")
    print(f"Titres uniquement en bibliothèque : {len(library_only_tracks)}")
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

        print("\nTitres uniquement en bibliothèque :")
        for track in library_only_tracks[:args.limit]:
            print(f"  - {track_label(track)}")
