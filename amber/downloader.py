import aiofiles
import asyncio
import aiohttp
import re
import click
from halo import Halo
from string import Formatter
from amber import config
from pathlib import Path
from pathvalidate import sanitize_filename


def strip_template_keys(template, key):
    # Code from light7s/smoked-salmon (https://github.com/ligh7s/smoked-salmon)
    # Licensed as Apache License 2.0
    folder = re.sub(r" *[\[{\(]*{" + key + r"}[\]}\)]* *", " ", template).strip()
    return re.sub(r" *- *$", "", folder)


def generate_filename(**kwargs):
    # Code from light7s/smoked-salmon (https://github.com/ligh7s/smoked-salmon)
    # Licensed as Apache License 2.0
    template = config["filename_template"]

    # Build new template string
    keys = [fn for _, fn, _, _ in Formatter().parse(template) if fn]
    non_empty_metadata = {k: v for k, v in kwargs.items() if v is not None}

    # Remove elements from template that aren't present in kwargs
    for k in keys.copy():
        if not kwargs.get(k):
            template = strip_template_keys(template, k)
            keys.remove(k)

    new_filename = template.format(**non_empty_metadata)

    return new_filename


async def download_image(source, single_image=False, **kwargs):
    """
    Runs an extractor's download function.
    """
    async with aiohttp.ClientSession() as session:
        if single_image:
            spinner = Halo("Downloading image...", color="magenta")
            with spinner:
                image_path = await source.download(session, **kwargs)
                spinner.succeed(f"Image downloaded to {image_path}")
        else:
            await source.download(session, **kwargs)


async def download_multiple_images(tasks):
    """
    Downloads multiple images.
    Accepts a list of coroutines.
    """
    spinner = Halo("Downloading images...", color="magenta")
    with spinner:
        results = await asyncio.gather(*tasks)
        if results:
            spinner.succeed("Images downloaded:")

        if len(results) <= 8:
            for res in results:
                if type(res) is list:
                    for i in res:
                        click.secho(i, fg="green")
                else:
                    click.secho(res, fg="green")


async def download_image_file(session, metadata, url, file_format):
    fname = sanitize_filename(f"{generate_filename(**metadata)}.{file_format}")
    target = Path(config["download_directory"]) / fname

    async with session.get(url) as resp:
        async with aiofiles.open(target, mode="wb") as image:
            while True:
                chunk = await resp.content.read(4096)
                if not chunk:
                    break
                await image.write(chunk)

    return str(target)
