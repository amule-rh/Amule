# aMule — Artificial Mule

**The decentralized mule for AI intelligence.**

eMule moved files. aMule moves intelligence.

aMule is an open resource network designed for AI agents and machine-to-machine data exchange.

## MVP

The repository contains:

- FastAPI API
- encrypted local storage adapter
- stable resource IDs separated from content hashes
- resource discovery model
- RSS/Atom ingestion
- Robinhood Chain registry contract
- small TypeScript/JavaScript SDK using viem
- clean web frontend
- Render/Docker deployment

### Identity model

`resourceId` identifies the logical resource/publication.

`contentHash` identifies the exact content bytes.

They are intentionally different so that:

- the same content can exist under different resources/operators
- a resource can be updated without changing its logical ID
- versioning remains possible
- provenance is preserved

## Run

```bash
pip install -r requirements.txt
uvicorn api.main:app --reload
```

Open `http://localhost:8000`.

## Robinhood Chain

The SDK defaults to Robinhood Chain testnet:

- Chain ID: 46630
- RPC: https://rpc.testnet.chain.robinhood.com

Set `AMULE_REGISTRY_ADDRESS` only when a deployed registry is available.

## Security

The upload endpoint is an MVP/dev implementation. Production should move encryption-key custody, authentication, rate limiting and durable storage into dedicated protocol services.

Never commit private keys or production secrets.
