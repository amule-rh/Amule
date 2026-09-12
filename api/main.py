"""
aMule — API + Web Application

Artificial Mule
The decentralized mule for AI intelligence.
"""

from pathlib import Path

from fastapi import FastAPI, File, HTTPException, UploadFile
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel, Field

from core.encryption import generate_key
from core.net_registry import (
    build_resource_record,
    serialize_resource_record,
    validate_resource_record,
)
from core.storage import store_resource

from net.ingestor.api import (
    add_source,
    disable_source,
    enable_source,
    get_source,
    list_sources,
    remove_source,
)

from net.ingestor.sources import (
    SourceCatalog,
)


BASE_DIR = Path(__file__).resolve().parent.parent
FRONTEND_DIR = BASE_DIR / "frontend"


app = FastAPI(
    title="aMule API",
    description=(
        "The decentralized mule for AI intelligence."
    ),
    version="0.5.0",
)


app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=False,
    allow_methods=["*"],
    allow_headers=["*"],
)


app.mount(
    "/static",
    StaticFiles(
        directory=FRONTEND_DIR
    ),
    name="static",
)


source_catalog = SourceCatalog()


class SourceCreateRequest(BaseModel):
    """
    Request used to register a new ingestion source.
    """

    source_id: str = Field(
        min_length=1,
        max_length=100,
    )

    name: str = Field(
        min_length=1,
        max_length=200,
    )

    url: str = Field(
        min_length=1,
        max_length=2000,
    )

    source_type: str = Field(
        default="rss",
        min_length=1,
        max_length=50,
    )

    category: str | None = Field(
        default=None,
        max_length=100,
    )

    description: str | None = Field(
        default=None,
        max_length=500,
    )


@app.get(
    "/",
    include_in_schema=False,
)
async def frontend():

    return FileResponse(
        FRONTEND_DIR / "index.html"
    )


@app.get(
    "/style.css",
    include_in_schema=False,
)
async def stylesheet():

    return FileResponse(
        FRONTEND_DIR / "style.css"
    )


@app.get(
    "/app.js",
    include_in_schema=False,
)
async def javascript():

    return FileResponse(
        FRONTEND_DIR / "app.js"
    )


@app.get("/api")
def api_root():

    return {
        "name": "aMule",
        "version": "0.5.0",
        "description": (
            "The decentralized mule for AI intelligence."
        ),
        "status": "online",
    }


@app.get("/health")
def health():

    return {
        "status": "healthy",
        "service": "amule",
    }


@app.post("/resources/upload")
async def upload_resource(
    file: UploadFile = File(...)
):

    if not file.filename:

        raise HTTPException(
            status_code=400,
            detail="Filename is required.",
        )

    try:

        data = await file.read()

        if not data:

            raise HTTPException(
                status_code=400,
                detail=(
                    "The uploaded file is empty."
                ),
            )

        key = generate_key()

        resource_id = store_resource(
            data,
            key,
        )

        content_type = (
            file.content_type
            or "application/octet-stream"
        )

        resource_record = (
            build_resource_record(
                name=file.filename,
                content_hash=resource_id,
                size=len(data),
                content_type=content_type,
                encrypted=True,
                provider=None,
            )
        )

        if not validate_resource_record(
            resource_record
        ):

            raise HTTPException(
                status_code=500,
                detail=(
                    "Invalid resource "
                    "registry record."
                ),
            )

        registry_payload = (
            serialize_resource_record(
                resource_record
            )
        )

        return {
            "success": True,
            "resource_id": resource_id,
            "filename": file.filename,
            "content_type": content_type,
            "size": len(data),
            "encrypted": True,
            "registry": resource_record,
            "registry_payload": registry_payload,
            "key": key.decode(
                "utf-8"
            ),
        }

    except HTTPException:

        raise

    except Exception as error:

        print(
            f"aMule upload error: {error}"
        )

        raise HTTPException(
            status_code=500,
            detail=(
                "Unable to store resource."
            ),
        )


@app.get("/sources")
def get_sources(
    enabled_only: bool = False,
):

    return {
        "success": True,
        "sources": list_sources(
            source_catalog,
            enabled_only=enabled_only,
        ),
    }


@app.get("/sources/{source_id}")
def get_source_by_id(
    source_id: str,
):

    source = get_source(
        source_catalog,
        source_id,
    )

    if not source:

        raise HTTPException(
            status_code=404,
            detail="Source not found.",
        )

    return {
        "success": True,
        "source": source,
    }


@app.post("/sources")
def create_source(
    request: SourceCreateRequest,
):

    existing = get_source(
        source_catalog,
        request.source_id,
    )

    if existing:

        raise HTTPException(
            status_code=409,
            detail="Source already exists.",
        )

    try:

        source = add_source(
            catalog=source_catalog,
            source_id=request.source_id,
            name=request.name,
            url=request.url,
            source_type=request.source_type,
            category=request.category,
            description=request.description,
        )

        return {
            "success": True,
            "source": source,
        }

    except ValueError as error:

        raise HTTPException(
            status_code=400,
            detail=str(error),
        )


@app.delete("/sources/{source_id}")
def delete_source(
    source_id: str,
):

    removed = remove_source(
        source_catalog,
        source_id,
    )

    if not removed:

        raise HTTPException(
            status_code=404,
            detail="Source not found.",
        )

    return {
        "success": True,
        "source_id": source_id,
        "removed": True,
    }


@app.post("/sources/{source_id}/enable")
def activate_source(
    source_id: str,
):

    enabled = enable_source(
        source_catalog,
        source_id,
    )

    if not enabled:

        raise HTTPException(
            status_code=404,
            detail="Source not found.",
        )

    return {
        "success": True,
        "source_id": source_id,
        "enabled": True,
    }


@app.post("/sources/{source_id}/disable")
def deactivate_source(
    source_id: str,
):

    disabled = disable_source(
        source_catalog,
        source_id,
    )

    if not disabled:

        raise HTTPException(
            status_code=404,
            detail="Source not found.",
        )

    return {
        "success": True,
        "source_id": source_id,
        "enabled": False,
    }
