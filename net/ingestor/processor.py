"""
aMule — Resource Processor

Transforms ingested candidates into normalized aMule Resources.

Identity model:

    resource_id
        Stable logical identity of the resource.

    content_hash
        SHA-256 fingerprint of the exact resource content.

A resource can therefore keep the same resource_id
while its content_hash changes between versions.

Pipeline:

    Ingestor
       ↓
    Normalize
       ↓
    Identity
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
    resource_id: str

    title: str
    content: str

    content_hash: str

    resource_type: str

    source_url: str | None
    source_feed: str | None

    created_at: str

    metadata: dict[str, Any]


def normalize_text(
    text: str,
) -> str:
    """
    Normalize text without changing its meaning.

    Removes:
    - null bytes
    - excessive whitespace

    The normalized result is what the MVP
    considers the canonical textual content.
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
    content: str,
) -> str:
    """
    Calculate SHA-256 of the canonical content.

    IMPORTANT:

    Metadata such as title, URL, source or filename
    must NOT affect content identity.
    """

    normalized_content = normalize_text(
        content,
    )

    return hashlib.sha256(
        normalized_content.encode(
            "utf-8",
        )
    ).hexdigest()


def create_resource_id(
    candidate: dict[str, Any],
) -> str:
    """
    Create a deterministic logical Resource ID.

    Preferred identity:

        source namespace
        +
        stable external identifier

    For RSS resources the stable identifier should
    normally be the feed item GUID.

    If no GUID exists, the item URL is used.

    This ID is intentionally different from content_hash.
    """

    source = candidate.get(
        "source",
        {},
    )

    if not isinstance(
        source,
        dict,
    ):
        source = {}

    source_namespace = (
        source.get("feed")
        or source.get("url")
        or candidate.get("source_id")
        or "unknown"
    )

    stable_id = (
        candidate.get("stable_id")
        or candidate.get("guid")
        or source.get("guid")
        or source.get("url")
    )

    if not stable_id:
        raise ValueError(
            "Stable resource identifier is required."
        )

    canonical = (
        "amule-resource-v1\n"
        f"{source_namespace}\n"
        f"{stable_id}"
    )

    return hashlib.sha256(
        canonical.encode(
            "utf-8",
        )
    ).hexdigest()


def process_candidate(
    candidate: dict[str, Any],
) -> ProcessedResource:
    """
    Convert an ingestion candidate into
    a normalized ProcessedResource.
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
        "url",
    )

    source_feed = source.get(
        "feed",
    )

    content_hash = calculate_content_hash(
        content,
    )

    resource_id = create_resource_id(
        candidate,
    )

    metadata = {
        "source": source,

        "ingestor": candidate.get(
            "ingestor",
            "unknown",
        ),

        "source_id": candidate.get(
            "source_id",
        ),

        "source_name": candidate.get(
            "source_name",
        ),

        "category": candidate.get(
            "category",
        ),

        "original_resource_id": candidate.get(
            "resource_id",
        ),

        "stable_id": (
            candidate.get(
                "stable_id",
            )
            or candidate.get(
                "guid",
            )
            or source.get(
                "guid",
            )
            or source.get(
                "url",
            )
        ),

        "content_length": len(
            content,
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
            timezone.utc,
        ).isoformat(),

        metadata=metadata,
    )


def resource_to_dict(
    resource: ProcessedResource,
) -> dict[str, Any]:
    """
    Convert a ProcessedResource into the
    canonical aMule resource representation.
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
    Check whether a logical resource is already known.
    """

    if not resource_id:
        return False

    return resource_id in known_resource_ids


def process_batch(
    candidates: list[dict[str, Any]],
    known_resource_ids: set[str] | None = None,
) -> list[ProcessedResource]:
    """
    Process multiple candidates while avoiding
    duplicate logical Resource IDs.
    """

    if known_resource_ids is None:
        known_resource_ids = set()

    processed: list[
        ProcessedResource
    ] = []

    for candidate in candidates:

        try:
            resource = process_candidate(
                candidate,
            )

        except ValueError:
            continue

        if is_duplicate(
            resource.resource_id,
            known_resource_ids,
        ):
            continue

        known_resource_ids.add(
            resource.resource_id,
        )

        processed.append(
            resource,
        )

    return processed


if __name__ == "__main__":

    example_candidate = {
        "protocol": "amule",

        "version": 1,

        "type": "article",

        "title": "Example AI Resource",

        "content": (
            "This is an example resource "
            "processed by aMule."
        ),

        "stable_id": "example-article-001",

        "source": {
            "url": (
                "https://example.com/article"
            ),

            "feed": (
                "https://example.com/rss"
            ),
        },
    }

    resource = process_candidate(
        example_candidate,
    )

    print(
        "aMule processor: OK"
    )

    print(
        resource_to_dict(
            resource,
        )
    )
