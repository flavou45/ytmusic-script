from collections import defaultdict

from common.client import get_ytmusic
from common.utils import iter_selected_playlists, track_key, track_label, write_csv


def matches_query(track, query, fields):
    query = query.casefold()
    values = []

    if "title" in fields:
        values.append(track.get("title") or "")
    if "artist" in fields:
        values.extend(artist.get("name") or "" for artist in track.get("artists") or [])
    if "album" in fields:
        values.append((track.get("album") or {}).get("name") or "")

    return any(query in value.casefold() for value in values)


def cmd_search(args):
    yt = get_ytmusic()
    ignored = set()
    fields = set(args.field)
    matches = {}
    playlists_by_key = defaultdict(list)

    for playlist, details in iter_selected_playlists(yt, args.playlist, ignored, args.track_limit):
        for track in details.get("tracks", []):
            if not matches_query(track, args.query, fields):
                continue

            key = track_key(track)
            matches.setdefault(key, track)
            playlists_by_key[key].append(playlist["title"])

    library_songs = yt.get_library_songs(limit=args.library_limit)
    for track in library_songs:
        if not matches_query(track, args.query, fields):
            continue

        key = track_key(track)
        matches.setdefault(key, track)
        if not playlists_by_key[key]:
            playlists_by_key[key].append("Bibliothèque")

    print(f"Résultats : {len(matches)} morceau(x)")

    rows = []
    for key, track in sorted(matches.items(), key=lambda item: track_label(item[1]).casefold()):
        playlists = sorted(set(playlists_by_key[key]))
        label = track_label(track)
        print(f"\n{label}")
        for playlist_title in playlists:
            print(f"  - {playlist_title}")

        rows.append(
            {
                "titre": label,
                "playlists": "|".join(playlists),
                "videoId": track.get("videoId") or "",
            }
        )

    if args.export_csv:
        write_csv(args.export_csv, rows, ["titre", "playlists", "videoId"], delimiter=";")
        print(f"\nExport CSV terminé : {args.export_csv}")
