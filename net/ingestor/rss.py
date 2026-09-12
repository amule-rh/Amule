"""
aMule — RSS Ingestor

Reads RSS/Atom feeds and converts new articles into
standardized aMule resource candidates.

This module does not publish anything to the blockchain.
It only performs ingestion.

Pipeline:

    RSS Feed
       ↓
    Fetch
       ↓
    Parse
       ↓
    Normalize
       ↓
    Resource Candidate
"""

from __future__ import annotations

import hashlib
import html
import re
import urllib.request
import xml.etree.ElementTree as ET

from dataclasses import dataclass
from datetime import datetime, timezone
from typing import Optional


USER_AGENT = "aMule-Ingestor/0.1"


@dataclass
class RSSItem:
    """
    Normalized RSS/Atom item.
    """

    title: str
    url: str
    description: str
    published_at: Optional[str]
    source_url: str
    content_hash: str


def _clean_text(value: Optional[str]) -> str:
    """
    Remove HTML and normalize whitespace.
    """

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


def _content_hash(
    title: str,
    url: str,
    description: str,
) -> str:
    """
    Generate a deterministic SHA-256 hash for an item.
    """

    normalized = (
        f"{title}\n"
        f"{url}\n"
        f"{description}"
    ).encode("utf-8")

    return hashlib.sha256(
        normalized
    ).hexdigest()


def _fetch_feed(
    feed_url: str,
    timeout: int = 20,
) -> bytes:
    """
    Download an RSS/Atom feed.
    """

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
    """
    Find text from an XML element using multiple possible tags.
    """

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
    """
    Extract a link from RSS or Atom.
    """

    # Standard RSS <link>
    rss_link = element.find(
        "./{*}link"
    )

    if rss_link is not None:

        if rss_link.text:
            return rss_link.text.strip()

        href = rss_link.attrib.get("href")

        if href:
            return href.strip()

    # Atom <link href="...">
    for link in element.findall(
        "./{*}link"
    ):

        href = link.attrib.get("href")

        if href:
            relation = link.attrib.get(
                "rel",
                "alternate",
            )

            if relation == "alternate":
                return href.strip()

    return ""


def _parse_feed(
    xml_data: bytes,
    source_url: str,
) -> list[RSSItem]:
    """
    Parse RSS or Atom XML.
    """

    root = ET.fromstring(
        xml_data
    )

    items: list[RSSItem] = []

    # RSS <item>
    xml_items = root.findall(
        ".//{*}item"
    )

    # Atom <entry>
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

        content_hash = _content_hash(
            title,
            url,
            description,
        )

        items.append(
            RSSItem(
                title=title,
                url=url,
                description=description,
                published_at=published or None,
                source_url=source_url,
                content_hash=content_hash,
            )
        )

    return items


def ingest_rss(
    feed_url: str,
    timeout: int = 20,
) -> list[RSSItem]:
    """
    Fetch and parse an RSS/Atom feed.

    Returns normalized aMule resource candidates.
    """

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
    """
    Convert an RSS item into the initial
    aMule Resource representation.
    """

    return {
        "protocol": "amule",
        "version": 1,
        "resource_id": item.content_hash,
        "type": "article",
        "title": item.title,
        "content": item.description,
        "source": {
            "url": item.url,
            "feed": item.source_url,
            "published_at": item.published_at,
        },
        "content_hash": item.content_hash,
        "ingested_at": datetime.now(
            timezone.utc
        ).isoformat(),
        "status": "candidate",
    }


if __name__ == "__main__":

    import sys

    if len(sys.argv) != 2:

        print(
            "Usage: python net/ingestor/rss.py <RSS_URL>"
        )

        raise SystemExit(1)

    feed_url = sys.argv[1]

    items = ingest_rss(
        feed_url
    )

    print(
        f"aMule RSS ingestion: {len(items)} items"
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
            "Hash:",
            item.content_hash,
        )
