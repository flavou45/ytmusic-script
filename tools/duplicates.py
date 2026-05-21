import time

from common.client import get_ytmusic

from common.config import get_ignore_playlists
from common.utils import chunked, confirm_or_exit, iter_selected_playlists, track_key, track_label


LIKED_MUSIC_TITLE = "Liked Music"


def cmd_duplicates(args):
    yt = get_ytmusic()
    ignored = set() if args.include_ignored else get_ignore_playlists()
    total_duplicates = 0
    removed = 0
    skipped = 0

    for playlist, details in iter_selected_playlists(yt, args.playlist, ignored, args.track_limit):
        seen = {}
        duplicates = []

        for track in details.get("tracks", []):
            key = track_key(track)
            if key in seen:
                duplicates.append(track)
            else:
                seen[key] = track

        if not duplicates:
            continue

        total_duplicates += len(duplicates)
        print(f"\n{playlist['title']} : {len(duplicates)} doublon(s)")
        for track in duplicates:
            print(f"  - {track_label(track)} [{track.get('videoId', 'sans videoId')}]")

        if args.apply:
            if playlist["title"] == LIKED_MUSIC_TITLE:
                unlikeable = [track for track in duplicates if track.get("videoId")]
                skipped += len(duplicates) - len(unlikeable)
                confirm_or_exit(args, f"{len(unlikeable)} doublon(s) vont être retirés des titres aimés.")
                for track in unlikeable:
                    yt.rate_song(track["videoId"], "INDIFFERENT")
                    removed += 1
                    time.sleep(args.pause)
            else:
                removable = [track for track in duplicates if track.get("videoId") and track.get("setVideoId")]
                skipped += len(duplicates) - len(removable)
                confirm_or_exit(args, f"{len(removable)} doublon(s) vont être supprimés de '{playlist['title']}'.")
                for batch in chunked(removable, args.batch_size):
                    yt.remove_playlist_items(playlist["playlistId"], batch)
                    removed += len(batch)
                    time.sleep(args.pause)

    if args.apply:
        print(f"\nTraitement terminé : {removed} doublon(s) nettoyé(s).")
        if skipped:
            print(f"{skipped} doublon(s) ignoré(s), car identifiant requis manquant.")
    else:
        print(f"\nDry-run : {total_duplicates} doublon(s) détecté(s). Ajoute --apply pour supprimer.")
