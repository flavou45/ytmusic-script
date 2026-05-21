import json

from common.config import CONFIG_FILE, DEFAULT_CONFIG, ensure_config_file, load_config, save_config


def cmd_config(args):
    if args.config_action == "init":
        created = ensure_config_file()
        if created:
            print(f"Config créée : {CONFIG_FILE}")
        else:
            print(f"Config déjà présente : {CONFIG_FILE}")
        return

    config = load_config()

    if args.config_action == "show":
        print(json.dumps(config, ensure_ascii=False, indent=2))
        return

    if args.config_action == "reset":
        save_config(DEFAULT_CONFIG)
        print(f"Config réinitialisée : {CONFIG_FILE}")
        return

    ignored = set(config.get("ignore_playlists", []))
    if args.config_action == "ignore-add":
        ignored.update(args.playlist)
        config["ignore_playlists"] = sorted(ignored)
        save_config(config)
        print("Playlist(s) ajoutée(s) à l'ignore list.")
        return

    if args.config_action == "ignore-remove":
        ignored.difference_update(args.playlist)
        config["ignore_playlists"] = sorted(ignored)
        save_config(config)
        print("Playlist(s) retirée(s) de l'ignore list.")
