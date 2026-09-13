from .sources import Source, SourceCatalog


class SourceAPI:
    def __init__(self, catalog: SourceCatalog | None = None):
        self.catalog = catalog or SourceCatalog()

    def list_sources(self):
        return self.catalog.list()

    def add_source(self, **kwargs):
        return self.catalog.add(Source(**kwargs))

    def delete_source(self, source_id: str):
        return self.catalog.remove(source_id)

    def enable(self, source_id: str):
        return self.catalog.set_enabled(source_id, True)

    def disable(self, source_id: str):
        return self.catalog.set_enabled(source_id, False)
