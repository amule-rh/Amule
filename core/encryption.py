"""
aMule — Encryption Core

Handles encryption and decryption of resources before
they are distributed through the aMule network.
"""

from cryptography.fernet import Fernet


def generate_key() -> bytes:
    """Generate a new encryption key."""
    return Fernet.generate_key()


def encrypt_data(data: bytes, key: bytes) -> bytes:
    """Encrypt raw data using the supplied key."""
    cipher = Fernet(key)
    return cipher.encrypt(data)


def decrypt_data(encrypted_data: bytes, key: bytes) -> bytes:
    """Decrypt encrypted data using the supplied key."""
    cipher = Fernet(key)
    return cipher.decrypt(encrypted_data)


if __name__ == "__main__":
    # Simple self-test
    key = generate_key()

    original = b"Hello from aMule!"
    encrypted = encrypt_data(original, key)
    decrypted = decrypt_data(encrypted, key)

    assert decrypted == original

    print("aMule encryption test: OK")
