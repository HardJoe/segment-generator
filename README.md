# Segment Generator

## How to run the API

Requirements: Docker with Docker Compose support.

```bash
docker compose up --build
```

The API starts at `http://localhost:8000`.

The Render production URL is assigned during the first Dashboard deploy. Record it here
once available: `https://<segment-generator-api>.onrender.com`.

Available endpoints:

```bash
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

- [Architecture](docs/architecture.md): data model and traversal design.
- [Design decisions](docs/decisions.md): rationale for the main implementation choices.
- [Technology stack](docs/technology-stack.md): runtime, framework, database, testing, and containerization tools used.

## Project layout

- `app/`: FastAPI application, database access, domain types, and traversal logic.
- `db/`: schema and seed SQL.
- `docs/`: reviewer-facing architecture and design documentation.
- `tests/`: unit and API contract tests.
- `Dockerfile` and `docker-compose.yml`: containerized API and PostgreSQL runtime.

## Render deployment

This repository includes a [Render Blueprint](render.yaml). It creates a Docker-based
web service and a managed PostgreSQL database in Singapore, then injects the database's
private connection string as `DATABASE_URL`. The app applies its schema and seeds its
demo data when it starts.

1. Push this repository, including `render.yaml`, to GitHub or GitLab.
2. In the [Render Dashboard](https://dashboard.render.com/), select **New** →
   **Blueprint**, connect the repository, and approve the proposed resources.
3. After the deploy finishes, open `https://<your-service>.onrender.com/health`.
   It should return `{"status":"ok"}`. The API is then available at
   `/api/canvas`, `/api/segments`, and `/docs`.

The Blueprint uses Render's `free` plans. Choose paid plans in `render.yaml` before
deployment if you need an always-on service or durable production database guarantees.
