from common.client import get_ytmusic
from common.utils import resolve_playlist, track_label, track_key


def _track_map(details):
    result = {}
    for track in details.get("tracks", []):
        result.setdefault(track_key(track), track)
    return result


def cmd_compare(args):
    yt = get_ytmusic()
    playlists = yt.get_library_playlists(limit=args.playlist_limit)
    left = resolve_playlist(yt, args.left, playlists)
    right = resolve_playlist(yt, args.right, playlists)

    left_tracks = _track_map(yt.get_playlist(left["playlistId"], limit=args.track_limit))
    right_tracks = _track_map(yt.get_playlist(right["playlistId"], limit=args.track_limit))

    left_keys = set(left_tracks)
    right_keys = set(right_tracks)
    only_left = sorted(left_keys - right_keys)
    only_right = sorted(right_keys - left_keys)
    common = sorted(left_keys & right_keys)

    print(f"{left['title']} : {len(left_keys)} titre(s)")
    print(f"{right['title']} : {len(right_keys)} titre(s)")
    print(f"En commun : {len(common)}")
    print(f"Seulement dans {left['title']} : {len(only_left)}")
    print(f"Seulement dans {right['title']} : {len(only_right)}")

    if args.show:
        print(f"\nSeulement dans {left['title']} :")
        for key in only_left:
            print(f"  - {track_label(left_tracks[key])}")

        print(f"\nSeulement dans {right['title']} :")
        for key in only_right:
            print(f"  - {track_label(right_tracks[key])}")
