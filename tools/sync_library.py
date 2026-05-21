import time

from common.client import get_ytmusic

from common.config import get_ignore_playlists
from common.utils import iter_selected_playlists, track_label


def cmd_sync_library(args):
    yt = get_ytmusic()
    ignore = set() if args.include_ignored else get_ignore_playlists(args.ignore)

    print("Chargement des titres déjà en bibliothèque...")
    library_songs = yt.get_library_songs(limit=args.library_limit)
    library_video_ids = {song.get("videoId") for song in library_songs if song.get("videoId")}
    print(f"{len(library_video_ids)} titres déjà en bibliothèque")

    added = 0
    candidates = 0

    for playlist, details in iter_selected_playlists(yt, args.playlist, ignore, args.track_limit):
        print(f"\nTraitement playlist : {playlist['title']}")
        for track in details.get("tracks", []):
            video_id = track.get("videoId")
            if not video_id or video_id in library_video_ids:
                continue

            add_token = (track.get("feedbackTokens") or {}).get("add")
            if not add_token:
                print(f"  Impossible d'ajouter : {track_label(track)} - pas de token")
                continue

            candidates += 1
            if args.apply:
                yt.edit_song_library_status([add_token])
                library_video_ids.add(video_id)
                added += 1
                print(f"  Ajouté : {track_label(track)}")
                time.sleep(args.pause)
            else:
                print(f"  À ajouter : {track_label(track)}")

    if args.apply:
        print(f"\nSynchronisation terminée : {added} titre(s) ajouté(s).")
    else:
        print(f"\nDry-run : {candidates} titre(s) à ajouter. Ajoute --apply pour synchroniser.")
