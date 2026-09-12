"""
aMule — Ingestion State

Persistent state for the ingestion pipeline.

Stores resource IDs that have already been processed so
aMule can avoid re-ingesting the same resources after
a restart.

Current backend:
    Local JSON file

Future backend:
    Database
    Distributed state
    On-chain registry
"""

from __future__ import annotations

import json

from pathlib import Path


DEFAULT_STATE_PATH = Path(
    "data/ingestor/state.json"
)


class IngestionState:
    """
    Persistent registry of processed resource IDs.
    """

    def __init__(
        self,
        path: Path = DEFAULT_STATE_PATH,
    ):
        self.path = Path(path)

        self.resource_ids: set[str] = set()

        self._load()

    def _load(self) -> None:
        """
        Load previously processed resource IDs.
        """

        if not self.path.exists():
            return

        try:

            data = json.loads(
                self.path.read_text(
                    encoding="utf-8"
                )
            )

        except (
            OSError,
            json.JSONDecodeError,
        ):

            return

        if not isinstance(
            data,
            list,
        ):
            return

        self.resource_ids = {
            str(resource_id)
            for resource_id in data
            if resource_id
        }

    def _save(self) -> None:
        """
        Persist processed resource IDs.
        """

        self.path.parent.mkdir(
            parents=True,
            exist_ok=True,
        )

        self.path.write_text(
            json.dumps(
                sorted(
                    self.resource_ids
                ),
                indent=2,
            ),
            encoding="utf-8",
        )

    def contains(
        self,
        resource_id: str,
    ) -> bool:
        """
        Check whether a resource was already processed.
        """

        return resource_id in self.resource_ids

    def add(
        self,
        resource_id: str,
    ) -> None:
        """
        Mark a resource as processed.
        """

        if not resource_id:
            return

        if resource_id in self.resource_ids:
            return

        self.resource_ids.add(
            resource_id
        )

        self._save()

    def add_many(
        self,
        resource_ids: list[str],
    ) -> None:
        """
        Mark multiple resources as processed.
        """

        changed = False

        for resource_id in resource_ids:

            if not resource_id:
                continue

            if (
                resource_id
                not in self.resource_ids
            ):

                self.resource_ids.add(
                    resource_id
                )

                changed = True

        if changed:
            self._save()

    def remove(
        self,
        resource_id: str,
    ) -> bool:
        """
        Remove a resource from the processed state.
        """

        if resource_id not in self.resource_ids:
            return False

        self.resource_ids.remove(
            resource_id
        )

        self._save()

        return True

    def clear(self) -> None:
        """
        Clear the complete ingestion state.
        """

        self.resource_ids.clear()

        self._save()

    def count(self) -> int:
        """
        Return the number of processed resources.
        """

        return len(
            self.resource_ids
        )


if __name__ == "__main__":

    state = IngestionState()

    print(
        "aMule ingestion state"
    )

    print(
        "Processed resources:",
        state.count(),
    )
