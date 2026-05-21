import argparse

from common.config import BATCH_SIZE, EXPORT_DIR, LIBRARY_LIMIT, PAUSE_SECONDS, PLAYLIST_LIMIT, TRACK_LIMIT


def command(module_name, function_name):
    def runner(args):
        try:
            module = __import__(f"tools.{module_name}", fromlist=[function_name])
        except ModuleNotFoundError as exc:
            if exc.name == "ytmusicapi":
                raise SystemExit(
                    "Dépendance manquante : ytmusicapi.\n"
                    "Utilise le Python du venv : .\\.venv\\Scripts\\python.exe .\\ytmusic_manager.py ...\n"
                    "Ou installe les dépendances : python -m pip install -r requirements.txt"
                ) from exc
            raise

        getattr(module, function_name)(args)

    return runner


def add_common_scan_args(parser):
    parser.add_argument("playlist", nargs="*", help="Titre ou ID des playlists à analyser. Vide = toutes.")
    parser.add_argument("--playlist-limit", type=int, default=PLAYLIST_LIMIT)
    parser.add_argument("--track-limit", type=int, default=TRACK_LIMIT)
    parser.add_argument("--include-ignored", action="store_true", help="Inclut les playlists de l'ignore list.")


def add_apply_args(parser, apply_help):
    parser.add_argument("--apply", action="store_true", help=apply_help)
    parser.add_argument("--yes", action="store_true", help="Saute la confirmation interactive.")


def add_batch_args(parser):
    parser.add_argument("--batch-size", type=int, default=BATCH_SIZE)
    parser.add_argument("--pause", type=float, default=PAUSE_SECONDS)


def build_parser():
    parser = argparse.ArgumentParser(description="Outil de gestion YouTube Music.")
    subparsers = parser.add_subparsers(dest="command", required=True)

    list_parser = subparsers.add_parser("list", help="Lister les playlists.")
    list_parser.add_argument("--limit", type=int, default=PLAYLIST_LIMIT)
    list_parser.set_defaults(func=command("listing", "cmd_list"))

    search_parser = subparsers.add_parser("search", help="Chercher un titre, artiste ou album dans les playlists.")
    search_parser.add_argument("query", help="Texte à chercher.")
    search_parser.add_argument("playlist", nargs="*", help="Titre ou ID des playlists à analyser. Vide = toutes.")
    search_parser.add_argument(
        "--field",
        action="append",
        choices=["title", "artist", "album"],
        default=["title", "artist", "album"],
        help="Champ à chercher. Répétable.",
    )
    search_parser.add_argument("--playlist-limit", type=int, default=PLAYLIST_LIMIT)
    search_parser.add_argument("--track-limit", type=int, default=TRACK_LIMIT)
    search_parser.add_argument("--library-limit", type=int, default=LIBRARY_LIMIT)
    search_parser.add_argument("--export-csv", help="Exporte les résultats en CSV.")
    search_parser.set_defaults(func=command("search", "cmd_search"))

    backup_parser = subparsers.add_parser("backup", help="Sauvegarder les playlists en JSON.")
    backup_parser.add_argument("--output")
    backup_parser.add_argument("--playlist-limit", type=int, default=PLAYLIST_LIMIT)
    backup_parser.add_argument("--track-limit", type=int, default=TRACK_LIMIT)
    backup_parser.add_argument("--include-ignored", action="store_true")
    backup_parser.set_defaults(func=command("backup", "cmd_backup"))

    dup_parser = subparsers.add_parser("duplicates", help="Vérifier ou supprimer les doublons dans les playlists.")
    add_common_scan_args(dup_parser)
    add_batch_args(dup_parser)
    add_apply_args(dup_parser, "Supprime réellement les doublons.")
    dup_parser.set_defaults(func=command("duplicates", "cmd_duplicates"))

    cross_dup_parser = subparsers.add_parser(
        "cross-duplicates",
        help="Lister les morceaux présents dans plusieurs playlists.",
    )
    add_common_scan_args(cross_dup_parser)
    cross_dup_parser.add_argument("--playlist-file", help="Fichier JSON avec la liste des playlists à vérifier.")
    cross_dup_parser.add_argument("--ignore", action="append", help="Playlist à ignorer pour cet appel. Répétable.")
    cross_dup_parser.add_argument(
        "--export-csv",
        nargs="?",
        const=str(EXPORT_DIR / "cross_duplicates.csv"),
        help="Exporte les doublons entre playlists en CSV.",
    )
    cross_dup_parser.add_argument("--import-csv", help="Importe un CSV pour supprimer les playlists non listées.")
    cross_dup_parser.add_argument("--batch-size", type=int, default=BATCH_SIZE)
    add_apply_args(cross_dup_parser, "Supprime réellement les titres des playlists non listées dans le CSV.")
    cross_dup_parser.set_defaults(func=command("cross_duplicates", "cmd_cross_duplicates"))

    sync_parser = subparsers.add_parser("sync-library", help="Ajouter à la bibliothèque les titres de playlists.")
    sync_parser.add_argument("playlist", nargs="*", help="Titre ou ID des playlists à synchroniser. Vide = toutes sauf ignorées.")
    sync_parser.add_argument("--ignore", action="append", help="Playlist à ignorer. Répétable.")
    sync_parser.add_argument("--include-ignored", action="store_true")
    sync_parser.add_argument("--library-limit", type=int, default=LIBRARY_LIMIT)
    sync_parser.add_argument("--track-limit", type=int, default=TRACK_LIMIT)
    add_batch_args(sync_parser)
    add_apply_args(sync_parser, "Ajoute réellement les titres.")
    sync_parser.set_defaults(func=command("sync_library", "cmd_sync_library"))

    merge_parser = subparsers.add_parser("merge", help="Fusionner plusieurs playlists.")
    merge_parser.add_argument("--source", action="append", required=True, help="Playlist source. Répétable.")
    merge_parser.add_argument("--target", required=True, help="Playlist cible existante, ou nom si --create-target.")
    merge_parser.add_argument("--create-target", action="store_true")
    merge_parser.add_argument("--description", default="Playlist fusionnée avec ytmusic_manager.py")
    merge_parser.add_argument("--privacy", choices=["PRIVATE", "PUBLIC", "UNLISTED"], default="PRIVATE")
    merge_parser.add_argument("--playlist-limit", type=int, default=PLAYLIST_LIMIT)
    merge_parser.add_argument("--track-limit", type=int, default=TRACK_LIMIT)
    merge_parser.add_argument("--include-ignored", action="store_true")
    add_batch_args(merge_parser)
    add_apply_args(merge_parser, "Modifie réellement la playlist cible.")
    merge_parser.set_defaults(func=command("merge", "cmd_merge"))

    missing_parser = subparsers.add_parser("missing", help="Trouver les morceaux manquants ou indisponibles.")
    add_common_scan_args(missing_parser)
    missing_parser.add_argument("--search", action="store_true", help="Recherche des remplaçants possibles.")
    missing_parser.add_argument("--search-limit", type=int, default=3)
    missing_parser.set_defaults(func=command("missing", "cmd_missing"))

    stats_parser = subparsers.add_parser("stats", help="Afficher des statistiques musicales.")
    add_common_scan_args(stats_parser)
    stats_parser.add_argument("--top", type=int, default=10)
    stats_parser.set_defaults(func=command("stats", "cmd_stats"))

    restore_parser = subparsers.add_parser("restore", help="Restaurer une playlist depuis un backup JSON.")
    restore_parser.add_argument("backup_file")
    restore_parser.add_argument("--title")
    restore_parser.add_argument("--description", default="Playlist restaurée avec ytmusic_manager.py")
    restore_parser.add_argument("--privacy", choices=["PRIVATE", "PUBLIC", "UNLISTED"], default="PRIVATE")
    add_batch_args(restore_parser)
    add_apply_args(restore_parser, "Crée réellement la playlist.")
    restore_parser.set_defaults(func=command("restore", "cmd_restore"))

    export_parser = subparsers.add_parser("export", help="Exporter une playlist en JSON, CSV ou Markdown.")
    export_parser.add_argument("playlist", help="Titre ou ID de la playlist.")
    export_parser.add_argument("--format", choices=["json", "csv", "md"], default="csv")
    export_parser.add_argument("--output")
    export_parser.add_argument("--playlist-limit", type=int, default=PLAYLIST_LIMIT)
    export_parser.add_argument("--track-limit", type=int, default=TRACK_LIMIT)
    export_parser.set_defaults(func=command("export", "cmd_export"))

    compare_parser = subparsers.add_parser("compare", help="Comparer deux playlists.")
    compare_parser.add_argument("left")
    compare_parser.add_argument("right")
    compare_parser.add_argument("--show", action="store_true", help="Affiche les titres différents.")
    compare_parser.add_argument("--playlist-limit", type=int, default=PLAYLIST_LIMIT)
    compare_parser.add_argument("--track-limit", type=int, default=TRACK_LIMIT)
    compare_parser.set_defaults(func=command("compare", "cmd_compare"))

    clean_parser = subparsers.add_parser("clean-library", help="Lister les titres de bibliothèque hors playlists.")
    add_common_scan_args(clean_parser)
    clean_parser.add_argument("--library-limit", type=int, default=LIBRARY_LIMIT)
    clean_parser.add_argument("--limit", type=int, default=50)
    clean_parser.add_argument(
        "--export-csv",
        nargs="?",
        const=str(EXPORT_DIR / "clean_library.csv"),
        help="Exporte la liste complète en CSV.",
    )
    clean_parser.set_defaults(func=command("clean_library", "cmd_clean_library"))

    copy_parser = subparsers.add_parser("copy", help="Copier une playlist vers une nouvelle playlist sans doublons.")
    copy_parser.add_argument("source")
    copy_parser.add_argument("--title")
    copy_parser.add_argument("--description", default="Playlist copiée avec ytmusic_manager.py")
    copy_parser.add_argument("--privacy", choices=["PRIVATE", "PUBLIC", "UNLISTED"], default="PRIVATE")
    copy_parser.add_argument("--playlist-limit", type=int, default=PLAYLIST_LIMIT)
    copy_parser.add_argument("--track-limit", type=int, default=TRACK_LIMIT)
    add_batch_args(copy_parser)
    add_apply_args(copy_parser, "Crée réellement la copie.")
    copy_parser.set_defaults(func=command("copy", "cmd_copy"))

    rename_parser = subparsers.add_parser("rename", help="Renommer une playlist.")
    rename_parser.add_argument("playlist")
    rename_parser.add_argument("title")
    rename_parser.add_argument("--playlist-limit", type=int, default=PLAYLIST_LIMIT)
    add_apply_args(rename_parser, "Renomme réellement la playlist.")
    rename_parser.set_defaults(func=command("rename", "cmd_rename"))

    audit_parser = subparsers.add_parser("audit", help="Rapport global : doublons, manquants, ignore list.")
    add_common_scan_args(audit_parser)
    audit_parser.add_argument("--details", action="store_true")
    audit_parser.add_argument("--limit", type=int, default=50)
    audit_parser.set_defaults(func=command("audit", "cmd_audit"))

    recommend_parser = subparsers.add_parser("recommend-missing", help="Proposer des remplaçants aux morceaux manquants.")
    add_common_scan_args(recommend_parser)
    recommend_parser.add_argument("--search-limit", type=int, default=3)
    recommend_parser.add_argument("--replace", action="store_true", help="Supprime l'ancien morceau après ajout du remplaçant.")
    add_batch_args(recommend_parser)
    add_apply_args(recommend_parser, "Ajoute réellement les remplaçants proposés.")
    recommend_parser.set_defaults(func=command("recommend_missing", "cmd_recommend_missing"))

    config_parser = subparsers.add_parser("config", help="Afficher ou modifier config.json.")
    config_subparsers = config_parser.add_subparsers(dest="config_action", required=True)
    config_subparsers.add_parser("init").set_defaults(func=command("config_tool", "cmd_config"))
    config_subparsers.add_parser("show").set_defaults(func=command("config_tool", "cmd_config"))
    config_subparsers.add_parser("reset").set_defaults(func=command("config_tool", "cmd_config"))
    ignore_add = config_subparsers.add_parser("ignore-add")
    ignore_add.add_argument("playlist", nargs="+")
    ignore_add.set_defaults(func=command("config_tool", "cmd_config"))
    ignore_remove = config_subparsers.add_parser("ignore-remove")
    ignore_remove.add_argument("playlist", nargs="+")
    ignore_remove.set_defaults(func=command("config_tool", "cmd_config"))

    return parser
