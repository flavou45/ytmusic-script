from common.client import get_ytmusic
from common.config import get_ignore_playlists


def cmd_list(args):
    yt = get_ytmusic()
    ignored = get_ignore_playlists()
    playlists = yt.get_library_playlists(limit=args.limit)
    for playlist in playlists:
        if playlist.get("title") in ignored:
            continue

        count = playlist.get("count")
        suffix = f" ({count} titres)" if count is not None else ""
        print(f"{playlist.get('title', '?')}{suffix} - {playlist.get('playlistId')}")
