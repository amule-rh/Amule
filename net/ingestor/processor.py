"""
aMule — Resource Processor

Transforms ingested data into normalized aMule Resources.

Pipeline:

    Ingestor
       ↓
    Processor
       ↓
    Normalize
       ↓
    Deduplicate
       ↓
    Resource
"""

from __future__ import annotations

import hashlib
import re
from dataclasses import dataclass
from datetime import datetime, timezone
from typing import Any


@dataclass
class ProcessedResource:
    """
    Canonical aMule resource produced by the processor.
    """

    resource_id: str
    title: str
    content: str
    content_hash: str
    resource_type: str
    source_url: str | None
    source_feed: str | None
    created_at: str
    metadata: dict[str, Any]


def normalize_text(text: str) -> str:
    """
    Normalize whitespace and remove unnecessary control characters.
    """

    if not text:
        return ""

    text = text.replace(
        "\x00",
        "",
    )

    text = re.sub(
        r"\s+",
        " ",
        text,
    )

    return text.strip()


def calculate_content_hash(
    title: str,
    content: str,
) -> str:
    """
    Generate a deterministic SHA-256 hash
    from normalized resource content.
    """

    normalized = (
        f"{normalize_text(title)}\n"
        f"{normalize_text(content)}"
    )

    return hashlib.sha256(
        normalized.encode("utf-8")
    ).hexdigest()


def process_candidate(
    candidate: dict[str, Any],
) -> ProcessedResource:
    """
    Convert an ingestor candidate into
    a canonical aMule Resource.
    """

    if not candidate:
        raise ValueError(
            "Resource candidate is required."
        )

    title = normalize_text(
        str(
            candidate.get(
                "title",
                "",
            )
        )
    )

    content = normalize_text(
        str(
            candidate.get(
                "content",
                "",
            )
        )
    )

    if not title:
        raise ValueError(
            "Resource title is required."
        )

    if not content:
        raise ValueError(
            "Resource content is required."
        )

    source = candidate.get(
        "source",
        {},
    )

    if not isinstance(
        source,
        dict,
    ):
        source = {}

    source_url = source.get(
        "url"
    )

    source_feed = source.get(
        "feed"
    )

    content_hash = calculate_content_hash(
        title,
        content,
    )

    resource_id = content_hash

    metadata = {
        "source": source,
        "ingestor": candidate.get(
            "ingestor",
            "unknown",
        ),
        "original_resource_id": candidate.get(
            "resource_id"
        ),
        "content_length": len(
            content
        ),
    }

    return ProcessedResource(
        resource_id=resource_id,
        title=title,
        content=content,
        content_hash=content_hash,
        resource_type=candidate.get(
            "type",
            "unknown",
        ),
        source_url=source_url,
        source_feed=source_feed,
        created_at=datetime.now(
            timezone.utc
        ).isoformat(),
        metadata=metadata,
    )


def resource_to_dict(
    resource: ProcessedResource,
) -> dict[str, Any]:
    """
    Serialize a processed resource
    into the canonical aMule format.
    """

    return {
        "protocol": "amule",
        "version": 1,
        "resource_id": resource.resource_id,
        "type": resource.resource_type,
        "title": resource.title,
        "content": resource.content,
        "content_hash": resource.content_hash,
        "source": {
            "url": resource.source_url,
            "feed": resource.source_feed,
        },
        "created_at": resource.created_at,
        "metadata": resource.metadata,
        "status": "processed",
    }


def is_duplicate(
    resource_id: str,
    known_resource_ids: set[str],
) -> bool:
    """
    Check whether a resource has already
    been processed.
    """

    if not resource_id:
        return False

    return resource_id in known_resource_ids


def process_batch(
    candidates: list[dict[str, Any]],
    known_resource_ids: set[str] | None = None,
) -> list[ProcessedResource]:
    """
    Process multiple candidates.

    Invalid and duplicate resources are skipped.
    """

    if known_resource_ids is None:
        known_resource_ids = set()

    processed: list[ProcessedResource] = []

    for candidate in candidates:

        try:

            resource = process_candidate(
                candidate
            )

        except ValueError:
            continue

        if is_duplicate(
            resource.resource_id,
            known_resource_ids,
        ):
            continue

        known_resource_ids.add(
            resource.resource_id
        )

        processed.append(
            resource
        )

    return processed


if __name__ == "__main__":

    example_candidate = {
        "protocol": "amule",
        "version": 1,
        "resource_id": "temporary",
        "type": "article",
        "title": "Example AI Resource",
        "content": (
            "This is an example resource "
            "processed by aMule."
        ),
        "source": {
            "url": "https://example.com/article",
            "feed": "https://example.com/rss",
        },
    }

    resource = process_candidate(
        example_candidate
    )

    print(
        "aMule processor: OK"
    )

    print(
        resource_to_dict(resource)
    )
