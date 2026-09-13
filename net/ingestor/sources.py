"""Persistent source catalog for the aMule ingestor."""

from dataclasses import asdict, dataclass
import json
from pathlib import Path


@dataclass
class Source:
    source_id: str
    name: str
    url: str
    source_type: str = "rss"
    enabled: bool = True
    category: str = "general"
    description: str = ""


class SourceCatalog:
    def __init__(self, path: str | Path = "data/ingestor/sources.json"):
        self.path = Path(path)
        self.path.parent.mkdir(parents=True, exist_ok=True)
        if not self.path.exists():
            self.path.write_text("[]", encoding="utf-8")

    def _load(self) -> list[dict]:
        try:
            return json.loads(self.path.read_text(encoding="utf-8"))
        except (json.JSONDecodeError, OSError):
            return []

    def _save(self, items: list[dict]) -> None:
        tmp = self.path.with_suffix(".tmp")
        tmp.write_text(
            json.dumps(items, indent=2, ensure_ascii=False),
            encoding="utf-8",
        )
        tmp.replace(self.path)

    def list(self) -> list[Source]:
        return [Source(**item) for item in self._load()]

    def get(self, source_id: str) -> Source | None:
        return next((s for s in self.list() if s.source_id == source_id), None)

    def add(self, source: Source) -> Source:
        items = self._load()
        if any(x["source_id"] == source.source_id for x in items):
            raise ValueError("Source already exists.")
        items.append(asdict(source))
        self._save(items)
        return source

    def remove(self, source_id: str) -> bool:
        items = self._load()
        updated = [x for x in items if x["source_id"] != source_id]
        changed = len(updated) != len(items)
        if changed:
            self._save(updated)
        return changed

    def set_enabled(self, source_id: str, enabled: bool) -> Source:
        items = self._load()
        for item in items:
            if item["source_id"] == source_id:
                item["enabled"] = enabled
                self._save(items)
                return Source(**item)
        raise KeyError(source_id)
