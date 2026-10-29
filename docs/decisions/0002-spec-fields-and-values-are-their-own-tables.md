# 0002. Specification fields and values are their own tables

Date: 2026-10-29
Status: agreed

## Decision

The agreed specification fields for a product type live in a table, `spec_fields`, one row per
field per type. Specification values live in a table, `product_specs`, one row per product per
field. Type-specific data is never stored as a free-form blob.

## Why

- The agreed field list is a first-class thing we review and approve, so it should be visible
  and queryable, not buried inside each record.
- One row per value lets each value carry its own source, capture time and verification, which
  a blob cannot do cleanly.
- The database can enforce that values match the field's data type and allowed values, that
  every value has a source, and that required fields are present, with no application code.
- Adding a product type needs no new tables and no migration.

## Consequences

- Reading a product's specs means joining rows. The `product_specs_json` view does this for
  you and presents one JSON object per product.
- Changing a field list is a new seed version, not an edit of live rows.
