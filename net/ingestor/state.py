"""Persistent processed-resource state."""

import json
from pathlib import Path


class IngestorState:
    def __init__(self, path: str | Path = "data/ingestor/state.json"):
        self.path = Path(path)
        self.path.parent.mkdir(parents=True, exist_ok=True)
        if not self.path.exists():
            self.path.write_text("[]", encoding="utf-8")

    def _load(self) -> set[str]:
        try:
            return set(json.loads(self.path.read_text(encoding="utf-8")))
        except (OSError, json.JSONDecodeError):
            return set()

    def contains(self, resource_id: str) -> bool:
        return resource_id in self._load()

    def add(self, resource_id: str) -> None:
        items = self._load()
        items.add(resource_id)
        tmp = self.path.with_suffix(".tmp")
        tmp.write_text(json.dumps(sorted(items)), encoding="utf-8")
        tmp.replace(self.path)
