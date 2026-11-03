# Product development

## What this department does

Given a manufacturer or a brand, product development produces our own internal data about
their products: titles, descriptions, specifications and media. Other parts of marketing build
on that data, so it has to be consistent, sourced and complete.

## The two-step workflow

Everything here happens in this order.

### Step 1: schema first

Before any product data is collected for a kind of product, we agree what data we want. That
agreement is the product type's **field list**: every specification field, what it means, its
unit, its data type, its allowed values, and whether it is required.

The field list is written in two places that say the same thing:

- `product-types/<type>/README.md`, the data dictionary, in plain English;
- `product-types/<type>/fields.json`, the same list in a form a program can read.

It is loaded into the database by a seed file under `database/seeds/product_types/`. Once the
list is reviewed and agreed, the type's status becomes `approved`. Until then, the database
refuses to create any product of that type.

The checklist for defining a type is in `product-types/README.md`.

There is no skill for this step yet; it is done by hand following the checklist.

### Step 2: extraction

For each product, data is pulled from the manufacturer's website, spec sheets, manuals and
images, and written **only into the agreed fields**. Every value records:

- where it came from (a URL or a specific document);
- when it was captured and by whom;
- whether a person has verified it, and when.

A value with no source is refused by the database. A value that does not fit the field's data
type or allowed values is refused. Nothing is ever guessed or filled in to look complete.

The pipeline under `pipeline/` does this step for routine products: give it a brand and part
number, and it drafts the record with one model call for a fraction of a dollar. The
`extract-product` skill does the same job the slow, careful way for products the pipeline
flags. Both produce a draft record file under `work/drafts/` and the SQL that loads it, which
the database session applies on a Neon branch first.

A size or feature the manufacturer marks "optional" belongs to an accessory, not the product.
The accessory becomes a draft product of its own and is linked to the product as an
`accessory` (decision 0006).

Useful data that does not fit any agreed field is not thrown away and is not forced in. It is
recorded as a **proposed field** with an example value and a source. Proposed fields are
reviewed in batches and either added to the field list (a new version, back to Step 1) or
rejected with a reason.

## A product's lifecycle

| Status | Meaning | How it moves on |
|---|---|---|
| `draft` | Being extracted. May be incomplete. | When a title and every required field have values, it can move to `in_review` |
| `in_review` | Complete; a person is checking values against sources | Reviewer verifies values and moves it to `approved`, or back to `draft` |
| `approved` | Checked and ready for use | Published to wherever it is consumed |
| `published` | In use by other departments or systems | Changes go through the same review again |

The database enforces the `draft` exit rule itself. The rest is working agreement.

## Where things are

| Path | What it is |
|---|---|
| `CLAUDE.md` | Rules Claude follows when working in this department |
| `product-types/README.md` | Checklist for defining and approving a product type |
| `product-types/pool-pump/` | The first product type, used as the template for all others |
| `pipeline/` | The routine way to do Step 2: code fetches the documents, one model call drafts the record, the validator checks it (decision 0009) |
| `.claude/skills/extract-product/` | The skill for hard cases: Claude works the product out step by step, same record format and checks (decision 0007) |
| `../../work/` | Fetched sources and draft records, ignored by git; the database is the only permanent home for product data |
| `../../database/` | The tables and seeds this department's data lives in |

## Product types

| Type | Status | Version |
|---|---|---|
| Pool pump | approved (port size list pending catalog review) | 1 |
