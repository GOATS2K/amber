from termcolor import colored
from colorama import Fore
import asyncio
import textwrap
import click
import sys


def generate_inquirer_string(metadata_dict, color_string=False):

    if color_string:
        """
        Due to the way that inquirer handles colors, we need to use a reset sequence
        to allow the rest of the selection string to be colored.
        """
        artist = f"{Fore.RESET} {metadata_dict['artist']}"
    else:
        artist = metadata_dict["artist"]

    if color_string and metadata_dict["resolution"]:
        resolution = colored(f"[{metadata_dict['resolution']}]", "cyan")
    else:
        resolution = metadata_dict["resolution"]

    if metadata_dict["resolution"]:
        fresult = f"{artist} - {metadata_dict['title']} ({metadata_dict['dated']}) {resolution} | {metadata_dict['source_url']}"  # noqa E501
    else:
        fresult = f"{artist} - {metadata_dict['title']} ({metadata_dict['dated']}) | {metadata_dict['source_url']}"  # noqa E501

    return fresult


def generate_inquirer_choices(
    metadata_list, terminal_colomn_length, metadata_key_to_return="source_url"
):
    """
    Generates a list of tuples to be used with Inquirier.
    Accepts a list of metadata dicts.
    """
    friendly_results = []
    terminal_too_small = None

    # Hacky way to relate string length with terminal width.
    terminal_colomn_length = terminal_colomn_length - 10
    for res in metadata_list:

        fresult = generate_inquirer_string(res)

        """
        Inquirier has a bug where if an element in the checkbox
        is larger than the width of the terminal,
        the prompt message repeats itself.

        In an attempt to mitigate this, we're shortening the length of
        the titles cause full result strings larger than the width of
        the users terminal window.
        """
        if terminal_colomn_length < len(fresult):

            truncated_title_length = len(res["title"]) - 1
            truncated_artist_length = len(res["artist"]) - 1

            while terminal_colomn_length < len(fresult):
                truncated_title_length -= 1

                try:
                    res["title"] = textwrap.shorten(
                        res["title"], width=truncated_title_length, placeholder="..."
                    )
                except ValueError:
                    # We can't reduce the size of the title string anymore.
                    try:
                        truncated_artist_length -= 1
                        res["artist"] = textwrap.shorten(
                            res["artist"],
                            width=truncated_artist_length,
                            placeholder="...",
                        )
                    except ValueError:
                        # We've run out of strings to manipulate
                        terminal_too_small = True
                        break

                fresult = generate_inquirer_string(res)

        colored_fresult = generate_inquirer_string(res, color_string=True)

        result_tuple = (colored_fresult, res[metadata_key_to_return])
        friendly_results.append(result_tuple)

    if terminal_too_small:
        click.secho(
            "Your terminal window is too narrow to display the search results properly.",  # noqa: E501
            fg="red",
        )
        sys.exit(1)

    return friendly_results


async def run_concurrently(tasks):
    """ Run async functions concurrently and return all results. """
    return await asyncio.gather(*tasks)
