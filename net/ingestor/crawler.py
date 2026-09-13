"""
aMule — Source Crawler

Orchestrates the ingestion of enabled sources.

Pipeline:

    Source Catalog
          ↓
       Crawler
          ↓
       Ingestor
          ↓
       Processor
          ↓
    Processed Resources

The crawler is responsible for orchestration.
Identity and content hashing remain inside the processor.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any

from net.ingestor.processor import (
    ProcessedResource,
    process_batch,
    resource_to_dict,
)

from net.ingestor.rss import (
    ingest_rss,
    resource_candidate,
)

from net.ingestor.sources import (
    Source,
    SourceCatalog,
)


@dataclass
class CrawlResult:
    sources_processed: int
    candidates_found: int
    resources_created: int

    resources: list[ProcessedResource]

    errors: list[dict[str, str]]


def crawl_rss_source(
    source: Source,
) -> list[dict[str, Any]]:
    """
    Ingest one RSS/Atom source and convert
    its items into aMule candidates.
    """

    items = ingest_rss(
        source.url
    )

    candidates: list[
        dict[str, Any]
    ] = []

    for item in items:

        candidate = resource_candidate(
            item
        )

        candidate["ingestor"] = "rss"

        candidate["source_id"] = (
            source.source_id
        )

        candidate["source_name"] = (
            source.name
        )

        candidate["category"] = (
            source.category
        )

        candidates.append(
            candidate
        )

    return candidates


def crawl_source(
    source: Source,
) -> list[dict[str, Any]]:
    """
    Crawl a single registered source.
    """

    source_type = (
        source.source_type
        .lower()
        .strip()
    )

    if source_type in {
        "rss",
        "atom",
    }:

        return crawl_rss_source(
            source
        )

    raise ValueError(
        f"Unsupported source type: "
        f"{source.source_type}"
    )


def crawl_catalog(
    catalog: SourceCatalog,
    known_resource_ids: set[str] | None = None,
) -> CrawlResult:
    """
    Crawl all enabled sources.

    known_resource_ids contains logical Resource IDs,
    not content hashes.
    """

    if known_resource_ids is None:

        known_resource_ids = set()

    all_candidates: list[
        dict[str, Any]
    ] = []

    errors: list[
        dict[str, str]
    ] = []

    sources_processed = 0

    sources = catalog.list(
        enabled_only=True
    )

    for source in sources:

        try:

            candidates = crawl_source(
                source
            )

            all_candidates.extend(
                candidates
            )

            sources_processed += 1

        except Exception as error:

            errors.append(
                {
                    "source_id": source.source_id,
                    "source": source.url,
                    "error": str(error),
                }
            )

    resources = process_batch(
        all_candidates,
        known_resource_ids,
    )

    return CrawlResult(
        sources_processed=(
            sources_processed
        ),

        candidates_found=len(
            all_candidates
        ),

        resources_created=len(
            resources
        ),

        resources=resources,

        errors=errors,
    )


def crawl_to_dict(
    result: CrawlResult,
) -> dict[str, Any]:
    """
    Convert crawl results into
    an API-friendly representation.
    """

    return {
        "protocol": "amule",

        "version": 1,

        "sources_processed": (
            result.sources_processed
        ),

        "candidates_found": (
            result.candidates_found
        ),

        "resources_created": (
            result.resources_created
        ),

        "resources": [
            resource_to_dict(
                resource
            )
            for resource
            in result.resources
        ],

        "errors": result.errors,
    }


if __name__ == "__main__":

    import json

    catalog = SourceCatalog()

    result = crawl_catalog(
        catalog
    )

    print(
        json.dumps(
            crawl_to_dict(
                result
            ),
            indent=2,
            ensure_ascii=False,
        )
    )
