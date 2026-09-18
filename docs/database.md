# Database Overview

The canvas is stored as a small directed graph in three PostgreSQL tables: `nodes`, `ports`, and `connections`.

## Table structure

| Table | Important columns | Purpose |
|---|---|---|
| `nodes` | `id` (PK), `name` (unique) | Stores each graph node. |
| `ports` | `id` (PK), `node_id` (FK), `name` (unique), `value` (nullable integer) | Stores the ports belonging to each node. A `NULL` value means traversal must continue upstream. |
| `connections` | `id` (PK), `source_port_id` (FK, not null, unique), `target_port_id` (FK, not null, unique) | Stores directed links from exactly one source port to exactly one target port. |

Relationship:

```text
nodes 1 ---- * ports
                 ^
                 | source_port_id
                 | target_port_id
             connections
```

Every connection must have exactly one source and exactly one target. Both port references are `NOT NULL`, so neither endpoint can be omitted, and their foreign-key constraints ensure that both referenced ports exist.

The two `UNIQUE` constraints in `connections` ensure that a port can be used at most once as a source and at most once as a target. A `CHECK` constraint also prevents a port from connecting to itself. Foreign keys use `ON DELETE CASCADE`, so dependent ports and connections do not become orphaned.

## Seeded data

### Nodes and ports

| Node | Ports (`name = value`) |
|---|---|
| 1 | `1a = 100` |
| 2 | `2a = 90`, `2b = 130` |
| 3 | `3a = 150` |
| 4 | `4a = 70` |
| 5 | `5a = 160` |
| 6 | `6a = NULL`, `6b = NULL`, `6c = NULL` |
| 7 | `7a = NULL`, `7b = NULL`, `7c = NULL` |
| 8 | `8a = 200` |
| 9 | `9a = 120` |
| 10 | `10a = 80` |
| 11 | `11a = 150`, `11b = 100`, `11d = 60`, `11c = 300` |
| 12 | `12a = 250`, `12b = 200`, `12c = 400` |

### Directed connections

| Source | Target | Source | Target |
|---|---|---|---|
| `1a` | `2a` | `2b` | `6b` |
| `3a` | `6a` | `6c` | `12a` |
| `4a` | `7a` | `5a` | `7b` |
| `7c` | `12b` | `8a` | `11a` |
| `9a` | `11b` | `10a` | `11d` |
| `11c` | `12c` |  |  |

In short, nodes group ports, ports hold optional values, and connections define the graph edges used by the segment trace-back algorithm.
