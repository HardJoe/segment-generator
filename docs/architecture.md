# Architecture

## Overview

The service has four narrow layers:

1. PostgreSQL stores the canvas and enforces directed single-wiring rules.
2. The repository loads database rows into plain domain objects.
3. The graph service discovers and calculates segments without HTTP or database dependencies.
4. FastAPI exposes the loaded canvas and calculated segments.

This keeps the graph algorithm unit-testable and prevents route or persistence concerns from leaking into traversal logic.

## Data model

`nodes` own `ports`; `connections` are directed from a source port to a target port. The database applies unique constraints to both `source_port_id` and `target_port_id`, so a port can participate at most once in either direction. A check constraint prevents self-connections.

## Segment traversal

A valued port with predecessors defines a segment. Its predecessors are determined as follows:

- A target port's predecessor is the source port of its incoming connection.
- An outgoing port with no incoming connection is fed by the other ports on its node.

Each predecessor branch is traversed backwards with depth-first search. A branch stops at the first valued port; only `NULL` ports are expanded further. The discovered values are summed and subtracted from the target value. One source is formatted directly (`2a - 1a`); multiple sources are grouped (`12b - (4a + 5a)`).

The traversal detects cycles and invalid/missing predecessor paths rather than returning a partial calculation.

## Verification

`pytest` covers the traversal rules, API contracts, seeded graph output, and the schema's single-wiring constraints. See the root [README](../README.md) for setup and test commands.
