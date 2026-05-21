from common.client import get_ytmusic
from common.utils import confirm_or_exit, resolve_playlist


def cmd_rename(args):
    yt = get_ytmusic()
    playlists = yt.get_library_playlists(limit=args.playlist_limit)
    playlist = resolve_playlist(yt, args.playlist, playlists)

    print(f"Renommage : {playlist['title']} -> {args.title}")
    if not args.apply:
        print("Dry-run : ajoute --apply pour renommer.")
        return

    confirm_or_exit(args, f"La playlist '{playlist['title']}' va être renommée en '{args.title}'.")
    result = yt.edit_playlist(playlist["playlistId"], title=args.title)
    print(f"Renommage terminé : {result}")
