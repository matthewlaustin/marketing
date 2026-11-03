# 0007. The first skill: extract-product

Date: 2026-11-03
Status: agreed (owner asked for it in chat)

## Decision

The product development department gets its first Claude skill, `extract-product`, at
`departments/product-development/.claude/skills/extract-product/`. Given an approved product
type, a brand and a manufacturer part number, it fetches the manufacturer's sources, fills only
the agreed fields with a source and quote per value, validates the draft against the type's
field list, and produces the SQL that loads it as a draft product.

## Why

This is Step 2 of the workflow (decision 0003) made repeatable. Putting the rules into a skill
with a validator means every extraction follows the same rules and is checked the same way,
instead of relying on each conversation to remember them.

## Consequences

- Drafts and fetched sources go under `work/`, which git ignores. Product data still lives only
  in the database (decision 0001).
- The load SQL is applied by the database session on a Neon branch first, like any other file.
- A second skill, to define a product type, is not built until agreed.
