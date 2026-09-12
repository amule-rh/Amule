"""
aMule — Storage Core

Local storage layer for encrypted resources.

The MVP keeps storage local.
Later this layer can be replaced by a P2P backend.
"""

from pathlib import Path

from core.encryption import encrypt_data, decrypt_data
from core.hashing import hash_data


STORAGE_DIR = Path("data/storage")


def ensure_storage():
    """Create the storage directory if it does not exist."""
    STORAGE_DIR.mkdir(parents=True, exist_ok=True)


def store_resource(data: bytes, key: bytes) -> str:
    """
    Encrypt and store a resource.

    Returns the SHA-256 content identifier of the encrypted resource.
    """
    ensure_storage()

    encrypted_data = encrypt_data(data, key)
    resource_id = hash_data(encrypted_data)

    resource_path = STORAGE_DIR / resource_id
    resource_path.write_bytes(encrypted_data)

    return resource_id


def retrieve_resource(resource_id: str, key: bytes) -> bytes:
    """
    Retrieve and decrypt a resource using its content identifier.
    """
    resource_path = STORAGE_DIR / resource_id

    if not resource_path.exists():
        raise FileNotFoundError("Resource not found")

    encrypted_data = resource_path.read_bytes()

    # Verify that the stored content still matches its identifier.
    calculated_id = hash_data(encrypted_data)

    if calculated_id != resource_id:
        raise ValueError("Resource integrity check failed")

    return decrypt_data(encrypted_data, key)


if __name__ == "__main__":
    test_data = b"Hello from the aMule network!"

    from core.encryption import generate_key

    key = generate_key()

    resource_id = store_resource(test_data, key)

    recovered_data = retrieve_resource(resource_id, key)

    assert recovered_data == test_data

    print("aMule storage test: OK")
    print(f"Resource ID: {resource_id}")
