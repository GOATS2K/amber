import aiofiles
import asyncio
import aiohttp
import re
import click
from halo import Halo
from string import Formatter
from amber import config
from pathlib import Path
from pathvalidate import sanitize_filename, sanitize_filepath


def strip_template_keys(template, key):
    # Code from light7s/smoked-salmon (https://github.com/ligh7s/smoked-salmon)
    # Licensed as Apache License 2.0
    folder = re.sub(r" *[\[{\(]*{" + key + r"}[\]}\)]* *", " ", template).strip()
    return re.sub(r" *- *$", "", folder)


def generate_destination_name(template, **kwargs):
    # Code from light7s/smoked-salmon (https://github.com/ligh7s/smoked-salmon)
    # Licensed as Apache License 2.0

    # Build new template string
    keys = [fn for _, fn, _, _ in Formatter().parse(template) if fn]
    non_empty_metadata = {k: v for k, v in kwargs.items() if v is not None}

    # Remove elements from template that aren't present in kwargs
    for k in keys.copy():
        if not kwargs.get(k):
            template = strip_template_keys(template, k)
            keys.remove(k)

    dest_name = template.format(**non_empty_metadata)

    return dest_name


async def get_images_to_download(session, available_sources, results_to_download):
    """
    Accepts a list of instantiated sources and a list of images to download.
    Returns image metadata with image URL
    """
    all_images = []
    url_tasks = []

    for source in available_sources:
        download_queue = [
            image for image in results_to_download if image["source"] == source.name
        ]
        for dl in download_queue:
            url_tasks.append(source.get_image(session, image_metadata=dl))

    images = await asyncio.gather(*url_tasks)

    for image in images:
        if type(image) == list:
            all_images += image
        else:
            all_images.append(image)

    return all_images


async def download_image(source, **kwargs):
    async with aiohttp.ClientSession() as session:
        spinner = Halo("Downloading image...", color="magenta")
        with spinner:
            image = await source.get_image(session, **kwargs)
            # Some sources deliver multiple image files per image
            if type(image) == list:
                for i in image:
                    image_path = await download_image_file(session, **i)
                    stem = Path(image_path).parent
                    complete_msg = f"Multiple images downloaded to {stem}"
            else:
                image_path = await download_image_file(session, **image)
                complete_msg = f"Image downloaded to {image_path}"

            spinner.succeed(complete_msg)


async def download_multiple_images(available_sources, results_to_download):
    """
    Accepts a list of instantiated sources and a list of images to download.
    Downloads images in list.
    """
    semaphore = asyncio.Semaphore(config["max_simultaneous_downloads"])
    spinner = Halo("Downloading images...", color="magenta")

    async with aiohttp.ClientSession() as session:
        images = await get_images_to_download(
            session, available_sources, results_to_download
        )
        async with semaphore:
            download_task = [
                bound_download_image_file(session, semaphore, **image)
                for image in images
            ]

            with spinner:
                results = await asyncio.gather(*download_task)
                if results:
                    spinner.succeed("Images downloaded.")

                if len(results) <= 8:
                    for res in results:
                        click.secho(res, fg="green")


async def download_image_file(session, metadata, url, file_format):
    target = _generate_download_target(metadata, file_format)

    async with session.get(url) as resp:
        async with aiofiles.open(target, mode="wb") as image:
            while True:
                chunk = await resp.content.read(4096)
                if not chunk:
                    break
                await image.write(chunk)

    return str(target)


def _generate_download_target(metadata, file_format):
    fname_template = config["filename_template"]
    folder_template = config["folder_template"]

    if config["create_subfolders"]:
        sub_folder = sanitize_filepath(
            generate_destination_name(folder_template, **metadata)
        )
        target_folder = Path(config["download_directory"]) / sub_folder
        target_folder.mkdir(parents=True, exist_ok=True)
    else:
        target_folder = Path(config["download_directory"])

    fname = sanitize_filename(
        f"{generate_destination_name(fname_template, **metadata)}.{file_format}"
    )
    target = target_folder / fname

    return target


async def bound_download_image_file(
    session, semaphore, metadata=None, url=None, file_format=None
):
    async with semaphore:
        return await download_image_file(session, metadata, url, file_format)
