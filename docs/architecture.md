# Architecture

## The model in one paragraph

The marketing department is made of sub-departments. Each one lives in its own folder under
`departments/`, with a `README.md` for people and a `CLAUDE.md` for Claude. Everything a
department produces that needs to persist is stored in one Neon Postgres database. The
repository defines the shape of that data and the rules for producing it; the database holds
the records. The repository is the rulebook and toolbox, the database is the filing cabinet.

## Layout

```
marketing/
├── README.md                    What this repository is, map of departments
├── CLAUDE.md                    Rules for Claude that apply everywhere
├── docs/
│   ├── architecture.md          This file
│   └── decisions/               Numbered one-page records of agreed decisions
├── database/
│   ├── README.md                How to apply migrations and seeds; the Neon branch workflow
│   ├── migrations/              Numbered SQL files that create or change tables
│   └── seeds/                   SQL files that load agreed reference data (for example a product type's field list)
└── departments/
    └── <department>/
        ├── README.md            What the department does and how its work flows
        ├── CLAUDE.md            Department-specific rules for Claude
        └── ...                  Whatever the department needs, agreed first
```

## The product data model

Product development produces data for many product types, and each type needs different
fields. The model keeps that cheap:

- Fields that **every** product shares (brand, part number, title, descriptions, status) are
  ordinary columns in the `products` table.
- Fields that are **specific to a type** (horsepower for a pump, square footage for a filter)
  are not columns. They are rows in `spec_fields`: one row per field per product type. This is
  the agreed field list for the type.
- The **values** are rows in `product_specs`: one row per product per field. Each row carries
  the value and where it came from.

Adding a new product type is therefore: agree its field list, add a folder under
`departments/product-development/product-types/`, write a seed that loads the list into
`spec_fields`. No new tables and no migration.

The database enforces the rules itself. A value can only be saved for a field that belongs to
the product's type. The value must match the field's data type and allowed values. Every value
must cite a source. A product cannot leave `draft` until all required fields have a value. A
product cannot be created for a type whose field list is not approved. Because the database
does this checking, there is no application code in phase 1.

A read-only view, `product_specs_json`, presents each product's specs as one JSON object so
reading is easy while storage stays structured.

## The two-step workflow

**Step 1, schema first.** For a product type, agree the list of specification fields: name,
meaning, unit, data type, allowed values, required or optional. Write it in the repository as
the type's data dictionary, load it into the database, and mark the type `approved`.

**Step 2, extraction.** For each product, pull data from manufacturer websites, spec sheets,
manuals and images, and write it **only into agreed fields**, each value with its source.
Anything useful that does not fit an agreed field goes into `proposed_spec_fields`, a holding
area that feeds back into Step 1 as a revision of the field list. It never silently becomes a
spec.

## Adding a department

1. Agree that the department should exist and what it produces. Record it in `docs/decisions/`.
2. Create `departments/<name>/README.md` (purpose, workflow, lifecycle of its output) and
   `departments/<name>/CLAUDE.md` (rules for Claude).
3. If it needs tables, add a numbered migration under `database/migrations/`.
4. Add it to the departments table in the root `README.md`.

## Adding a product type

See `departments/product-development/product-types/README.md` for the checklist.

## What is deliberately deferred

- Where media **files** are hosted. The database stores URLs only.
- The programming language for anything that consumes the data.
- Other sub-departments.
