import json
import time
from pathlib import Path

from common.client import get_ytmusic
from common.utils import chunked, confirm_or_exit, video_ids_from_tracks


def cmd_restore(args):
    backup_file = Path(args.backup_file)
    payload = json.loads(backup_file.read_text(encoding="utf-8"))
    source_playlist = payload.get("playlist", {})
    details = payload.get("details", {})
    title = args.title or source_playlist.get("title") or backup_file.stem
    video_ids = video_ids_from_tracks(details.get("tracks", []))

    print(f"Restore : {title}")
    print(f"{len(video_ids)} titre(s) restaurable(s)")

    if not args.apply:
        print("Dry-run : ajoute --apply pour créer la playlist.")
        return

    confirm_or_exit(args, f"La playlist '{title}' va être créée avec {len(video_ids)} titre(s).")
    yt = get_ytmusic()
    playlist_id = yt.create_playlist(title, args.description, args.privacy)

    for batch in chunked(video_ids, args.batch_size):
        yt.add_playlist_items(playlist_id, batch, duplicates=False)
        time.sleep(args.pause)

    print(f"Playlist restaurée : {title} - {playlist_id}")
