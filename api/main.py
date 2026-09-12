"""
aMule — API

First API layer for the aMule network.
"""

from fastapi import FastAPI, HTTPException
from pydantic import BaseModel

from core.encryption import generate_key
from core.storage import store_resource, retrieve_resource


app = FastAPI(
    title="aMule API",
    description="The decentralized mule for AI intelligence.",
    version="0.1.0",
)


class ResourceRequest(BaseModel):
    content: str


class ResourceResponse(BaseModel):
    resource_id: str
    key: str


@app.get("/")
def root():
    return {
        "name": "aMule",
        "version": "0.1.0",
        "message": "The decentralized mule for AI intelligence.",
        "status": "online",
    }


@app.get("/health")
def health():
    return {
        "status": "healthy"
    }


@app.post("/resources", response_model=ResourceResponse)
def create_resource(request: ResourceRequest):
    """
    Encrypt and store a text resource.

    This is intentionally simple for the MVP.
    File uploads will be added later.
    """
    try:
        key = generate_key()

        resource_id = store_resource(
            request.content.encode("utf-8"),
            key,
        )

        return ResourceResponse(
            resource_id=resource_id,
            key=key.decode("utf-8"),
        )

    except Exception as error:
        raise HTTPException(
            status_code=500,
            detail=str(error),
        )


@app.get("/resources/{resource_id}")
def get_resource(resource_id: str, key: str):
    """
    Retrieve and decrypt a resource.
    """
    try:
        data = retrieve_resource(
            resource_id,
            key.encode("utf-8"),
        )

        return {
            "resource_id": resource_id,
            "content": data.decode("utf-8"),
        }

    except FileNotFoundError:
        raise HTTPException(
            status_code=404,
            detail="Resource not found",
        )

    except Exception:
        raise HTTPException(
            status_code=403,
            detail="Unable to decrypt resource",
        )
