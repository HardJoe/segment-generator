# Technology stack

## Runtime and API

- **Python 3.13:** application runtime and implementation language. Type annotations, dataclasses, and standard-library tools keep the domain model small and explicit.
- **FastAPI:** exposes the `GET /api/canvas` and `GET /api/segments` endpoints and provides OpenAPI documentation at `/docs`.
- **Uvicorn:** production ASGI server used to run the FastAPI application in the container.

## Data and persistence

- **PostgreSQL 16:** stores nodes, ports, and directed connections. DDL `UNIQUE` constraints enforce the single-wiring rule for source and target ports.
- **psycopg 3:** PostgreSQL driver used by the repository layer to load relational data into domain objects and run schema/seed initialization.
- **SQL:** schema and idempotent seed data are kept as explicit files in `db/`, making the required constraints and supplied graph easy to inspect.

## Testing

- **pytest:** runs unit tests for graph traversal, invalid graph handling, schema constraints, and seeded output expectations.
- **FastAPI TestClient:** exercises HTTP endpoint contracts without requiring a running PostgreSQL instance.
- **HTTPX:** TestClient transport dependency used by the API tests.

## Delivery and local development

- **Docker:** packages the API with Python 3.13 and its runtime dependencies.
- **Docker Compose:** starts the API and PostgreSQL together, waits for database health, and supplies the connection configuration.
- **Ubuntu/WSL-compatible shell commands:** the documented commands and container configuration use standard POSIX tooling and LF line endings.

## Why this stack

This stack fits a focused backend: it keeps the graph traversal logic easy to inspect and test, retains PostgreSQL as the source of truth for data integrity, and gives a reviewer a one-command local runtime. The selected tools are widely used, have small amounts of project-specific configuration, and meet the requested Python, FastAPI, PostgreSQL, Docker, and pytest constraints without adding infrastructure that the exercise does not need.

## Trade-offs and alternatives

| Choice | Why it fits here | Trade-off and reasonable alternative |
| --- | --- | --- |
| Python + FastAPI | FastAPI provides a small, typed HTTP layer and automatic API documentation while the traversal remains ordinary Python. | Java/Spring Boot, .NET, or Node.js/NestJS can offer stronger team conventions or different ecosystem preferences, but would add implementation overhead for this small service. |
| PostgreSQL + explicit SQL | The schema makes the single-wiring invariants visible and enforces them in the database. | SQLAlchemy/Alembic would help as a larger schema evolves, but are unnecessary abstraction and migration overhead for this fixed dataset. SQLite would simplify local setup but would not reflect the requested PostgreSQL environment. |
| psycopg repository | A narrow repository keeps SQL close to the model and isolates persistence from graph logic. | An ORM reduces repetitive mapping in larger CRUD applications, but can obscure the simple queries and constraints that are important to review here. |
| pytest + TestClient | Tests execute quickly without a database and directly cover traversal behavior and API responses. | Test containers or a Docker-backed integration suite would validate the live PostgreSQL path more completely, at the cost of slower, Docker-dependent tests. |
| Docker Compose | Provides a reproducible API-plus-database setup with a health-checked startup dependency. | Kubernetes or cloud deployment templates suit multi-service production environments, but would be disproportionate for a single API and database. |
