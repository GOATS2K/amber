import toml
from appdirs import user_config_dir
import pathlib
from amber.config import (
    create_config_dir,
    write_default_config,
    update_config,
    DEFAULT_CONFIG,
)
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

if not CONFIG_DIR.exists():
    create_config_dir(CONFIG_DIR)
    write_default_config(CONFIG_FILE, DEFAULT_CONFIG)

if CONFIG_FILE.exists():
    update_config(CONFIG_FILE, DEFAULT_CONFIG)
else:
    write_default_config(CONFIG_FILE, DEFAULT_CONFIG)


with open(CONFIG_FILE, "r") as config_handle:
    config = toml.load(config_handle)
