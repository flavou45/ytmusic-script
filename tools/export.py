from pathlib import Path

from common.client import get_ytmusic
from common.config import EXPORT_DIR
from common.utils import resolve_playlist, track_row, write_csv, write_json


def cmd_export(args):
    yt = get_ytmusic()
    playlists = yt.get_library_playlists(limit=args.playlist_limit)
    playlist = resolve_playlist(yt, args.playlist, playlists)
    details = yt.get_playlist(playlist["playlistId"], limit=args.track_limit)
    tracks = details.get("tracks", [])

    output = Path(args.output) if args.output else EXPORT_DIR / f"{playlist['title']}.{args.format}"

    if args.format == "json":
        write_json(output, {"playlist": playlist, "details": details})
    elif args.format == "csv":
        rows = [track_row(playlist["title"], track) for track in tracks]
        write_csv(
            output,
            rows,
            ["playlist", "title", "artists", "album", "videoId", "setVideoId", "duration", "duration_seconds"],
        )
    else:
        lines = [f"# {playlist['title']}", ""]
        lines.extend(f"- {track_row(playlist['title'], track)['artists']} - {track.get('title', '')}" for track in tracks)
        output.parent.mkdir(parents=True, exist_ok=True)
        output.write_text("\n".join(lines), encoding="utf-8")

    print(f"Export terminé : {output}")
