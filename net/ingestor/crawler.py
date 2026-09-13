"""HTTP crawler for configured RSS/Atom sources."""

from dataclasses import dataclass
from urllib.request import Request, urlopen

from .processor import process_batch
from .rss import parse_feed
from .sources import SourceCatalog


@dataclass
class CrawlResult:
    source_id: str
    fetched: int
    candidates: list[dict]
    error: str | None = None


def crawl_source(source) -> CrawlResult:
    try:
        request = Request(
            source.url,
            headers={"User-Agent": "aMule-Net/0.1 (+https://amule.onrender.com)"},
        )
        with urlopen(request, timeout=20) as response:
            payload = response.read()

        items = parse_feed(payload, source.url)
        return CrawlResult(
            source_id=source.source_id,
            fetched=len(items),
            candidates=process_batch(items),
        )
    except Exception as exc:
        return CrawlResult(
            source_id=source.source_id,
            fetched=0,
            candidates=[],
            error=str(exc),
        )


def crawl_enabled_sources(catalog: SourceCatalog | None = None) -> list[CrawlResult]:
    catalog = catalog or SourceCatalog()
    return [crawl_source(source) for source in catalog.list() if source.enabled]
