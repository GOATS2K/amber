import aiohttp
from abc import ABC


class IIIF(ABC):
    def __init__(self):
        self.iiif_api = None

    async def available_qualities(self, session, iiif_image_id):
        """ Returns available qualities for image. """
        image_json = f"{self.iiif_api}/{iiif_image_id}/info.json"

        async with session.get(image_json) as resp:
            try:
                raw_image_quality_data = await resp.json()
            except aiohttp.ContentTypeError:
                return None

        image_quality_data = {
            "formats": raw_image_quality_data["profile"][1]["formats"],
            "qualities": raw_image_quality_data["profile"][1]["qualities"],
            "image_url": raw_image_quality_data["@id"],
        }

        return image_quality_data

    async def _test_download_link(self, session, url):
        """
        Test if download links work.
        IIIF sometimes only returns a small part of available qualities.
        This can be used to test if a "unavailable" link works
        """
        async with session.head(url) as resp:
            if resp.status == 200:
                return True
            else:
                return False

    async def generate_download_link(
        self, session, image_quality_data, quality="default", file_format="png"
    ):
        if image_quality_data:
            image_url = (
                f"{image_quality_data['image_url']}/full/full/0/{quality}.{file_format}"
            )

            if await self._test_download_link(session, image_url):
                return image_url, file_format
            elif (
                len(image_quality_data["formats"])
                and len(image_quality_data["qualities"]) == 1
            ):
                img_quality = image_quality_data["qualities"][0]
                img_codec = image_quality_data["formats"][0]
                return f"{image_quality_data['image_url']}/full/full/0/{img_quality}.{img_codec}"  # noqa: E501
            else:
                return (
                    f"{image_quality_data['image_url']}/full/full/0/default.{file_format}",
                    file_format,
                )
