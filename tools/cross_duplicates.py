import csv
import json
from collections import defaultdict
from pathlib import Path

from common.client import get_ytmusic
from common.config import JSON_DIR, get_ignore_playlists
from common.utils import chunked, confirm_or_exit, iter_selected_playlists, track_key, track_label


DEFAULT_PLAYLIST_FILE = JSON_DIR / "playlist_cross_duplicate.json"


def load_playlist_selectors(path):
    payload = json.loads(Path(path).read_text(encoding="utf-8"))
    if isinstance(payload, list):
        playlists = payload
    elif isinstance(payload, dict):
        playlists = payload.get("playlists")
    else:
        playlists = None

    if not isinstance(playlists, list) or not all(isinstance(item, str) for item in playlists):
        raise SystemExit(
            "Le fichier JSON doit contenir une liste de playlists "
            'ou un objet {"playlists": ["Nom ou ID", "..."]}.'
        )

    return playlists


def load_cleanup_csv(path):
    rows = {}
    with Path(path).open("r", encoding="utf-8-sig", newline="") as file:
        sample = file.read(2048)
        file.seek(0)
        dialect = csv.Sniffer().sniff(sample, delimiters=";,") if sample else csv.excel
        reader = csv.DictReader(file, dialect=dialect)
        if not reader.fieldnames or "titre" not in reader.fieldnames or "playlists" not in reader.fieldnames:
            raise SystemExit("Le CSV doit contenir les colonnes 'titre' et 'playlists'.")

        for row in reader:
            title = (row.get("titre") or "").strip()
            playlists = {
                playlist.strip()
                for playlist in (row.get("playlists") or "").split("|")
                if playlist.strip()
            }
            if title:
                rows[title] = playlists

    return rows


def export_duplicates_csv(path, duplicates, labels_by_key):
    output = Path(path)
    output.parent.mkdir(parents=True, exist_ok=True)
    with output.open("w", encoding="utf-8-sig", newline="") as file:
        writer = csv.DictWriter(file, fieldnames=["titre", "playlists"], delimiter=";")
        writer.writeheader()
        for key, entries in sorted(duplicates.items(), key=lambda item: labels_by_key[item[0]].casefold()):
            playlist_titles = sorted({entry["playlist_title"] for entry in entries})
            writer.writerow(
                {
                    "titre": labels_by_key[key],
                    "playlists": "|".join(playlist_titles),
                }
            )

    print(f"\nExport CSV terminé : {output}")


def clean_from_csv(yt, args, duplicates, labels_by_key):
    wanted_playlists_by_title = load_cleanup_csv(args.import_csv)
    removals_by_playlist = defaultdict(list)
    missing_titles = set(wanted_playlists_by_title)

    for key, entries in duplicates.items():
        title = labels_by_key[key]
        wanted_playlists = wanted_playlists_by_title.get(title)
        if wanted_playlists is None:
            continue

        missing_titles.discard(title)
        for entry in entries:
            if entry["playlist_title"] not in wanted_playlists:
                track = entry["track"]
                if track.get("videoId") and track.get("setVideoId"):
                    removals_by_playlist[entry["playlist_id"]].append(track)

    removal_count = sum(len(tracks) for tracks in removals_by_playlist.values())
    print(f"\nNettoyage CSV : {removal_count} suppression(s) prévue(s).")
    if missing_titles:
        print(f"{len(missing_titles)} titre(s) du CSV introuvable(s) dans les doublons actuels.")

    for playlist_id, tracks in removals_by_playlist.items():
        print(f"\nPlaylist {playlist_id} : {len(tracks)} suppression(s)")
        for track in tracks:
            print(f"  - {track_label(track)}")

    if not args.apply:
        print("\nDry-run : ajoute --apply pour supprimer les titres des playlists non listées dans le CSV.")
        return

    confirm_or_exit(args, f"{removal_count} titre(s) vont être retirés des playlists non listées dans {args.import_csv}.")
    for playlist_id, tracks in removals_by_playlist.items():
        for batch in chunked(tracks, args.batch_size):
            yt.remove_playlist_items(playlist_id, batch)

    print("\nNettoyage terminé.")


def cmd_cross_duplicates(args):
    yt = get_ytmusic()
    ignored = set() if args.include_ignored else get_ignore_playlists()
    ignored.update(args.ignore or [])
    playlist_selectors = list(args.playlist or [])

    playlist_file = args.playlist_file
    if not playlist_file and DEFAULT_PLAYLIST_FILE.exists():
        playlist_file = DEFAULT_PLAYLIST_FILE
        print(f"Fichier utilisé : {playlist_file}")

    if playlist_file:
        playlist_selectors.extend(load_playlist_selectors(playlist_file))

    tracks_by_key = defaultdict(list)
    labels_by_key = {}

    for playlist, details in iter_selected_playlists(yt, playlist_selectors, ignored, args.track_limit):
        seen_in_playlist = set()
        for track in details.get("tracks", []):
            key = track_key(track)
            if key in seen_in_playlist:
                continue

            seen_in_playlist.add(key)
            tracks_by_key[key].append(
                {
                    "playlist_id": playlist["playlistId"],
                    "playlist_title": playlist["title"],
                    "track": track,
                }
            )
            labels_by_key.setdefault(key, track_label(track))

    duplicates = {
        key: playlists
        for key, playlists in tracks_by_key.items()
        if len(playlists) > 1
    }

    print(f"Doublons entre playlists : {len(duplicates)} morceau(x)")
    if ignored:
        print(f"Playlists ignorées : {', '.join(sorted(ignored))}")

    for key, playlists in sorted(duplicates.items(), key=lambda item: labels_by_key[item[0]].casefold()):
        print(f"\n{labels_by_key[key]}")
        for playlist_title in sorted(entry["playlist_title"] for entry in playlists):
            print(f"  - {playlist_title}")

    if args.export_csv:
        export_duplicates_csv(args.export_csv, duplicates, labels_by_key)

    if args.import_csv:
        clean_from_csv(yt, args, duplicates, labels_by_key)
