from urllib.parse import urlparse
from amber.extractors.backends.iiif import IIIF
from amber.downloader import download_image_file
from amber.metadata.artsmia import ArtsmiaMetadata


class Artsmia(IIIF, ArtsmiaMetadata):
    def __init__(self):
        self.search_url = "https://search.artsmia.org"
        self.iiif_api = "https://iiif.dx.artsmia.org"
        self.iiif_tiles = "https://tiles.dx.artsmia.org/iiif"
        self.name = "Artsmia"

    async def search(self, session, search_str, search_limit=10):
        """ Search the Artsmia collection. """
        async with session.get(
            f"{self.search_url}/{search_str}", params={"size": search_limit}
        ) as resp:
            """
            For some reason, the search API response uses a 'text/html' content-type.
            Unless we explicitly say that aiohttp should expect that content type,
            the response fails to be parsed.
            """
            search_results = await resp.json(
                content_type=f"{resp.headers['Content-Type']}"
            )

            results = []

            for result in search_results["hits"]["hits"]:
                result = result["_source"]

                if result["image"] != "valid":
                    continue

                image_metadata = self.parse_image_metadata(result)

                results.append(image_metadata)

            return results

    async def _get_image_iiif_id(self, session, image_id):
        """ Get the ID that the IIIF backend uses to fetch images. """
        async with session.get(f"{self.iiif_tiles}/{image_id}") as resp:
            if resp.status == 200:
                iiif_metadata = await resp.json(
                    content_type=f"{resp.headers['Content-Type']}"
                )
            else:
                raise ConnectionError(f"[HTTP {resp.status}] Unable to reach IIIF.")

        image_url = urlparse(iiif_metadata["@id"])

        return str(image_url.path).strip("/")

    async def download(self, session, image_id=None, image_metadata=None):
        """ Downloads an image by its ID """
        if not image_metadata:
            image_metadata = await self.get_image_metadata(session, image_id)

        iiif_image_data = await self.available_qualities(
            session, image_metadata["source_metadata"]["iiif_image_id"]
        )
        if iiif_image_data:
            download_url, file_format = await self.generate_download_link(
                session, iiif_image_data
            )
            return await download_image_file(
                session, image_metadata, download_url, file_format
            )
        else:
            print(
                f"\nFailed to download {image_metadata['source_url']} - image not available."
            )
