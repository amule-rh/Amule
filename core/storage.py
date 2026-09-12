"""
aMule — Storage Core

Storage abstraction for aMule.

The application does not talk directly to a filesystem or
blockchain storage provider.

Instead:

    API
      ↓
    Storage Core
      ↓
    Storage Backend

Current backend:
    LocalStorageBackend

Future backend:
    NetStorageBackend

This architecture allows aMule to move from local development
storage to permanent Net Storage without changing the API layer.
"""

from __future__ import annotations

from pathlib import Path
from typing import Protocol

from core.encryption import decrypt_data, encrypt_data
from core.hashing import hash_data


# =========================================================
# LOCAL STORAGE PATH
# =========================================================

STORAGE_DIR = Path("data/storage")


# =========================================================
# STORAGE BACKEND INTERFACE
# =========================================================

class StorageBackend(Protocol):
    """
    Generic storage backend.

    Any storage provider used by aMule must implement these
    operations.
    """

    def put(
        self,
        resource_id: str,
        data: bytes,
    ) -> None:
        """Store encrypted resource data."""
        ...

    def get(
        self,
        resource_id: str,
    ) -> bytes:
        """Retrieve encrypted resource data."""
        ...

    def exists(
        self,
        resource_id: str,
    ) -> bool:
        """Check whether a resource exists."""
        ...


# =========================================================
# RESOURCE ID VALIDATION
# =========================================================

def _validate_resource_id(
    resource_id: str,
) -> None:
    """
    Validate a resource identifier.

    aMule resource IDs are SHA-256 hashes and therefore must
    contain exactly 64 hexadecimal characters.

    This also prevents path traversal attacks when using
    filesystem-based storage.
    """

    if not isinstance(resource_id, str):
        raise ValueError(
            "Resource ID must be a string."
        )

    if len(resource_id) != 64:
        raise ValueError(
            "Invalid resource ID."
        )

    if any(
        character not in "0123456789abcdef"
        for character in resource_id.lower()
    ):
        raise ValueError(
            "Invalid resource ID."
        )


# =========================================================
# LOCAL STORAGE BACKEND
# =========================================================

class LocalStorageBackend:
    """
    Local filesystem storage backend.

    Used for development and testing.

    This backend is intentionally isolated so it can later
    be replaced by Net Storage.
    """

    def __init__(
        self,
        root: Path = STORAGE_DIR,
    ):
        self.root = Path(root)

    # -----------------------------------------------------
    # INTERNAL
    # -----------------------------------------------------

    def _ensure_storage(self) -> None:
        """Create the storage directory if necessary."""

        self.root.mkdir(
            parents=True,
            exist_ok=True,
        )

    def _get_path(
        self,
        resource_id: str,
    ) -> Path:
        """Return the filesystem path for a resource."""

        _validate_resource_id(resource_id)

        return self.root / resource_id

    # -----------------------------------------------------
    # PUT
    # -----------------------------------------------------

    def put(
        self,
        resource_id: str,
        data: bytes,
    ) -> None:
        """Store encrypted resource data."""

        self._ensure_storage()

        resource_path = self._get_path(
            resource_id
        )

        resource_path.write_bytes(
            data
        )

    # -----------------------------------------------------
    # GET
    # -----------------------------------------------------

    def get(
        self,
        resource_id: str,
    ) -> bytes:
        """Retrieve encrypted resource data."""

        resource_path = self._get_path(
            resource_id
        )

        if not resource_path.exists():
            raise FileNotFoundError(
                "Resource not found."
            )

        return resource_path.read_bytes()

    # -----------------------------------------------------
    # EXISTS
    # -----------------------------------------------------

    def exists(
        self,
        resource_id: str,
    ) -> bool:
        """Check whether a resource exists."""

        resource_path = self._get_path(
            resource_id
        )

        return resource_path.exists()


# =========================================================
# ACTIVE STORAGE BACKEND
# =========================================================

_storage_backend: StorageBackend = (
    LocalStorageBackend()
)


def configure_storage_backend(
    backend: StorageBackend,
) -> None:
    """
    Configure the storage backend used by aMule.

    Example future usage:

        configure_storage_backend(
            NetStorageBackend(...)
        )
    """

    global _storage_backend

    _storage_backend = backend


def get_storage_backend() -> StorageBackend:
    """
    Return the currently configured storage backend.
    """

    return _storage_backend


# =========================================================
# STORE RESOURCE
# =========================================================

def store_resource(
    data: bytes,
    key: bytes,
) -> str:
    """
    Encrypt and store a resource.

    Flow:

        Raw data
           ↓
        Encryption
           ↓
        SHA-256
           ↓
        Storage Backend

    Returns:

        resource_id

    The resource ID is the SHA-256 hash of the encrypted
    content.
    """

    encrypted_data = encrypt_data(
        data,
        key,
    )

    resource_id = hash_data(
        encrypted_data
    )

    _storage_backend.put(
        resource_id,
        encrypted_data,
    )

    return resource_id


# =========================================================
# RETRIEVE RESOURCE
# =========================================================

def retrieve_resource(
    resource_id: str,
    key: bytes,
) -> bytes:
    """
    Retrieve and decrypt a resource.

    Flow:

        Storage Backend
              ↓
        Encrypted data
              ↓
        SHA-256 verification
              ↓
        Decryption
              ↓
        Original data
    """

    encrypted_data = _storage_backend.get(
        resource_id
    )

    calculated_id = hash_data(
        encrypted_data
    )

    if calculated_id != resource_id:
        raise ValueError(
            "Resource integrity check failed."
        )

    return decrypt_data(
        encrypted_data,
        key,
    )


# =========================================================
# DEVELOPMENT TEST
# =========================================================

if __name__ == "__main__":

    from core.encryption import generate_key

    print(
        "aMule storage backend:",
        type(_storage_backend).__name__,
    )

    original_data = (
        b"Hello from the aMule network!"
    )

    key = generate_key()

    resource_id = store_resource(
        original_data,
        key,
    )

    print(
        "Resource ID:",
        resource_id,
    )

    recovered_data = retrieve_resource(
        resource_id,
        key,
    )

    assert recovered_data == original_data

    print(
        "aMule storage test: OK"
    )
