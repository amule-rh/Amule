"""RSS/Atom ingestion helpers."""

from dataclasses import dataclass
from datetime import datetime, timezone
import hashlib
import re
import xml.etree.ElementTree as ET


@dataclass
class RSSItem:
    stable_id: str
    title: str
    content: str
    url: str
    published_at: str | None
    source_url: str


def clean_text(value: str | None) -> str:
    if not value:
        return ""
    value = re.sub(r"<[^>]+>", " ", value)
    value = re.sub(r"\s+", " ", value)
    return value.strip()


def _child_text(node, names):
    for name in names:
        child = node.find(name)
        if child is not None and child.text:
            return child.text.strip()
    return ""


def parse_feed(xml_bytes: bytes, source_url: str) -> list[RSSItem]:
    root = ET.fromstring(xml_bytes)
    items = root.findall(".//item") or root.findall(".//{http://www.w3.org/2005/Atom}entry")
    results = []

    for node in items:
        title = clean_text(_child_text(node, ["title", "{http://www.w3.org/2005/Atom}title"]))
        description = clean_text(_child_text(node, [
            "description",
            "content",
            "{http://www.w3.org/2005/Atom}summary",
            "{http://www.w3.org/2005/Atom}content",
        ]))

        guid = clean_text(_child_text(node, [
            "guid",
            "{http://www.w3.org/2005/Atom}id",
        ]))

        url = _child_text(node, ["link"])
        if not url:
            atom_link = node.find("{http://www.w3.org/2005/Atom}link")
            if atom_link is not None:
                url = atom_link.attrib.get("href", "")

        stable_id = guid or url or hashlib.sha256(
            f"{source_url}\n{title}\n{description}".encode()
        ).hexdigest()

        published = _child_text(node, [
            "pubDate",
            "{http://www.w3.org/2005/Atom}published",
            "{http://www.w3.org/2005/Atom}updated",
        ]) or None

        results.append(RSSItem(
            stable_id=stable_id,
            title=title,
            content=description,
            url=url,
            published_at=published,
            source_url=source_url,
        ))

    return results


def now_iso() -> str:
    return datetime.now(timezone.utc).isoformat()
