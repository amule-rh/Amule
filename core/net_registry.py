"""
aMule — Net Protocol Registry

Decentralized resource registry abstraction.

This module keeps the aMule application independent from
the underlying Net Protocol SDK.

Current MVP:
- Build deterministic resource metadata
- Prepare records for decentralized registration
- Keep Net integration isolated from the API

Future:
- Publish records through Net Protocol
- Query decentralized resource indexes
- Resolve resources by content hash
"""

from __future__ import annotations

import json
from datetime import datetime, timezone
from typing import Any


AMULE_PROTOCOL = "amule"
REGISTRY_VERSION = 1


def build_resource_record(
    *,
    name: str,
    content_hash: str,
    size: int,
    content_type: str,
    encrypted: bool = True,
    provider: str | None = None,
) -> dict[str, Any]:
    """
    Build the canonical metadata record for an aMule resource.

    The actual file is NOT stored here.

    This record is intended to become the decentralized
    discovery/index layer of aMule.
    """

    return {
        "protocol": AMULE_PROTOCOL,
        "version": REGISTRY_VERSION,
        "name": name,
        "contentHash": content_hash,
        "size": size,
        "contentType": content_type,
        "encrypted": encrypted,
        "provider": provider,
        "createdAt": datetime.now(
            timezone.utc
        ).isoformat(),
    }


def serialize_resource_record(
    record: dict[str, Any],
) -> str:
    """
    Serialize a resource record deterministically.

    Deterministic serialization is important because
    the same metadata should produce the same payload.
    """

    return json.dumps(
        record,
        sort_keys=True,
        separators=(",", ":"),
    )


def validate_resource_record(
    record: dict[str, Any],
) -> bool:
    """
    Validate the minimum structure required by aMule.
    """

    required_fields = {
        "protocol",
        "version",
        "name",
        "contentHash",
        "size",
        "contentType",
        "encrypted",
        "createdAt",
    }

    if not required_fields.issubset(record):
        return False

    if record["protocol"] != AMULE_PROTOCOL:
        return False

    if record["version"] != REGISTRY_VERSION:
        return False

    if not isinstance(record["contentHash"], str):
        return False

    if len(record["contentHash"]) != 64:
        return False

    if not isinstance(record["size"], int):
        return False

    if record["size"] < 0:
        return False

    return True


if __name__ == "__main__":

    record = build_resource_record(
        name="README.md",
        content_hash=(
            "462108affe0000000000000000000000000000000000000000000000"
            "c2adf9f9"
        ),
        size=9088,
        content_type="text/markdown",
    )

    print(
        serialize_resource_record(record)
    )

    print(
        "Valid:",
        validate_resource_record(record),
    )
