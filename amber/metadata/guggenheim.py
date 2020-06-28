from amber.metadata.base import MetadataBase


class GuggenheimMetadata(MetadataBase):
    async def get_source_metadata(self, session, metadata_url):
        async with session.get(metadata_url) as resp:
            return await resp.json()

    async def get_image_metadata(self, session, image_id):
        async with session.get(
            f"{self.image_api}", params={"filter[name]": image_id}
        ) as resp:
            metadata = await resp.json()
            source_metadata = await self._get_parsed_source_metadata(session, metadata)
            parsed_metadata = self.parse_image_metadata(
                metadata, source_metadata=source_metadata
            )

        return parsed_metadata

    async def _get_parsed_source_metadata(self, session, metadata):
        if type(metadata) == list:
            metadata = metadata[0]

        source_metadata_list = []
        source_metadata = await self.get_source_metadata(
            session, metadata["_links"]["wp:attachment"][0]["href"]
        )
        for link in source_metadata:
            source_metadata_dict = {
                "id": link["id"],
                "slug": link["slug"],
                "date_modified": link["modified"],
                "media_details": link["media_details"],
            }
            source_metadata_list.append(source_metadata_dict)

        return source_metadata

    def parse_image_metadata(self, metadata, source_metadata=None):
        if type(metadata) == list:
            metadata = metadata[0]

        artist_str = ""
        for i, artist in enumerate(metadata["artist"]):
            if i == 0:
                artist_str = artist["name"]
            else:
                artist_str += f", {artist['name']['name']}"

        metadata = self.generate_metadata(
            source=self.name,
            artist=artist_str,
            title=metadata["title"]["rendered"],
            creditline=metadata["credit"],
            dated=metadata["dates"],
            resolution=None,
            source_url=metadata["link"],
            source_metadata=source_metadata,
        )

        return metadata
