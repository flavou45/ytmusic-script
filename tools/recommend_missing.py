import time

from common.client import get_ytmusic
from common.config import get_ignore_playlists
from common.utils import confirm_or_exit, iter_selected_playlists, track_label


def cmd_recommend_missing(args):
    yt = get_ytmusic()
    ignored = set() if args.include_ignored else get_ignore_playlists()
    replacements = []

    for playlist, details in iter_selected_playlists(yt, args.playlist, ignored, args.track_limit):
        for track in details.get("tracks", []):
            unavailable = track.get("isAvailable") is False
            if track.get("videoId") and not unavailable:
                continue

            query = track_label(track)
            results = yt.search(query, filter="songs", limit=args.search_limit)
            candidate = next((result for result in results if result.get("videoId")), None)
            print(f"\n{playlist['title']} : {query}")
            if candidate:
                print(f"  -> {track_label(candidate)} [{candidate.get('videoId')}]")
                replacements.append((playlist, track, candidate))
            else:
                print("  -> Aucun remplaçant trouvé")

    print(f"\n{len(replacements)} remplaçant(s) proposé(s).")
    if not args.apply:
        action = "remplacer les morceaux manquants" if args.replace else "ajouter les remplaçants aux playlists"
        print(f"Dry-run : ajoute --apply pour {action}.")
        return

    action = "ajoutés puis les anciens morceaux supprimés" if args.replace else "ajoutés"
    confirm_or_exit(args, f"{len(replacements)} remplaçant(s) vont être {action}.")

    removed = 0
    not_removable = 0
    for playlist, old_track, candidate in replacements:
        yt.add_playlist_items(playlist["playlistId"], [candidate["videoId"]], duplicates=False)
        time.sleep(args.pause)

        if args.replace:
            if old_track.get("videoId") and old_track.get("setVideoId"):
                yt.remove_playlist_items(playlist["playlistId"], [old_track])
                removed += 1
                time.sleep(args.pause)
            else:
                not_removable += 1

    if args.replace:
        print(f"Remplacement terminé : {removed} ancien(s) morceau(x) supprimé(s).")
        if not_removable:
            print(f"{not_removable} ancien(s) morceau(x) non supprimé(s), car videoId ou setVideoId manquant.")
    else:
        print("Ajout des remplaçants terminé.")
