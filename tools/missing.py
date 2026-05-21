from common.client import get_ytmusic

from common.config import get_ignore_playlists
from common.utils import iter_selected_playlists, track_label


def cmd_missing(args):
    yt = get_ytmusic()
    ignored = set() if args.include_ignored else get_ignore_playlists()
    missing = []

    for playlist, details in iter_selected_playlists(yt, args.playlist, ignored, args.track_limit):
        for track in details.get("tracks", []):
            unavailable = track.get("isAvailable") is False
            if not track.get("videoId") or unavailable:
                missing.append((playlist["title"], track))

    if not missing:
        print("Aucun morceau manquant détecté.")
        return

    for playlist_title, track in missing:
        query = track_label(track)
        print(f"\n{playlist_title} : {query}")
        if args.search:
            try:
                results = yt.search(query, filter="songs", limit=args.search_limit)
            except Exception as exc:
                print(f"  Recherche impossible => {exc}")
                continue

            for result in results[:args.search_limit]:
                print(f"  -> {track_label(result)} [{result.get('videoId', 'sans videoId')}]")

    print(f"\n{len(missing)} morceau(x) manquant(s) ou indisponible(s).")
