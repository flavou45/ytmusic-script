from collections import Counter

from common.client import get_ytmusic

from common.config import get_ignore_playlists
from common.utils import iter_selected_playlists


def cmd_stats(args):
    yt = get_ytmusic()
    ignored = set() if args.include_ignored else get_ignore_playlists()
    playlists = list(iter_selected_playlists(yt, args.playlist, ignored, args.track_limit))
    all_tracks = []
    playlist_sizes = []

    for playlist, details in playlists:
        tracks = details.get("tracks", [])
        all_tracks.extend(tracks)
        playlist_sizes.append((playlist["title"], len(tracks)))

    video_ids = [track.get("videoId") for track in all_tracks if track.get("videoId")]
    artists = Counter()
    albums = Counter()
    durations = 0

    for track in all_tracks:
        for artist in track.get("artists") or []:
            if artist.get("name"):
                artists[artist["name"]] += 1
        album_name = (track.get("album") or {}).get("name")
        if album_name:
            albums[album_name] += 1
        durations += track.get("duration_seconds") or 0

    duplicate_count = len(video_ids) - len(set(video_ids))
    hours = durations / 3600 if durations else 0

    print(f"Playlists analysées : {len(playlists)}")
    print(f"Titres au total : {len(all_tracks)}")
    print(f"Titres uniques : {len(set(video_ids))}")
    print(f"Doublons globaux : {duplicate_count}")
    if durations:
        print(f"Durée cumulée : {hours:.1f} h")

    print("\nPlus grosses playlists :")
    for title, count in sorted(playlist_sizes, key=lambda item: item[1], reverse=True)[:args.top]:
        print(f"  {count:4d} - {title}")

    print("\nArtistes les plus présents :")
    for name, count in artists.most_common(args.top):
        print(f"  {count:4d} - {name}")

    print("\nAlbums les plus présents :")
    for name, count in albums.most_common(args.top):
        print(f"  {count:4d} - {name}")
