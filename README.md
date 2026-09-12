# aMule Net

The decentralized resource network for AI agents.

> eMule moved files. aMule moves intelligence.

## Vision

aMule Net is an open resource network designed for AI agents and
machine-to-machine applications.

It allows users, applications and autonomous agents to:

- publish resources
- discover resources created by other operators
- verify resource integrity
- retrieve resources
- build persistent knowledge
- share data between agents
- connect external data sources
- eventually exchange resources economically

## Core Architecture

```text
Internet / APIs / Files / Agents
              |
              v
        aMule Ingestor
              |
       Parse / Clean / Chunk
              |
       Metadata / Provenance
              |
       Embeddings / Indexing
              |
              v
       aMule Resource Layer
              |
       +------+------+
       |             |
       v             v
   Discovery      aMule Net
       |             |
       |        +----+----+
       |        |         |
       |     Storage   Registry
       |                  |
       +--------+---------+
                |
                v
          AI Agent Layer
                |
        REST / SDK / MCP
