import json
from datetime import datetime
from pathlib import Path

from common.client import get_ytmusic

from common.config import BACKUP_DIR, get_ignore_playlists


def cmd_backup(args):
    yt = get_ytmusic()
    timestamp = datetime.now().strftime("%Y%m%d-%H%M%S")
    out_dir = Path(args.output) if args.output else BACKUP_DIR / timestamp
    out_dir.mkdir(parents=True, exist_ok=True)

    ignored = set() if args.include_ignored else get_ignore_playlists()
    playlists = [
        playlist
        for playlist in yt.get_library_playlists(limit=args.playlist_limit)
        if playlist.get("title") not in ignored
    ]
    summary = []

    for playlist in playlists:
        title = playlist.get("title", "playlist")
        playlist_id = playlist.get("playlistId")
        print(f"Backup : {title}")
        try:
            details = yt.get_playlist(playlist_id, limit=args.track_limit)
        except Exception as exc:
            print(f"  Erreur => {exc}")
            continue

        safe_name = "".join(c if c.isalnum() or c in " ._-" else "_" for c in title).strip()
        filename = f"{safe_name or playlist_id}.json"
        payload = {"playlist": playlist, "details": details}
        (out_dir / filename).write_text(json.dumps(payload, ensure_ascii=False, indent=2), encoding="utf-8")
        summary.append(
            {
                "title": title,
                "playlistId": playlist_id,
                "trackCount": len(details.get("tracks", [])),
                "file": filename,
            }
        )

    (out_dir / "_summary.json").write_text(json.dumps(summary, ensure_ascii=False, indent=2), encoding="utf-8")
    print(f"\nBackup terminé : {out_dir}")
