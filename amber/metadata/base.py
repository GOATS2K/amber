from abc import ABC


class MetadataBase(ABC):
    @staticmethod
    def generate_metadata(
        source,
        artist,
        title,
        dated,
        resolution,
        source_url,
        country=None,
        portfolio=None,
        creditline=None,
        source_metadata=None,
    ):

        metadata = {
            "source": source,
            "artist": artist,
            "title": title,
            "portfolio": portfolio,
            "credits": creditline,
            "country": country,
            "dated": dated,
            "resolution": resolution,
            "source_url": source_url,
            "source_metadata": source_metadata,
        }

        return metadata
