import time

from common.client import get_ytmusic
from common.utils import chunked, confirm_or_exit, resolve_playlist, unique_video_ids


def cmd_copy(args):
    yt = get_ytmusic()
    playlists = yt.get_library_playlists(limit=args.playlist_limit)
    source = resolve_playlist(yt, args.source, playlists)
    details = yt.get_playlist(source["playlistId"], limit=args.track_limit)
    video_ids = unique_video_ids(details.get("tracks", []))
    title = args.title or f"{source['title']} - copie"

    print(f"Copie : {source['title']} -> {title}")
    print(f"{len(video_ids)} titre(s) unique(s)")

    if not args.apply:
        print("Dry-run : ajoute --apply pour créer la copie.")
        return

    confirm_or_exit(args, f"La playlist '{title}' va être créée avec {len(video_ids)} titre(s).")
    playlist_id = yt.create_playlist(title, args.description, args.privacy)
    for batch in chunked(video_ids, args.batch_size):
        yt.add_playlist_items(playlist_id, batch, duplicates=False)
        time.sleep(args.pause)

    print(f"Copie créée : {title} - {playlist_id}")
