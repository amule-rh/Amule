"""Content hashing utilities."""

from hashlib import sha256
from pathlib import Path


def hash_bytes(data: bytes) -> str:
    return sha256(data).hexdigest()


def hash_data(data: str, encoding: str = "utf-8") -> str:
    return hash_bytes(data.encode(encoding))


def hash_file(file_path: str | Path) -> str:
    digest = sha256()
    with Path(file_path).open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()
