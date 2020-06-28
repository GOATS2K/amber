from amber.metadata.guggenheim import GuggenheimMetadata
import mimetypes


class Guggenheim(GuggenheimMetadata):
    def __init__(self):
        self.search_url = "https://www.guggenheim.org/wp-json/guggenheim/v1/search"
        self.image_api = "https://www.guggenheim.org/wp-json/wp/v2/artwork"
        self.name = "Guggenheim"

    async def search(self, session, search_str, search_limit=10):
        async with session.get(
            f"{self.search_url}", params={"post_type": "artwork", "s": search_str}
        ) as resp:
            search_results = await resp.json()
            results = search_results["posts"]

            if len(results) >= search_limit:
                results = list(results)[:search_limit]

        parsed_results = []

        for i in results:
            source_metadata_list = []
            source_metadata = await self.get_source_metadata(
                session, i["_links"]["wp:attachment"][0]["href"]
            )
            for link in source_metadata:
                source_metadata_dict = {
                    "id": link["id"],
                    "slug": link["slug"],
                    "date_modified": link["modified"],
                    "media_details": link["media_details"],
                }
                source_metadata_list.append(source_metadata_dict)

            image_metadata = self.parse_image_metadata(
                i, source_metadata=source_metadata_list
            )

            parsed_results.append(image_metadata)

        return parsed_results

    async def get_image(self, session, image_id=None, image_metadata=None):
        if not image_metadata:
            image_metadata = await self.get_image_metadata(session, image_id)

        download_urls = []
        images = []

        original_metadata = image_metadata.copy()

        for i in image_metadata["source_metadata"]:
            url = i["media_details"]["sizes"]["full"]["source_url"]
            width = i["media_details"]["sizes"]["full"]["width"]
            height = i["media_details"]["sizes"]["full"]["height"]
            resolution = f"{width}x{height}"
            mime_type = i["media_details"]["sizes"]["full"]["mime_type"]
            file_format = mimetypes.guess_extension(mime_type).strip(".")

            download_urls.append(
                {
                    "slug": i["slug"],
                    "resolution": resolution,
                    "url": url,
                    "file_format": file_format,
                }
            )

        for i in download_urls:
            image_metadata["title"] = f"{original_metadata['title']} ({i['slug']})"
            image_metadata["resolution"] = i["resolution"]

            image = {
                "metadata": image_metadata,
                "url": i["url"],
                "file_format": i["file_format"],
            }

            images.append(image)

        return images
