import csv
import json
from pathlib import Path


def artists_label(track):
    artists = track.get("artists") or []
    names = [artist.get("name") for artist in artists if artist.get("name")]
    return ", ".join(names)


def track_label(track):
    artist = artists_label(track)
    title = track.get("title") or "Titre inconnu"
    return f"{artist} - {title}" if artist else title


def track_key(track):
    video_id = track.get("videoId")
    if video_id:
        return f"video:{video_id}"

    title = (track.get("title") or "").casefold().strip()
    artist = artists_label(track).casefold().strip()
    album = ((track.get("album") or {}).get("name") or "").casefold().strip()
    return f"meta:{artist}|{title}|{album}"


def resolve_playlist(yt, selector, playlists=None):
    playlists = playlists or yt.get_library_playlists(limit=1000)

    for playlist in playlists:
        if selector == playlist.get("playlistId") or selector == playlist.get("title"):
            return playlist

    lowered = selector.casefold()
    matches = [p for p in playlists if lowered in (p.get("title") or "").casefold()]
    if len(matches) == 1:
        return matches[0]
    if len(matches) > 1:
        names = ", ".join(p.get("title", "?") for p in matches)
        raise SystemExit(f"Plusieurs playlists correspondent à '{selector}' : {names}")

    raise SystemExit(f"Playlist introuvable : {selector}")


def load_playlist_details(yt, playlist, limit):
    return yt.get_playlist(playlist["playlistId"], limit=limit)


def iter_selected_playlists(yt, selectors, ignore, limit):
    playlists = yt.get_library_playlists(limit=1000)
    if selectors:
        selected = [resolve_playlist(yt, selector, playlists) for selector in selectors]
    else:
        selected = [playlist for playlist in playlists if playlist.get("title") not in ignore]

    for playlist in selected:
        try:
            yield playlist, load_playlist_details(yt, playlist, limit)
        except Exception as exc:
            print(f"Erreur chargement playlist {playlist.get('title', '?')} => {exc}")


def chunked(items, size):
    for index in range(0, len(items), size):
        yield items[index:index + size]


def video_ids_from_tracks(tracks):
    return [track.get("videoId") for track in tracks if track.get("videoId")]


def unique_video_ids(tracks, existing=None):
    seen = set(existing or [])
    result = []
    for track in tracks:
        video_id = track.get("videoId")
        if video_id and video_id not in seen:
            seen.add(video_id)
            result.append(video_id)
    return result


def confirm_or_exit(args, message):
    if not getattr(args, "apply", False):
        return
    if getattr(args, "yes", False):
        return

    answer = input(f"{message} Tape 'oui' pour continuer : ").strip().casefold()
    if answer != "oui":
        raise SystemExit("Annulé.")


def write_json(path, payload):
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, ensure_ascii=False, indent=2), encoding="utf-8")


def write_csv(path, rows, fieldnames, delimiter=","):
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8-sig", newline="") as file:
        writer = csv.DictWriter(file, fieldnames=fieldnames, delimiter=delimiter)
        writer.writeheader()
        writer.writerows(rows)


def track_row(playlist_title, track):
    album = track.get("album") or {}
    return {
        "playlist": playlist_title,
        "title": track.get("title") or "",
        "artists": artists_label(track),
        "album": album.get("name") or "",
        "videoId": track.get("videoId") or "",
        "setVideoId": track.get("setVideoId") or "",
        "duration": track.get("duration") or "",
        "duration_seconds": track.get("duration_seconds") or "",
    }
