"""
aMule — RSS / Atom Ingestor

Converts RSS/Atom items into aMule resource candidates.

Identity model:

    stable_id
        ↓
    logical resource_id (created by processor)

    content
        ↓
    content_hash (created by processor)

The ingestor does NOT calculate the final content hash.
"""

from __future__ import annotations

import html
import re
import urllib.request
import xml.etree.ElementTree as ET

from dataclasses import dataclass
from typing import Optional


USER_AGENT = "aMule-Ingestor/0.1"


@dataclass
class RSSItem:
    title: str
    url: str
    description: str
    published_at: Optional[str]

    source_url: str

    stable_id: str


def _clean_text(
    value: Optional[str],
) -> str:
    if not value:
        return ""

    value = html.unescape(value)

    value = re.sub(
        r"<[^>]+>",
        " ",
        value,
    )

    value = re.sub(
        r"\s+",
        " ",
        value,
    )

    return value.strip()


def _fetch_feed(
    feed_url: str,
    timeout: int = 20,
) -> bytes:

    request = urllib.request.Request(
        feed_url,
        headers={
            "User-Agent": USER_AGENT,
            "Accept": (
                "application/rss+xml,"
                "application/atom+xml,"
                "application/xml,"
                "text/xml"
            ),
        },
    )

    with urllib.request.urlopen(
        request,
        timeout=timeout,
    ) as response:
        return response.read()


def _find_text(
    element: ET.Element,
    names: tuple[str, ...],
) -> str:

    for name in names:

        child = element.find(
            f".//{{*}}{name}"
        )

        if child is not None:

            text = "".join(
                child.itertext()
            )

            if text.strip():
                return text.strip()

    return ""


def _find_link(
    element: ET.Element,
) -> str:

    links = element.findall(
        "./{*}link"
    )

    # RSS
    for link in links:

        if link.text:

            value = link.text.strip()

            if value.startswith(
                ("http://", "https://")
            ):
                return value

    # Atom
    for link in links:

        href = link.attrib.get(
            "href"
        )

        if not href:
            continue

        relation = link.attrib.get(
            "rel",
            "alternate",
        )

        if relation == "alternate":
            return href.strip()

    # Final fallback
    for link in links:

        href = link.attrib.get(
            "href"
        )

        if href:
            return href.strip()

    return ""


def _find_guid(
    element: ET.Element,
) -> str:

    # RSS guid
    guid = element.find(
        "./{*}guid"
    )

    if guid is not None:

        if guid.text:
            value = guid.text.strip()

            if value:
                return value

    # Atom id
    atom_id = element.find(
        "./{*}id"
    )

    if atom_id is not None:

        if atom_id.text:
            value = atom_id.text.strip()

            if value:
                return value

    return ""


def _parse_feed(
    xml_data: bytes,
    source_url: str,
) -> list[RSSItem]:

    root = ET.fromstring(
        xml_data
    )

    items: list[RSSItem] = []

    xml_items = root.findall(
        ".//{*}item"
    )

    if not xml_items:

        xml_items = root.findall(
            ".//{*}entry"
        )

    for item in xml_items:

        title = _clean_text(
            _find_text(
                item,
                ("title",),
            )
        )

        url = _find_link(
            item
        )

        description = _clean_text(
            _find_text(
                item,
                (
                    "description",
                    "summary",
                    "content",
                ),
            )
        )

        published = _clean_text(
            _find_text(
                item,
                (
                    "pubDate",
                    "published",
                    "updated",
                ),
            )
        )

        if not title or not url:
            continue

        guid = _find_guid(
            item
        )

        # Prefer the publisher's GUID.
        #
        # If no GUID exists, the canonical URL
        # becomes the stable external identity.
        stable_id = (
            guid
            or url
        )

        items.append(
            RSSItem(
                title=title,
                url=url,
                description=description,
                published_at=(
                    published
                    or None
                ),
                source_url=source_url,
                stable_id=stable_id,
            )
        )

    return items


def ingest_rss(
    feed_url: str,
    timeout: int = 20,
) -> list[RSSItem]:

    if not feed_url:
        raise ValueError(
            "feed_url is required."
        )

    xml_data = _fetch_feed(
        feed_url,
        timeout=timeout,
    )

    return _parse_feed(
        xml_data,
        feed_url,
    )


def resource_candidate(
    item: RSSItem,
) -> dict:

    return {
        "protocol": "amule",

        "version": 1,

        "resource_id": None,

        "stable_id": item.stable_id,

        "type": "article",

        "title": item.title,

        "content": item.description,

        "source": {
            "url": item.url,
            "feed": item.source_url,
            "published_at": item.published_at,
        },

        "status": "candidate",
    }


if __name__ == "__main__":

    import sys

    if len(sys.argv) != 2:

        print(
            "Usage: "
            "python net/ingestor/rss.py "
            "<RSS_URL>"
        )

        raise SystemExit(1)

    feed_url = sys.argv[1]

    items = ingest_rss(
        feed_url
    )

    print(
        f"aMule RSS ingestion: "
        f"{len(items)} items"
    )

    for item in items:

        print()

        print(
            "Title:",
            item.title,
        )

        print(
            "URL:",
            item.url,
        )

        print(
            "Stable ID:",
            item.stable_id,
        )
