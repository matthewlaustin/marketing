# 0005. Warranty is standardized as shared fields

Date: 2026-11-02
Status: agreed (Marketing page, question 3 note and question 14)

## Decision

Warranty is not a per-type specification field. Every product, whatever its type, carries the
same four columns on `products`:

| Column | Meaning |
|---|---|
| `warranty_years` | The headline term as a number of years |
| `warranty_type` | `full`, `limited` or `prorated` |
| `warranty_conditions` | What the manufacturer requires for the full term, in its own words |
| `warranty_component_terms` | Only when parts differ, for example motor 3 years and wet end 1 year |

## Why

The owner asked for warranty to be standardized across brands and product types. A number of
years and a fixed type make products comparable; the two text fields keep the manufacturer's
exact conditions without forcing them into a structure they do not fit.

## Consequences

- The pool pump type's free-text `warranty` field was dropped before the type was approved.
- Future product types do not define a warranty field; they inherit these columns.
- Extraction records a source for the warranty like any other value, in the product's notes
  until a dedicated place exists.
