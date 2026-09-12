"""
aMule — Source Catalog

Maintains the external information sources that aMule can ingest.

Current source type:
    RSS / Atom

Future source types:
    Web
    GitHub
    API
    Documents
    Agent

The catalog is intentionally independent from the crawler.
"""

from __future__ import annotations

import json

from dataclasses import asdict, dataclass
from pathlib import Path
from typing import Optional


CATALOG_PATH = Path(
    "data/ingestor/sources.json"
)


@dataclass
class Source:
    """
    Represents an external information source.
    """

    source_id: str
    name: str
    url: str
    source_type: str = "rss"
    enabled: bool = True
    category: Optional[str] = None
    description: Optional[str] = None


class SourceCatalog:
    """
    Persistent catalog of aMule ingestion sources.
    """

    def __init__(
        self,
        path: Path = CATALOG_PATH,
    ):
        self.path = Path(path)
        self.sources: dict[
            str,
            Source,
        ] = {}

        self._load()

    def _load(self) -> None:
        """
        Load the catalog from disk.
        """

        if not self.path.exists():
            return

        try:

            data = json.loads(
                self.path.read_text(
                    encoding="utf-8"
                )
            )

        except (
            OSError,
            json.JSONDecodeError,
        ):

            return

        for item in data:

            try:

                source = Source(
                    **item
                )

                self.sources[
                    source.source_id
                ] = source

            except TypeError:
                continue

    def _save(self) -> None:
        """
        Persist the catalog.
        """

        self.path.parent.mkdir(
            parents=True,
            exist_ok=True,
        )

        data = [
            asdict(source)
            for source in self.sources.values()
        ]

        self.path.write_text(
            json.dumps(
                data,
                indent=2,
                ensure_ascii=False,
            ),
            encoding="utf-8",
        )

    def add(
        self,
        source: Source,
    ) -> Source:
        """
        Add or replace a source.
        """

        if not source.source_id:
            raise ValueError(
                "source_id is required."
            )

        if not source.name:
            raise ValueError(
                "source name is required."
            )

        if not source.url:
            raise ValueError(
                "source URL is required."
            )

        self.sources[
            source.source_id
        ] = source

        self._save()

        return source

    def remove(
        self,
        source_id: str,
    ) -> bool:
        """
        Remove a source.
        """

        if source_id not in self.sources:
            return False

        del self.sources[
            source_id
        ]

        self._save()

        return True

    def get(
        self,
        source_id: str,
    ) -> Optional[Source]:
        """
        Retrieve a source by ID.
        """

        return self.sources.get(
            source_id
        )

    def list(
        self,
        enabled_only: bool = False,
        source_type: Optional[str] = None,
    ) -> list[Source]:
        """
        List catalog sources.
        """

        sources = list(
            self.sources.values()
        )

        if enabled_only:

            sources = [
                source
                for source in sources
                if source.enabled
            ]

        if source_type:

            sources = [
                source
                for source in sources
                if source.source_type
                == source_type
            ]

        return sources

    def enable(
        self,
        source_id: str,
    ) -> bool:
        """
        Enable a source.
        """

        source = self.get(
            source_id
        )

        if not source:
            return False

        source.enabled = True

        self._save()

        return True

    def disable(
        self,
        source_id: str,
    ) -> bool:
        """
        Disable a source.
        """

        source = self.get(
            source_id
        )

        if not source:
            return False

        source.enabled = False

        self._save()

        return True


def create_default_catalog() -> SourceCatalog:
    """
    Create the initial aMule source catalog.

    No external sources are added automatically.
    """

    return SourceCatalog()


if __name__ == "__main__":

    catalog = create_default_catalog()

    print(
        "aMule Source Catalog"
    )

    print(
        f"Sources: {len(catalog.list())}"
    )
