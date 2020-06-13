import click
import sys
import asyncio
import aiohttp
import inquirer
from amber.common import generate_inquirer_choices
from amber import CONFIG_FILE
from amber.extractors import SOURCES
from amber.downloader import download_image, download_multiple_images
import shutil


def get_available_sources():
    """ Generates usable instances of available sources """
    available_sources = []

    for i in SOURCES:
        source_module = SOURCES[i]
        source_class = getattr(source_module, i)
        source = source_class()
        available_sources.append(source)

    return available_sources


def prompt_for_search_results(friendly_results, all_results):
    questions = [
        inquirer.Checkbox(
            "results",
            message="[Up/Down] Choose | [Space] Select | [Enter] Confirm",
            choices=friendly_results,
        )
    ]

    try:
        search_prompt = inquirer.prompt(questions)
        results_to_download = [
            image
            for image in all_results
            if image["source_url"] in search_prompt["results"]
        ]
    except TypeError:
        # Prompt is cancelled
        sys.exit(1)

    return results_to_download


async def source_search(
    search_str, search_limit=10, source_instance=None, source_instance_list=None
):
    """
    Runs an extractor class' search function.
    We're doing the list search here for performance reasons.
    ^ aiohttp prefers that we reuse the session ^
    """

    async with aiohttp.ClientSession() as session:
        if source_instance:
            results = await source_instance.search(
                session, search_str, search_limit=search_limit
            )
        elif source_instance_list:
            results = []
            tasks = [
                i.search(session, search_str, search_limit=search_limit)
                for i in source_instance_list
            ]
            search_results = await asyncio.gather(*tasks)
            for i in search_results:
                results += i

    return results


@click.group()
def cmdgroup():
    pass


@cmdgroup.command()
def config():
    """ Edit configuration file """
    click.edit(filename=CONFIG_FILE)


@cmdgroup.command()
@click.argument("source")
@click.argument("image_id")
def download(source, image_id):
    """ Download an image by ID """
    try:
        # Get internal source name
        downloader_module = SOURCES[source]
        # Initialize source class
        source_class = getattr(downloader_module, source)
        # Instantiate class
        source = source_class()
    except KeyError:
        click.secho("This source is not supported.", fg="red")
        sys.exit(1)

    asyncio.run(download_image(source, image_id))


@cmdgroup.command()
@click.argument("search_str", nargs=-1)
@click.option("--limit", default=5, help="Max amount of images to display per source.")
@click.option(
    "--source", default="all", help="Source name to search, defaults to all sources."
)
def search(search_str, limit, source):
    """ Search and download images """
    download_tasks = []
    available_sources = get_available_sources()

    column, width = shutil.get_terminal_size()
    search_string = " ".join(search_str)

    if source == "all":
        all_results = asyncio.run(
            source_search(
                search_string,
                search_limit=limit,
                source_instance_list=available_sources,
            )
        )
    else:
        try:
            selected_source = [
                source_instance
                for source_instance in available_sources
                if source.lower() == source_instance.name.lower()
            ][0]

            all_results = asyncio.run(
                source_search(
                    search_string, search_limit=limit, source_instance=selected_source
                )
            )
        except IndexError:
            click.secho("Amber only supports the following sources:")
            for i in available_sources:
                click.secho(f"{i.name}", fg="magenta")
            sys.exit(1)

    friendly_results = generate_inquirer_choices(
        all_results, terminal_colomn_length=column
    )

    results_to_download = prompt_for_search_results(friendly_results, all_results)

    for source_instance in available_sources:
        download_queue = [
            image
            for image in results_to_download
            if image["source"] == source_instance.name
        ]
        for dl in download_queue:
            download_tasks.append(download_image(source_instance, image_metadata=dl))

    asyncio.run(download_multiple_images(download_tasks))
