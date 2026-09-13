from pathlib import Path
import hashlib
import os
import re
import sys

from fastapi import FastAPI, File, HTTPException, UploadFile
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel, Field

# -------------------------------------------------------------------
# Project paths
# -------------------------------------------------------------------

ROOT = Path(__file__).resolve().parents[1]

if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from core.storage import LocalEncryptedStorage
from net.ingestor.sources import Source, SourceCatalog


# -------------------------------------------------------------------
# Application
# -------------------------------------------------------------------

app = FastAPI(
    title="aMule Net API",
    version="0.6.2",
    description="Decentralized resource layer for AI intelligence.",
)


# -------------------------------------------------------------------
# Configuration
# -------------------------------------------------------------------

storage = LocalEncryptedStorage(
    os.getenv(
        "AMULE_STORAGE_DIR",
        str(ROOT / "data" / "storage"),
    )
)

catalog = SourceCatalog(
    os.getenv(
        "AMULE_SOURCE_CATALOG",
        str(ROOT / "data" / "ingestor" / "sources.json"),
    )
)

MAX_UPLOAD = int(
    os.getenv(
        "AMULE_MAX_UPLOAD_BYTES",
        str(20 * 1024 * 1024),
    )
)


# -------------------------------------------------------------------
# Static assets
# -------------------------------------------------------------------

ASSETS_DIR = ROOT / "frontend" / "assets"

if ASSETS_DIR.exists():
    app.mount(
        "/assets",
        StaticFiles(directory=str(ASSETS_DIR)),
        name="assets",
    )


# -------------------------------------------------------------------
# Request models
# -------------------------------------------------------------------

class SourceCreateRequest(BaseModel):
    source_id: str = Field(
        min_length=1,
        max_length=80,
    )

    name: str = Field(
        min_length=1,
        max_length=200,
    )

    url: str

    source_type: str = "rss"

    category: str = "general"

    description: str = ""


# -------------------------------------------------------------------
# Frontend
# -------------------------------------------------------------------

@app.get("/")
def index():
    return FileResponse(
        ROOT / "frontend" / "index.html"
    )


@app.get("/style.css")
def style():
    return FileResponse(
        ROOT / "frontend" / "style.css",
        media_type="text/css",
    )


@app.get("/app.js")
def app_js():
    return FileResponse(
        ROOT / "frontend" / "app.js",
        media_type="application/javascript",
    )


# -------------------------------------------------------------------
# API information
# -------------------------------------------------------------------

@app.get("/api")
def api_info():
    return {
        "name": "aMule Net API",
        "protocol": "aMule",
        "version": "0.6.2",
        "chain": {
            "name": "Robinhood Chain Testnet",
            "chain_id": 46630,
        },
        "storage": "local-encrypted-mvp",
    }


# -------------------------------------------------------------------
# Health check
# -------------------------------------------------------------------

@app.get("/health")
def health():
    return {
        "status": "ok",
        "protocol": "amule",
        "version": "0.6.2",
    }


# -------------------------------------------------------------------
# Resource ID
# -------------------------------------------------------------------

def generate_resource_id() -> str:
    """
    Generate a 32-byte / 64-hex-character resource ID.

    This ID represents the logical resource identity.
    It is intentionally different from contentHash.
    """

    random_bytes = os.urandom(32)

    return hashlib.sha256(
        random_bytes
    ).hexdigest()


# -------------------------------------------------------------------
# Resource upload
# -------------------------------------------------------------------

@app.post("/resources/upload")
async def upload_resource(
    file: UploadFile = File(...)
):
    if not file.filename:
        raise HTTPException(
            status_code=400,
            detail="Filename is required.",
        )

    # ---------------------------------------------------------------
    # Sanitize filename
    # ---------------------------------------------------------------

    safe_name = re.sub(
        r"[^A-Za-z0-9._-]",
        "_",
        file.filename,
    )

    # ---------------------------------------------------------------
    # Read file
    # ---------------------------------------------------------------

    content = await file.read()

    # ---------------------------------------------------------------
    # Validate size
    # ---------------------------------------------------------------

    if len(content) > MAX_UPLOAD:
        raise HTTPException(
            status_code=413,
            detail="File exceeds the MVP upload limit.",
        )

    # ---------------------------------------------------------------
    # Generate 32-byte resource ID
    # ---------------------------------------------------------------

    resource_id = generate_resource_id()

    # ---------------------------------------------------------------
    # Store encrypted resource
    # ---------------------------------------------------------------

    stored = storage.store(
        resource_id,
        content,
    )

    # ---------------------------------------------------------------
    # Return protocol resource
    # ---------------------------------------------------------------

    return {
        "protocol": "amule",

        "resourceId": stored.resource_id,

        "contentHash": stored.content_hash,

        "ciphertextHash": stored.ciphertext_hash,

        "storageRef": stored.storage_ref,

        "filename": safe_name,

        "contentType": (
            file.content_type
            or "application/octet-stream"
        ),

        "size": stored.size,

        "encrypted": True,

        # Temporary MVP key.
        # Production will move key custody
        # into the protocol layer.
        "key": stored.key,

        "status": "stored",
    }


# -------------------------------------------------------------------
# Sources
# -------------------------------------------------------------------

@app.get("/sources")
def list_sources():
    return {
        "sources": [
            source.__dict__
            for source in catalog.list()
        ]
    }


# -------------------------------------------------------------------
# Get source
# -------------------------------------------------------------------

@app.get("/sources/{source_id}")
def get_source(
    source_id: str,
):
    source = catalog.get(source_id)

    if not source:
        raise HTTPException(
            status_code=404,
            detail="Source not found.",
        )

    return source.__dict__


# -------------------------------------------------------------------
# Add source
# -------------------------------------------------------------------

@app.post("/sources")
def add_source(
    request: SourceCreateRequest,
):
    # ---------------------------------------------------------------
    # Basic URL validation
    # ---------------------------------------------------------------

    if not request.url.startswith(
        (
            "http://",
            "https://",
        )
    ):
        raise HTTPException(
            status_code=400,
            detail="Source URL must use HTTP or HTTPS.",
        )

    # ---------------------------------------------------------------
    # Add source
    # ---------------------------------------------------------------

    try:
        source = catalog.add(
            Source(
                **request.model_dump()
            )
        )

    except ValueError as exc:
        raise HTTPException(
            status_code=409,
            detail=str(exc),
        )

    return source.__dict__


# -------------------------------------------------------------------
# Delete source
# -------------------------------------------------------------------

@app.delete("/sources/{source_id}")
def delete_source(
    source_id: str,
):
    deleted = catalog.remove(
        source_id
    )

    if not deleted:
        raise HTTPException(
            status_code=404,
            detail="Source not found.",
        )

    return {
        "deleted": source_id
    }


# -------------------------------------------------------------------
# Enable source
# -------------------------------------------------------------------

@app.post("/sources/{source_id}/enable")
def enable_source(
    source_id: str,
):
    try:
        source = catalog.set_enabled(
            source_id,
            True,
        )

        return source.__dict__

    except KeyError:
        raise HTTPException(
            status_code=404,
            detail="Source not found.",
        )


# -------------------------------------------------------------------
# Disable source
# -------------------------------------------------------------------

@app.post("/sources/{source_id}/disable")
def disable_source(
    source_id: str,
):
    try:
        source = catalog.set_enabled(
            source_id,
            False,
        )

        return source.__dict__

    except KeyError:
        raise HTTPException(
            status_code=404,
            detail="Source not found.",
        )
