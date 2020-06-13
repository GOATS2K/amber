import toml
from appdirs import user_config_dir
import pathlib
import click
import asyncio
import sys
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
    CONFIG_DIR.mkdir(parents=True)

if not CONFIG_FILE.exists():
    with open(CONFIG_FILE, "w") as config_handle:
        toml.dump(DEFAULT_CONFIG, config_handle)

    click.secho(
        f"A default config has been written at: {str(CONFIG_FILE)}", fg="magenta"
    )

with open(CONFIG_FILE, "r") as config:
    config = toml.load(config)

# Change event loop on Windows.
# aiohttp fails with "RuntimeError: Event loop is close" without this fix.

if (
    sys.version_info[0] == 3
    and sys.version_info[1] >= 8
    and sys.platform.startswith("win")
):
    asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())
