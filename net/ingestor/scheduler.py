"""
aMule — Ingestion Scheduler

Runs the aMule ingestion pipeline periodically and keeps
persistent ingestion state between executions.
"""

from __future__ import annotations

import logging
import time
from datetime import datetime, timezone
from typing import Callable

from net.ingestor.crawler import crawl_catalog
from net.ingestor.sources import SourceCatalog
from net.ingestor.state import IngestionState


logger = logging.getLogger("amule.ingestor")


class IngestionScheduler:
    """
    Periodically executes the aMule ingestion pipeline.
    """

    def __init__(
        self,
        catalog: SourceCatalog,
        state: IngestionState | None = None,
        interval_seconds: int = 900,
        on_resources: Callable | None = None,
    ):
        if interval_seconds < 60:
            raise ValueError(
                "interval_seconds must be at least 60 seconds."
            )

        self.catalog = catalog

        self.state = (
            state
            if state is not None
            else IngestionState()
        )

        self.interval_seconds = interval_seconds
        self.on_resources = on_resources

        self.running = False

    def run_once(self):
        """
        Execute one ingestion cycle.
        """

        started_at = datetime.now(
            timezone.utc
        )

        logger.info(
            "Starting aMule ingestion cycle."
        )

        known_resource_ids = set(
            self.state.resource_ids
        )

        result = crawl_catalog(
            self.catalog,
            known_resource_ids,
        )

        if result.resources:

            self.state.add_many(
                [
                    resource.resource_id
                    for resource in result.resources
                ]
            )

            if self.on_resources:

                self.on_resources(
                    result.resources
                )

        finished_at = datetime.now(
            timezone.utc
        )

        duration = (
            finished_at - started_at
        ).total_seconds()

        logger.info(
            "Ingestion cycle completed: "
            "sources=%s candidates=%s "
            "new_resources=%s errors=%s "
            "duration=%.2fs",
            result.sources_processed,
            result.candidates_found,
            result.resources_created,
            len(result.errors),
            duration,
        )

        for error in result.errors:

            logger.warning(
                "Source error: %s",
                error,
            )

        return result

    def start(self):
        """
        Start the scheduler loop.
        """

        if self.running:
            return

        self.running = True

        logger.info(
            "aMule ingestion scheduler started."
        )

        logger.info(
            "Interval: %s seconds.",
            self.interval_seconds,
        )

        logger.info(
            "Known resources: %s",
            self.state.count(),
        )

        while self.running:

            try:

                self.run_once()

            except Exception:

                logger.exception(
                    "Unexpected ingestion error."
                )

            if not self.running:
                break

            time.sleep(
                self.interval_seconds
            )

    def stop(self):
        """
        Stop the scheduler.
        """

        self.running = False

        logger.info(
            "aMule ingestion scheduler stopped."
        )


def create_scheduler(
    catalog: SourceCatalog | None = None,
    state: IngestionState | None = None,
    interval_seconds: int = 900,
    on_resources: Callable | None = None,
) -> IngestionScheduler:
    """
    Create a configured scheduler.
    """

    if catalog is None:
        catalog = SourceCatalog()

    if state is None:
        state = IngestionState()

    return IngestionScheduler(
        catalog=catalog,
        state=state,
        interval_seconds=interval_seconds,
        on_resources=on_resources,
    )


if __name__ == "__main__":

    logging.basicConfig(
        level=logging.INFO,
        format=(
            "%(asctime)s "
            "%(levelname)s "
            "%(name)s "
            "%(message)s"
        ),
    )

    scheduler = create_scheduler(
        interval_seconds=900
    )

    try:

        scheduler.start()

    except KeyboardInterrupt:

        scheduler.stop()

        print(
            "aMule scheduler stopped."
        )
