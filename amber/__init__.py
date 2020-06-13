import toml
from appdirs import user_config_dir
import pathlib
import click
from colorama import init

init()

CONFIG_DIR = pathlib.Path(user_config_dir(appname="amber"))
CONFIG_FILE = CONFIG_DIR / "config.toml"
DEFAULT_DOWNLOAD_DIR = pathlib.Path.home() / "Downloads"

DEFAULT_CONFIG = {
    "download_directory": str(DEFAULT_DOWNLOAD_DIR),
    "filename_template": "{artist} - {title} ({dated})",
}

if not CONFIG_DIR.exists():
    CONFIG_DIR.mkdir()

if not CONFIG_FILE.exists():
    with open(CONFIG_FILE, "w") as config_handle:
        toml.dump(DEFAULT_CONFIG, config_handle)

    click.secho(
        f"A default config has been written at: {str(CONFIG_FILE)}", fg="magenta"
    )

with open(CONFIG_FILE, "r") as config:
    config = toml.load(config)
