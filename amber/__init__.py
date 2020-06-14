import toml
from appdirs import user_config_dir
import pathlib
import click
import asyncio
import sys
from colorama import init

init()

# Change event loop on Windows.
# aiohttp fails with "RuntimeError: Event loop is closed" without this fix.

if (
    sys.version_info[0] == 3
    and sys.version_info[1] >= 8
    and sys.platform.startswith("win")
):
    asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())


CONFIG_DIR = pathlib.Path(user_config_dir(appname="amber"))
CONFIG_FILE = CONFIG_DIR / "config.toml"
DEFAULT_DOWNLOAD_DIR = pathlib.Path.home() / "Downloads"

DEFAULT_CONFIG = {
    "download_directory": str(DEFAULT_DOWNLOAD_DIR),
    "filename_template": "{artist} - {title} ({dated})",
    "max_simultaneous_downloads": 8,
}

if not CONFIG_DIR.exists():
    CONFIG_DIR.mkdir(parents=True)

if not CONFIG_FILE.exists():
    with open(CONFIG_FILE, "w") as config_handle:
        toml.dump(DEFAULT_CONFIG, config_handle)

    click.secho(
        f"A default config has been written to: {str(CONFIG_FILE)}", fg="magenta"
    )
else:
    # Add missing keys to config.
    config_update = None
    with open(CONFIG_FILE, "r+") as config_handle:
        config = toml.load(config_handle)

        for key, value in DEFAULT_CONFIG.items():
            if key not in config:
                config_update = True
                config[key] = value

        if config_update:
            click.secho(
                "A recent update introduced a new configuration option.", fg="magenta"
            )
            click.secho(
                "This has now been added to your current configuration file.\n",
                fg="magenta",
            )
            # Delete contents of file
            config_handle.seek(0)
            config_handle.truncate()
            toml.dump(config, config_handle)


with open(CONFIG_FILE, "r") as config_handle:
    config = toml.load(config_handle)
