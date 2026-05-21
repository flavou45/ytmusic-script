from common.client import get_ytmusic
from common.config import get_ignore_playlists
from common.utils import iter_selected_playlists, track_label, write_csv


def cmd_clean_library(args):
    yt = get_ytmusic()
    ignored = set() if args.include_ignored else get_ignore_playlists()

    playlist_video_ids = set()
    for _, details in iter_selected_playlists(yt, args.playlist, ignored, args.track_limit):
        playlist_video_ids.update(track.get("videoId") for track in details.get("tracks", []) if track.get("videoId"))

    library_songs = yt.get_library_songs(limit=args.library_limit)
    orphan_songs = [
        song
        for song in library_songs
        if song.get("videoId") and song.get("videoId") not in playlist_video_ids
    ]

    print(f"Titres en bibliothèque : {len(library_songs)}")
    print(f"Titres présents dans les playlists analysées : {len(playlist_video_ids)}")
    print(f"Titres de bibliothèque hors playlists : {len(orphan_songs)}")

    for song in orphan_songs[:args.limit]:
        print(f"  - {track_label(song)} [{song.get('videoId')}]")

    if len(orphan_songs) > args.limit:
        print(f"  ... {len(orphan_songs) - args.limit} autre(s)")
        if not args.export_csv:
            print("Utilise --export-csv pour exporter la liste complète.")

    if args.export_csv:
        rows = [
            {
                "titre": track_label(song),
                "videoId": song.get("videoId") or "",
                "album": (song.get("album") or {}).get("name") or "",
            }
            for song in orphan_songs
        ]
        write_csv(args.export_csv, rows, ["titre", "videoId", "album"], delimiter=";")
        print(f"\nExport CSV terminé : {args.export_csv}")
