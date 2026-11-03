# 0006. Accessories and related products are links between product records

Date: 2026-11-03
Status: agreed (Marketing page, question 12 note and question 16)

## Decision

One shared table, `product_links`, records how one product relates to another. Each link has a
kind: `accessory` (sold for the product), `replacement_part`, or `compatible_with`. It also
records where the link was found. The linked item is itself a product record, with its own brand
and part number, at least in draft.

## Why

- The owner asked that accessory SKUs be linked to the product.
- A size or feature a manufacturer marks "optional" is provided by an accessory. Recording it as
  a specification would claim the product is something it is not. A link keeps the fact without
  the false claim.
- One table with a kind covers accessories, parts and compatibility without three designs.

## Consequences

- An accessory found during extraction becomes a draft product of its own, then a link. It does
  not need to be fully extracted to be linked.
- A product cannot link to itself, and the same link is recorded once.
- Deleting a product deletes its links.
