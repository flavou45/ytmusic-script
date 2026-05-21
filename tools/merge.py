import time

from common.client import get_ytmusic

from common.config import get_ignore_playlists
from common.utils import chunked, confirm_or_exit, resolve_playlist


def cmd_merge(args):
    yt = get_ytmusic()
    ignored = set() if args.include_ignored else get_ignore_playlists()
    playlists = [
        playlist
        for playlist in yt.get_library_playlists(limit=args.playlist_limit)
        if playlist.get("title") not in ignored
    ]
    sources = [resolve_playlist(yt, selector, playlists) for selector in args.source]

    if args.create_target:
        if not args.apply:
            print(f"Dry-run : création prévue de la playlist '{args.target}'.")
            target = {"title": args.target, "playlistId": None}
            target_existing_ids = set()
        else:
            playlist_id = yt.create_playlist(args.target, args.description, args.privacy)
            target = {"title": args.target, "playlistId": playlist_id}
            target_existing_ids = set()
            print(f"Playlist créée : {args.target} - {playlist_id}")
    else:
        target = resolve_playlist(yt, args.target, playlists)
        target_details = yt.get_playlist(target["playlistId"], limit=args.track_limit)
        target_existing_ids = {
            track.get("videoId") for track in target_details.get("tracks", []) if track.get("videoId")
        }

    to_add = []
    seen = set(target_existing_ids)

    for source in sources:
        details = yt.get_playlist(source["playlistId"], limit=args.track_limit)
        print(f"Source : {source['title']} ({len(details.get('tracks', []))} titres)")
        for track in details.get("tracks", []):
            video_id = track.get("videoId")
            if video_id and video_id not in seen:
                seen.add(video_id)
                to_add.append(video_id)

    print(f"\nFusion vers '{target['title']}' : {len(to_add)} titre(s) unique(s) à ajouter.")
    if not args.apply:
        print("Dry-run : ajoute --apply pour modifier la playlist.")
        return

    confirm_or_exit(args, f"{len(to_add)} titre(s) vont être ajoutés à '{target['title']}'.")
    for batch in chunked(to_add, args.batch_size):
        yt.add_playlist_items(target["playlistId"], batch, duplicates=False)
        time.sleep(args.pause)
    print("Fusion terminée.")
