import click
import toml
import pathlib

DEFAULT_DOWNLOAD_DIR = pathlib.Path.home() / "Downloads"

DEFAULT_CONFIG = {
    "download_directory": str(DEFAULT_DOWNLOAD_DIR),
    "filename_template": "{artist} - {title} ({dated})",
    "max_simultaneous_downloads": 8,
    "folder_template": "{source}/{artist}",
    "create_subfolders": False,
}


def create_config_dir(config_dir):
    if not config_dir.exists():
        config_dir.mkdir(parents=True, exist_ok=True)


def write_default_config(config_file):
    with open(config_file, "w") as config_handle:
        toml.dump(DEFAULT_CONFIG, config_handle)
        click.secho(
            f"A default config has been written to: {str(config_file)}", fg="magenta"
        )


def update_config(config_file):
    config_update = None
    new_keys = []
    with open(config_file, "r+") as config_handle:
        config = toml.load(config_handle)

        for key, value in DEFAULT_CONFIG.items():
            if key not in config:
                config_update = True
                config[key] = value
                new_keys.append(key)

        if config_update:
            click.secho(
                "A recent update introduced new configuration options:", fg="magenta"
            )

            for new_key in new_keys:
                click.secho(new_key, fg="yellow")

            click.secho(
                "\nThese have now been added to your current configuration file.\n",
                fg="magenta",
            )
            # Delete contents of file
            config_handle.seek(0)
            config_handle.truncate()
            toml.dump(config, config_handle)
