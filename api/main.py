from pathlib import Path
import os
import re
import sys
import uuid

from fastapi import FastAPI, File, HTTPException, UploadFile
from fastapi.responses import FileResponse
from pydantic import BaseModel, Field

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from core.storage import LocalEncryptedStorage
from net.ingestor.sources import Source, SourceCatalog

app = FastAPI(
    title="aMule Net API",
    version="0.6.0",
    description="Decentralized resource layer for AI intelligence.",
)

storage = LocalEncryptedStorage(
    os.getenv("AMULE_STORAGE_DIR", str(ROOT / "data" / "storage"))
)
catalog = SourceCatalog(
    os.getenv("AMULE_SOURCE_CATALOG", str(ROOT / "data" / "ingestor" / "sources.json"))
)

MAX_UPLOAD = int(os.getenv("AMULE_MAX_UPLOAD_BYTES", str(20 * 1024 * 1024)))


class SourceCreateRequest(BaseModel):
    source_id: str = Field(min_length=1, max_length=80)
    name: str = Field(min_length=1, max_length=200)
    url: str
    source_type: str = "rss"
    category: str = "general"
    description: str = ""


@app.get("/")
def index():
    return FileResponse(ROOT / "frontend" / "index.html")


@app.get("/style.css")
def style():
    return FileResponse(ROOT / "frontend" / "style.css", media_type="text/css")


@app.get("/app.js")
def app_js():
    return FileResponse(ROOT / "frontend" / "app.js", media_type="application/javascript")


@app.get("/api")
def api_info():
    return {
        "name": "aMule Net API",
        "protocol": "aMule",
        "version": "0.6.0",
        "chain": {"name": "Robinhood Chain Testnet", "chain_id": 46630},
        "storage": "local-encrypted-mvp",
    }


@app.get("/health")
def health():
    return {"status": "ok"}


@app.post("/resources/upload")
async def upload_resource(file: UploadFile = File(...)):
    if not file.filename:
        raise HTTPException(400, "Filename is required.")

    safe_name = re.sub(r"[^A-Za-z0-9._-]", "_", file.filename)
    content = await file.read()

    if len(content) > MAX_UPLOAD:
        raise HTTPException(413, "File exceeds the MVP upload limit.")

    resource_id = uuid.uuid4().hex
    stored = storage.store(resource_id, content)

    return {
        "protocol": "amule",
        "resourceId": stored.resource_id,
        "contentHash": stored.content_hash,
        "ciphertextHash": stored.ciphertext_hash,
        "storageRef": stored.storage_ref,
        "filename": safe_name,
        "contentType": file.content_type or "application/octet-stream",
        "size": stored.size,
        "encrypted": True,
        "key": stored.key,
        "status": "stored",
    }


@app.get("/sources")
def list_sources():
    return {"sources": [s.__dict__ for s in catalog.list()]}


@app.get("/sources/{source_id}")
def get_source(source_id: str):
    source = catalog.get(source_id)
    if not source:
        raise HTTPException(404, "Source not found.")
    return source.__dict__


@app.post("/sources")
def add_source(request: SourceCreateRequest):
    if not request.url.startswith(("http://", "https://")):
        raise HTTPException(400, "Source URL must use HTTP or HTTPS.")

    try:
        source = catalog.add(Source(**request.model_dump()))
    except ValueError as exc:
        raise HTTPException(409, str(exc))

    return source.__dict__


@app.delete("/sources/{source_id}")
def delete_source(source_id: str):
    if not catalog.remove(source_id):
        raise HTTPException(404, "Source not found.")
    return {"deleted": source_id}


@app.post("/sources/{source_id}/enable")
def enable_source(source_id: str):
    try:
        return catalog.set_enabled(source_id, True).__dict__
    except KeyError:
        raise HTTPException(404, "Source not found.")


@app.post("/sources/{source_id}/disable")
def disable_source(source_id: str):
    try:
        return catalog.set_enabled(source_id, False).__dict__
    except KeyError:
        raise HTTPException(404, "Source not found.")
