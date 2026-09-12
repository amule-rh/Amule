"""
aMule — API

API layer for the aMule network.

Current MVP:
- Health check
- Resource upload
- Encryption
- Content hashing
- Local encrypted storage
"""

from pathlib import Path

from fastapi import FastAPI, File, HTTPException, UploadFile
from fastapi.middleware.cors import CORSMiddleware

from core.encryption import generate_key
from core.storage import store_resource


app = FastAPI(
    title="aMule API",
    description="The decentralized mule for AI intelligence.",
    version="0.2.0",
)


# =========================
# CORS
# =========================

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=False,
    allow_methods=["*"],
    allow_headers=["*"],
)


# =========================
# ROOT
# =========================

@app.get("/")
def root():
    return {
        "name": "aMule",
        "version": "0.2.0",
        "description": "The decentralized mule for AI intelligence.",
        "status": "online",
    }


# =========================
# HEALTH
# =========================

@app.get("/health")
def health():
    return {
        "status": "healthy",
    }


# =========================
# RESOURCE UPLOAD
# =========================

@app.post("/resources/upload")
async def upload_resource(
    file: UploadFile = File(...)
):
    """
    Upload a resource to aMule.

    Current flow:

    File
      ↓
    Read
      ↓
    Encrypt
      ↓
    SHA-256
      ↓
    Local storage
      ↓
    Resource ID
    """

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
                detail="The uploaded file is empty.",
            )


        # Generate a unique encryption key
        key = generate_key()


        # Encrypt + hash + store
        resource_id = store_resource(
            data,
            key,
        )


        return {
            "success": True,
            "resource_id": resource_id,
            "filename": file.filename,
            "content_type": (
                file.content_type
                or "application/octet-stream"
            ),
            "size": len(data),

            # Temporary MVP behaviour.
            # This will later be replaced by
            # proper key management.
            "key": key.decode("utf-8"),
        }


    except HTTPException:
        raise


    except Exception as error:

        print(
            f"aMule upload error: {error}"
        )

        raise HTTPException(
            status_code=500,
            detail="Unable to store resource.",
        )
