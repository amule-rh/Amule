"""Small registry abstraction used by the API.

Blockchain publication is deliberately optional in the MVP. The native
Robinhood Chain SDK in net/sdk can be used when a registry is deployed.
"""


class RegistryNotConfigured(RuntimeError):
    pass


class RegistryAdapter:
    def __init__(self, address: str | None = None):
        self.address = address

    @property
    def configured(self) -> bool:
        return bool(self.address)
