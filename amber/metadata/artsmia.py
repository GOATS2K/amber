from amber.metadata.base import MetadataBase


class ArtsmiaMetadata(MetadataBase):
    async def get_image_metadata(self, session, image_id):
        """ Get the metadata for an image via its ID """
        async with session.get(f"{self.search_url}/id/{image_id}") as resp:
            metadata = await resp.json()

        return self.parse_image_metadata(metadata)

    def parse_image_metadata(self, metadata):
        bloated_artist_string = ["Photographer: ", "Designer: "]

        try:
            artist = metadata["highlight_artist_suggest"]["output"]
        except KeyError:
            try:
                artist = metadata["artist_suggest"]["output"]
            except KeyError:
                artist = metadata.get("artist", "Unknown")

        for i in bloated_artist_string:
            if i in artist:
                artist = artist.strip(i)

        resolution = f"{metadata['image_width']}x{metadata['image_height']}"

        source_url = f"https://collections.artsmia.org/art/{metadata['id']}"

        source_metadata = {
            "id": metadata["id"],
            "iiif_image_id": f"{metadata['id']}.jpg",
        }

        image_metadata = self.generate_metadata(
            source=self.name,
            artist=artist,
            title=metadata["title"],
            portfolio=metadata.get("portfolio", None),
            creditline=metadata["creditline"],
            country=metadata["country"],
            dated=metadata["dated"],
            resolution=resolution,
            source_url=source_url,
            source_metadata=source_metadata,
        )

        return image_metadata
