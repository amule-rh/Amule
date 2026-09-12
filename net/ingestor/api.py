"""
aMule — Ingestion Source API

Provides an API-friendly interface for managing
the sources used by the aMule ingestion system.

Current source type:
    RSS / Atom

Future:
    Web
    GitHub
    API
    Documents
"""

from __future__ import annotations

from typing import Any

from net.ingestor.sources import (
    Source,
    SourceCatalog,
)


def add_source(
    catalog: SourceCatalog,
    source_id: str,
    name: str,
    url: str,
    source_type: str = "rss",
    category: str | None = None,
    description: str | None = None,
) -> dict[str, Any]:
    """
    Add a new ingestion source.
    """

    source = Source(
        source_id=source_id,
        name=name,
        url=url,
        source_type=source_type,
        enabled=True,
        category=category,
        description=description,
    )

    catalog.add(
        source
    )

    return source_to_dict(
        source
    )


def remove_source(
    catalog: SourceCatalog,
    source_id: str,
) -> bool:
    """
    Remove an ingestion source.
    """

    return catalog.remove(
        source_id
    )


def enable_source(
    catalog: SourceCatalog,
    source_id: str,
) -> bool:
    """
    Enable an ingestion source.
    """

    return catalog.enable(
        source_id
    )


def disable_source(
    catalog: SourceCatalog,
    source_id: str,
) -> bool:
    """
    Disable an ingestion source.
    """

    return catalog.disable(
        source_id
    )


def list_sources(
    catalog: SourceCatalog,
    enabled_only: bool = False,
) -> list[dict[str, Any]]:
    """
    Return all configured sources.
    """

    sources = catalog.list(
        enabled_only=enabled_only
    )

    return [
        source_to_dict(
            source
        )
        for source in sources
    ]


def get_source(
    catalog: SourceCatalog,
    source_id: str,
) -> dict[str, Any] | None:
    """
    Retrieve one source.
    """

    source = catalog.get(
        source_id
    )

    if not source:
        return None

    return source_to_dict(
        source
    )


def source_to_dict(
    source: Source,
) -> dict[str, Any]:
    """
    Serialize a Source.
    """

    return {
        "source_id": source.source_id,
        "name": source.name,
        "url": source.url,
        "source_type": source.source_type,
        "enabled": source.enabled,
        "category": source.category,
        "description": source.description,
    }
