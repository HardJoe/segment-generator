# Design decisions

## Plain SQL over an ORM

The canvas is a fixed take-home dataset with a small schema. Explicit DDL makes the critical wiring constraints easy to review and avoids adding an ORM or migration framework solely for this scope.

## Pure traversal service

The segment generator accepts domain data rather than request or database objects. This makes the stop-at-value rule, recursive trace-back behavior, and error cases direct to test without a running API or PostgreSQL instance.

## Database-enforced wiring

The rule that a port may be used once as a source and once as a target is a data-integrity concern, so it is enforced by PostgreSQL constraints instead of relying only on application checks.

## Read-only API scope

The requested API exposes the canvas and calculated segments. Mutation endpoints were intentionally omitted: they would expand validation and authorization scope without helping demonstrate the traversal requirement.
