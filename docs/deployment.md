# Deployment

Production API: <https://segment-generator-api.onrender.com/>

## Infrastructure

The application is deployed on Render from this repository using the
[Render Blueprint](../render.yaml). The Blueprint provisions a Docker web service and
a PostgreSQL database in Singapore, then supplies the database connection as
`DATABASE_URL`.

## Continuous integration

For each change, GitHub Actions runs the test suite on pull requests and before merging
to the production branch.

## Release process

Render detects the merged commit, builds the Docker image, and starts the API. On
startup, the application applies the schema and seeds the demo graph.

## Verification

The deployment is verified at <https://segment-generator-api.onrender.com/health>,
which returns `{"status":"ok"}`. The reviewer-facing endpoints are `/api/canvas`,
`/api/segments`, and `/docs`.
