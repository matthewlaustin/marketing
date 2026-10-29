# 0003. Schema first, then extraction

Date: 2026-10-29
Status: agreed

## Decision

The product development workflow has two steps in a fixed order. First, agree a product type's
field list and mark the type approved. Second, extract product data from websites and other
media into those agreed fields only. The database refuses to create a product for a type that
is not approved.

## Why

- Extracting before the fields are agreed produces inconsistent data that has to be redone.
- A fixed field list makes extraction a well-defined task that can be checked.
- Data found during extraction that does not fit is still valuable. It goes into a holding area,
  `proposed_spec_fields`, and feeds a deliberate revision of the field list rather than quietly
  changing it.

## Consequences

- Every product type folder holds a data dictionary and a `fields.json`, and nothing is
  extracted until the type's status is `approved`.
- Every extracted value cites its source. A value with no source is rejected by the database.
