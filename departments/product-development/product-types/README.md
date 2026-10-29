# Product types

Each folder here defines one product type. The folder is the human-readable, reviewable
source of the type's agreed field list. The database copy is loaded from it by a seed file.

## What a product type folder contains

| File | What it is |
|---|---|
| `README.md` | The data dictionary: each field in plain English, with meaning, unit, data type, allowed values, required or optional |
| `fields.json` | The same list in machine-readable form. The seed file is derived from it and must match |
| `example.json` | One fully filled sample product, with a source per value, showing what good looks like |

`pool-pump/` is the template. Copy it.

## Checklist for defining a new product type (Step 1)

1. **Agree that the type is wanted.** Record it in `docs/decisions/`.
2. **Draft the field list.** Start from how the manufacturers of that product type describe
   their own products: spec sheets, catalogue pages, comparison tables. Include a field only if
   it will be used; it is easy to add one later and hard to remove one that has values.
3. For each field decide: a `key` (lowercase, underscores), a `label`, a one-sentence
   `description`, a `data_type` (`text`, `number`, `boolean` or `enum`), a `unit` where it
   applies, `allowed_values` for an enum, and whether it is `required`.
   Keep required fields to the few that every product of the type must have.
4. **Write `README.md` and `fields.json`** in a new folder named after the type's slug.
5. **Write `example.json`** for one product, real or illustrative, with a source per value.
6. **Write the seed** at `database/seeds/product_types/<slug>.sql`, saying exactly what
   `fields.json` says, with status `draft`.
7. **Review.** The field list is read by whoever will use the data. Changes go back to step 3.
8. **Approve.** Set `"status": "approved"` in `fields.json`, make the seed match, re-run the
   seed following `database/README.md`, and update the status table in the department
   `README.md`. Extraction may now begin.

## Changing an existing field list

Same checklist from step 3, with the `version` bumped. Adding an optional field is routine.
Adding a required field puts every product missing it back under the `draft` exit rule, so
say so in the decision. Removing a field that already has values needs a migration that says
what happens to those values.
