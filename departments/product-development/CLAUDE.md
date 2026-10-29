# Instructions for Claude in product development

Read this department's `README.md` first. The repository-wide rules in the root `CLAUDE.md`
also apply.

## Rules

1. **Schema first.** Do not extract or record data for a product type whose status is not
   `approved`. If asked to, say so and offer to help define the field list instead.
2. **Never invent a specification.** If a value cannot be found in a source, leave the field
   empty. An empty required field keeps the product in `draft`, which is the correct outcome.
3. **Every value cites its source.** Record the exact URL or document for each value, not just
   for the product. Prefer the manufacturer's own site or documents over resellers.
4. **Record values in the manufacturer's units and words**, converted only where the field's
   unit requires it, and say so in the value's notes.
5. **Do not force data into the wrong field.** Something that does not fit an agreed field goes
   into `proposed_spec_fields` with an example value, a source and a one-line rationale.
6. **Do not change a field list in place.** A change is a new version: update the type's
   `README.md` and `fields.json`, update the seed to match, and present it for review.
7. **Do not mark anything verified.** Verification is a person's action.
8. **Do not create product types, skills or tooling** without an agreed decision recorded in
   `docs/decisions/`.

## Data types in plain terms

| Data type | Means | Stored in |
|---|---|---|
| `text` | Free text, kept short | `value_text` |
| `number` | A number, no unit in the value itself; the unit is on the field | `value_number` |
| `boolean` | Yes or no | `value_boolean` |
| `enum` | One choice from the field's fixed list of allowed values | `value_text` |
