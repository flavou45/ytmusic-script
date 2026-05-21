from pathlib import Path
import json


BASE_DIR = Path(__file__).resolve().parent.parent
JSON_DIR = BASE_DIR / "json"
BACKUP_DIR = BASE_DIR / "backups"
EXPORT_DIR = BASE_DIR / "exports"
CONFIG_FILE = JSON_DIR / "config.json"

PLAYLIST_LIMIT = 1000
TRACK_LIMIT = 5000
LIBRARY_LIMIT = 10000
BATCH_SIZE = 50
PAUSE_SECONDS = 0.3

DEFAULT_IGNORE_PLAYLISTS = {}

DEFAULT_CONFIG = {
    "ignore_playlists": sorted(DEFAULT_IGNORE_PLAYLISTS),
    "playlist_limit": PLAYLIST_LIMIT,
    "track_limit": TRACK_LIMIT,
    "library_limit": LIBRARY_LIMIT,
    "batch_size": BATCH_SIZE,
    "pause_seconds": PAUSE_SECONDS,
}


def load_config():
    if not CONFIG_FILE.exists():
        return dict(DEFAULT_CONFIG)

    with CONFIG_FILE.open("r", encoding="utf-8") as file:
        user_config = json.load(file)

    config = dict(DEFAULT_CONFIG)
    config.update(user_config)
    return config


def save_config(config):
    CONFIG_FILE.write_text(json.dumps(config, ensure_ascii=False, indent=2), encoding="utf-8")


def ensure_config_file():
    if CONFIG_FILE.exists():
        return False

    save_config(DEFAULT_CONFIG)
    return True


def get_ignore_playlists(extra=None):
    ignored = set(load_config().get("ignore_playlists", []))
    ignored.update(extra or [])
    return ignored
