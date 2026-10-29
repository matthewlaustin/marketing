# 0001. Product data lives in Neon Postgres

Date: 2026-10-29
Status: agreed

## Decision

Product records are stored in a Neon Postgres database, not as files in this repository.
The repository holds the definitions (tables, field lists, rules) and the instructions for
producing the data. The database is only ever changed by running a numbered SQL file committed
in the repository first.

## Why

- A database handles a large catalogue, cross-product queries and consumption by other systems
  far better than a folder of files.
- Keeping the definitions in the repository preserves review, history and a single place to
  read how things work.
- Neon branches give an isolated copy of the database for trying things out, so failed
  attempts never touch the real data.

## Consequences

- Nobody edits the live database by hand. See `database/README.md`.
- Database work happens in a dedicated session, on a Neon branch first, never as a side task.
- The Neon project to use is not yet recorded. When it is chosen, record its name in a new
  decision file.
