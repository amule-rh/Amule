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

from core.encryption import generate_key
from core.storage import store_resource


# =========================================================
# PATHS
# =========================================================

BASE_DIR = Path(__file__).resolve().parent.parent

FRONTEND_DIR = BASE_DIR / "frontend"


# =========================================================
# APPLICATION
# =========================================================

app = FastAPI(
    title="aMule API",
    description="The decentralized mule for AI intelligence.",
    version="0.3.0",
)


# =========================================================
# CORS
# =========================================================

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=False,
    allow_methods=["*"],
    allow_headers=["*"],
)


# =========================================================
# STATIC FILES
# =========================================================

app.mount(
    "/static",
    StaticFiles(directory=FRONTEND_DIR),
    name="static",
)


# =========================================================
# WEB APPLICATION
# =========================================================

@app.get("/", include_in_schema=False)
async def frontend():

    return FileResponse(
        FRONTEND_DIR / "index.html"
    )


@app.get("/style.css", include_in_schema=False)
async def stylesheet():

    return FileResponse(
        FRONTEND_DIR / "style.css"
    )


@app.get("/app.js", include_in_schema=False)
async def javascript():

    return FileResponse(
        FRONTEND_DIR / "app.js"
    )


# =========================================================
# API ROOT
# =========================================================

@app.get("/api")
def api_root():

    return {
        "name": "aMule",
        "version": "0.3.0",
        "description": (
            "The decentralized mule "
            "for AI intelligence."
        ),
        "status": "online",
    }


# =========================================================
# HEALTH
# =========================================================

@app.get("/health")
def health():

    return {
        "status": "healthy",
        "service": "amule",
    }


# =========================================================
# RESOURCE UPLOAD
# =========================================================

@app.post("/resources/upload")
async def upload_resource(
    file: UploadFile = File(...)
):
    """
    Upload a resource to aMule.

    Current MVP flow:

    File
      ↓
    Read
      ↓
    Encrypt
      ↓
    SHA-256
      ↓
    Local encrypted storage
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


        # Generate encryption key
        key = generate_key()


        # Encrypt + hash + store
        resource_id = store_resource(
            data,
            key,
        )


        return {

            "success": True,

            "resource_id":
                resource_id,

            "filename":
                file.filename,

            "content_type":
                (
                    file.content_type
                    or "application/octet-stream"
                ),

            "size":
                len(data),

            # Temporary MVP only.
            #
            # Production aMule will use
            # proper key management and
            # access authorization.
            "key":
                key.decode("utf-8"),

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
