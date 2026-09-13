"""Normalize ingested items and create protocol resource candidates."""

from hashlib import sha256
import json
import re


def normalize_text(value: str) -> str:
    return re.sub(r"\s+", " ", (value or "")).strip()


def calculate_content_hash(content: bytes) -> str:
    return sha256(content).hexdigest()


def create_resource_id(namespace: str, stable_id: str) -> str:
    return sha256(
        f"{namespace}\n{stable_id}".encode("utf-8")
    ).hexdigest()


def process_item(item) -> dict:
    title = normalize_text(item.title)
    content = normalize_text(item.content)
    body = content or title
    exact_bytes = body.encode("utf-8")

    resource_id = create_resource_id(item.source_url, item.stable_id)
    content_hash = calculate_content_hash(exact_bytes)

    return {
        "protocol": "amule",
        "version": 1,
        "resource_id": resource_id,
        "content_hash": content_hash,
        "type": "article",
        "title": title,
        "content": body,
        "source": {
            "url": item.url,
            "feed": item.source_url,
            "published_at": item.published_at,
            "stable_id": item.stable_id,
        },
        "metadata": {
            "content_encoding": "utf-8",
            "content_bytes": len(exact_bytes),
        },
        "status": "candidate",
    }


def process_batch(items) -> list[dict]:
    results = []
    seen = set()

    for item in items:
        candidate = process_item(item)
        if candidate["resource_id"] in seen:
            continue
        seen.add(candidate["resource_id"])
        results.append(candidate)

    return results


def serialize_candidate(candidate: dict) -> str:
    return json.dumps(candidate, ensure_ascii=False, indent=2)
