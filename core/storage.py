"""Local encrypted storage backend for the MVP."""

from dataclasses import dataclass
from pathlib import Path
import base64
import os

from .encryption import decrypt_data, encrypt_data, generate_key
from .hashing import hash_bytes


@dataclass
class StoredResource:
    resource_id: str
    content_hash: str
    ciphertext_hash: str
    storage_ref: str
    key: str
    size: int
    encrypted: bool = True


class LocalEncryptedStorage:
    def __init__(self, root: str | Path = "data/storage"):
        self.root = Path(root)
        self.root.mkdir(parents=True, exist_ok=True)

    def store(self, resource_id: str, content: bytes) -> StoredResource:
        content_hash = hash_bytes(content)
        key = generate_key()
        encrypted = encrypt_data(content, key)
        ciphertext_hash = hash_bytes(encrypted)

        filename = f"{resource_id}.bin"
        path = self.root / filename
        path.write_bytes(encrypted)

        return StoredResource(
            resource_id=resource_id,
            content_hash=content_hash,
            ciphertext_hash=ciphertext_hash,
            storage_ref=f"local://{filename}",
            key=base64.urlsafe_b64encode(key).decode("ascii"),
            size=len(content),
        )

    def retrieve(self, resource_id: str, key_b64: str) -> bytes:
        path = self.root / f"{resource_id}.bin"
        if not path.exists():
            raise FileNotFoundError(resource_id)

        key = base64.urlsafe_b64decode(key_b64.encode("ascii"))
        return decrypt_data(path.read_bytes(), key)

    def exists(self, resource_id: str) -> bool:
        return (self.root / f"{resource_id}.bin").exists()
