from core.hashing import hash_bytes
from core.storage import LocalEncryptedStorage
from net.ingestor.processor import create_resource_id, process_item
from net.ingestor.rss import RSSItem


def test_hash_is_stable():
    assert hash_bytes(b"hello") == hash_bytes(b"hello")
    assert hash_bytes(b"hello") != hash_bytes(b"world")


def test_resource_id_is_not_content_hash():
    rid = create_resource_id("https://example.com/feed", "item-1")
    assert len(rid) == 64
    assert rid != hash_bytes(b"item-1")


def test_local_storage_roundtrip(tmp_path):
    storage = LocalEncryptedStorage(tmp_path)
    stored = storage.store("a" * 64, b"secret data")
    recovered = storage.retrieve(stored.resource_id, stored.key)

    assert recovered == b"secret data"
    assert stored.content_hash == hash_bytes(b"secret data")


def test_rss_candidate_has_separate_identity_and_content_hash():
    item = RSSItem(
        stable_id="guid-1",
        title="Hello",
        content="World",
        url="https://example.com/a",
        published_at=None,
        source_url="https://example.com/feed",
    )

    candidate = process_item(item)

    assert candidate["resource_id"] != candidate["content_hash"]
    assert candidate["source"]["stable_id"] == "guid-1"
