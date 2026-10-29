# Database

The product data lives in a Neon Postgres database. This folder holds the only two kinds of
file that are ever allowed to change it.

| Folder | What it holds | How often it runs |
|---|---|---|
| `migrations/` | Numbered SQL files that create or change tables and rules | Each file runs exactly once per database, in number order |
| `seeds/` | SQL files that load agreed reference data, such as a product type's field list | Safe to re-run; existing rows are updated in place |

## The one rule

**The database is only ever changed by running a file from this folder that has been
committed and reviewed first.** Nobody edits the live database by hand, and Claude does not
either. If something needs to change, write the next numbered file, get it reviewed, then
apply it.

## Which Neon project

Not yet recorded. When the project is chosen or created, add a decision file under
`docs/decisions/` naming it, and note it here.

## How to apply files safely: the branch workflow

Neon can make a **branch** of a database: an instant, isolated copy that you can change
freely and throw away. Use one every time.

1. Create a branch from `main`. Call it `dev` or name it after the change.
2. Run the migration files that have not yet been applied, in number order, against the
   branch. Then run any seed files that are new or changed.
3. Check the result. For a migration, confirm the tables and rules behave as the file says.
   For a seed, confirm the rows match the source file.
4. If anything failed, fix the file in the repository, delete the branch, and start again at
   step 1. Nothing has touched `main`.
5. Once the branch is clean, run the same files, in the same order, against `main`.
6. Delete the branch.

Keep track of which migrations `main` has received by their number. There is no migration
tool yet; this is deliberate while there are few files. When a tool is adopted that is a
recorded decision.

## Do this in a dedicated session

Database work has its own trial and error. Do it in a conversation whose purpose is database
work, starting from this file, so the attempts do not clutter a conversation about something
else.

## What the migration creates

`0001_product_core.sql` creates these tables. The full explanation is in
`docs/architecture.md`.

| Table | One row per |
|---|---|
| `manufacturers` | Company that makes products |
| `brands` | Brand, owned by a manufacturer |
| `product_types` | Kind of product, with `draft` or `approved` status |
| `spec_fields` | Agreed specification field for one product type |
| `products` | Product |
| `product_media` | Image, manual, spec sheet or video for a product (URL only) |
| `product_specs` | Value of one field for one product, with its source |
| `proposed_spec_fields` | Data found during extraction that has no agreed field yet |

And one view, `product_specs_json`, which shows each product with its specs as one JSON object.

## Rules the database enforces on its own

- A product can only be created for a product type whose status is `approved`.
- A product's type cannot be changed after creation.
- A spec value must belong to a field of the product's type, must be of the field's data type,
  and for an enum field must be one of the allowed values.
- Every spec value must cite a source: a URL or a media record.
- A product cannot leave `draft` until it has a title and every required field has a value.

## Changing a product type's field list

Edit the type's `fields.json` and `README.md` under `departments/product-development/
product-types/<type>/`, bump the version, update the matching seed file so it says the same
thing, and re-run the seed. Removing a field that already has values will be refused by the
database; that case needs a migration that says what happens to the values.
