# Segment Generator

Production API: <https://segment-generator-api.onrender.com/>

## How to run the API

Requirements: Docker with Docker Compose support.

```bash
docker compose up --build
```

The API starts at `http://localhost:8000`.

Available endpoints:

```bash
curl http://localhost:8000/
curl http://localhost:8000/health
curl http://localhost:8000/api/canvas
curl http://localhost:8000/api/segments
```

Interactive OpenAPI documentation is available at `http://localhost:8000/docs`.

Stop the services with `docker compose down`. Add `--volumes` only when you intentionally want to remove the local PostgreSQL data volume.

## How to run the tests

The test suite does not require a running database: API tests use an in-memory repository test double, while traversal and schema checks run locally.

```bash
python3 -m venv .venv
.venv/bin/pip install -r requirements-dev.txt
.venv/bin/pytest -q
```

## Documentation

- [Database](docs/database.md): table structure, constraints, and seeded graph data.
- [Architecture](docs/architecture.md): data model and traversal design.
- [Design decisions](docs/decisions.md): rationale for the main implementation choices.
- [Technology stack](docs/technology-stack.md): runtime, framework, database, testing, and containerization tools used.
- [Deployment](docs/deployment.md): Render setup, GitHub Actions, and production-service details.

## Project layout

- `app/`: FastAPI application, database access, domain types, and traversal logic.
- `db/`: schema and seed SQL.
- `docs/`: reviewer-facing architecture and design documentation.
- `tests/`: unit and API contract tests.
- `Dockerfile` and `docker-compose.yml`: containerized API and PostgreSQL runtime.
