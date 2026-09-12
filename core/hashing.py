"""
aMule — Content Hashing

Creates deterministic SHA-256 fingerprints for resources.
The hash can be used to identify and verify content.
"""

import hashlib
from pathlib import Path


def hash_data(data: bytes) -> str:
    """
    Generate a SHA-256 hash from raw data.
    """
    return hashlib.sha256(data).hexdigest()


def hash_file(file_path: str) -> str:
    """
    Generate a SHA-256 hash from a file.
    """
    sha256 = hashlib.sha256()

    with Path(file_path).open("rb") as file:
        for chunk in iter(lambda: file.read(1024 * 1024), b""):
            sha256.update(chunk)

    return sha256.hexdigest()


if __name__ == "__main__":
    test_data = b"Hello from aMule!"

    content_hash = hash_data(test_data)

    print("aMule content hash:")
    print(content_hash)
