"""Simple polling scheduler for local development."""

import time

from .crawler import crawl_enabled_sources


def run(interval_seconds: int = 900, callback=None):
    while True:
        results = crawl_enabled_sources()
        if callback:
            callback(results)
        time.sleep(interval_seconds)
