"""
aMule — Source Crawler

Orchestrates multiple external information sources.

Current source:
    RSS / Atom

Future sources:
    Web
    GitHub
    APIs
    Documents
    Agent submissions

Pipeline:

    Sources
       ↓
    Crawler
       ↓
    Ingestor
       ↓
    Processor
       ↓
    Processed Resources
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


@dataclass
class CrawlResult:
    """
    Result of a crawler execution.
    """

    sources_processed: int
    candidates_found: int
    resources_created: int
    resources: list[ProcessedResource]
    errors: list[dict[str, str]]


def crawl_rss_source(
    feed_url: str,
) -> list[dict[str, Any]]:
    """
    Ingest a single RSS/Atom source and convert
    its items into resource candidates.
    """

    items = ingest_rss(
        feed_url
    )

    candidates = []

    for item in items:

        candidate = resource_candidate(
            item
        )

        candidate["ingestor"] = "rss"

        candidates.append(
            candidate
        )

    return candidates


def crawl_sources(
    sources: list[str],
    known_resource_ids: set[str] | None = None,
) -> CrawlResult:
    """
    Crawl multiple RSS/Atom sources.

    Sources that fail do not stop the entire crawl.
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

    for source in sources:

        if not source:
            continue

        try:

            candidates = crawl_rss_source(
                source
            )

            all_candidates.extend(
                candidates
            )

            sources_processed += 1

        except Exception as error:

            errors.append(
                {
                    "source": source,
                    "error": str(error),
                }
            )

    resources = process_batch(
        all_candidates,
        known_resource_ids,
    )

    return CrawlResult(
        sources_processed=sources_processed,
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
    Convert crawler results into
    an API-friendly structure.
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
            for resource in result.resources
        ],
        "errors": result.errors,
    }


if __name__ == "__main__":

    import json
    import sys

    if len(sys.argv) < 2:

        print(
            "Usage:"
        )

        print(
            "python net/ingestor/crawler.py <RSS_URL> [RSS_URL...]"
        )

        raise SystemExit(1)

    sources = sys.argv[1:]

    result = crawl_sources(
        sources
    )

    print(
        json.dumps(
            crawl_to_dict(result),
            indent=2,
            ensure_ascii=False,
        )
    )
