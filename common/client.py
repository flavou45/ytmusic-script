from pathlib import Path

from ytmusicapi import YTMusic


BASE_DIR = Path(__file__).resolve().parent.parent
JSON_DIR = BASE_DIR / "json"


def get_ytmusic():
    return YTMusic(str(JSON_DIR / "browser.json"))
