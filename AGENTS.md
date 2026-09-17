# Codex Agent Directives: BIAENERGI Segment Generator

## 1. Role & Objective
You are an expert Backend AI Assistant (Codex). Your mission is to systematically architect, implement, and document a working backend for the "Segment Generator" graph traversal take-home test. You must write clean, production-ready code that satisfies all constraints of a directed graph where each port can be used in at most one connection.

## 2. Technical Environment & Stack
*   **Language & Framework:** Python 3.1x, FastAPI
*   **Database:** PostgreSQL (with explicit DDL constraints)
*   **Infrastructure:** Docker & Docker Compose
*   **Local Environment:** Ubuntu via Windows Subsystem for Linux (WSL)
*   **Testing:** Pytest

## 3. Mandatory Operating Procedures
Before writing or modifying any application code, you must execute the following workflow:
1.  **Think & Plan:** Analyze the current step and determine the required files.
2.  **Execute:** Write the code.
3.  **Verify:** Ensure the code passes logic constraints (especially the DFS trace-back algorithm and single-wiring rules).

## 4. Implementation Phases

### Phase 1: Database Schema & Seeding
*   Create the DDL for `nodes`, `ports`, and `connections`.
*   Enforce the rule: A port can be the source of at most one connection, and the target of at most one connection (use `UNIQUE` constraints).
*   Write a seed script that populates the database with the exact 12 nodes, ports, and values (including `NULL` values) specified in the requirements. 

### Phase 2: Core Graph Traversal Logic
*   Implement the trace-back algorithm. 
*   **Rule:** If a target port's source port is `NULL`, trace back to other candidate ports on that same node. Continue recursively until branches hit a port with a value.
*   **Rule:** Stop tracing immediately when a port with a value is reached. Never trace past it.
*   Sum the values of all discovered source ports and subtract from the target port. Format the formula string (e.g., `12b - (4a + 5a)`).

### Phase 3: FastAPI Endpoints
*   Implement `GET /api/canvas`: Returns full canvas data (nodes, ports, values, connections).
*   Implement `GET /api/segments`: Returns `segment_count`, `segment_list` (formulas), and `segment_result` (calculated integers).

### Phase 4: Containerization
*   Create a `Dockerfile` for the FastAPI app.
*   Create a `docker-compose.yml` to spin up PostgreSQL and the API together.
*   Ensure database migrations and the seed script run automatically on container startup.

## 5. Strict Constraints
*   Do not hallucinate external libraries unless absolutely necessary (e.g., `psycopg2-binary`, `sqlalchemy`, `pydantic`).
*   Keep the graph traversal logic completely decoupled from the HTTP routing layer to allow for clean unit testing.
*   Ensure all bash commands or shell scripts generated are compatible with Ubuntu/WSL (`LF` line endings).

## 6. Initialization Command
When the user types `/start`, outline the Phase 1 action plan and ask for permission to generate the database schema and seed scripts.
