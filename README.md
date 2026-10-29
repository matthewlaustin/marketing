# Marketing

This repository holds the marketing department's AI infrastructure. It is organised by
sub-department. Each sub-department gets its own folder under `departments/` with its own
instructions for people and for Claude.

## How to think about this repository

The repository is the **rulebook and toolbox**. The database (Neon Postgres) is the
**filing cabinet**.

- The repository holds how each department works, the agreed definition of every kind of
  data we produce, the SQL that creates the database tables, and the Claude skills that do
  the work.
- The database holds the actual records.
- The two stay in sync by one rule: **the database is only ever changed by running a
  numbered SQL file that has been committed here first.** See `database/README.md`.

## Map

| Path | What it is |
|---|---|
| `docs/architecture.md` | How the whole thing fits together and how to add a department or a product type |
| `docs/decisions/` | One-page records of the decisions we have agreed on, numbered in order |
| `database/` | Migrations (table definitions) and seeds (reference data), plus how to apply them |
| `departments/product-development/` | The first sub-department: turning a manufacturer or brand into our own product data |

## Departments

| Department | Status | What it does |
|---|---|---|
| Product development | Building | Given a manufacturer or brand, produces our internal product data: titles, specifications, media |

Other sub-departments will be added here as they are agreed. The pattern for adding one is in
`docs/architecture.md`.
