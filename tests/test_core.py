from core.encryption import generate_key
from core.storage import store_resource, retrieve_resource


def test_encrypt_store_retrieve():
    original = b"aMule test resource"

    key = generate_key()

    resource_id = store_resource(original, key)

    recovered = retrieve_resource(resource_id, key)

    assert recovered == original
