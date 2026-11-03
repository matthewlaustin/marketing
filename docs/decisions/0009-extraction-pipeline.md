# 0009. Extraction runs as a pipeline, with the skill for hard cases

Date: 2026-11-03
Status: agreed (owner: "This is way too expensive. We need this under a $.")

## Decision

Routine extraction runs through `departments/product-development/pipeline/`: code finds and
fetches the manufacturer's documents, one model call drafts the record under a strict output
format built from the type's field list, and the validator checks it. Default model: Claude
Sonnet 5.5 at medium effort. The `extract-product` skill stays for the cases the pipeline flags:
a required field it could not fill, a source conflict, or a product the manufacturer no longer
lists.

The pipeline calls the API with a key kept as an environment secret, billed per token.

## Why

Measured on the same product (Hayward VSP32940): the skill as an agent loop on Fable 5.1 cost
$4.37 at API list prices, mostly re-reading its own growing context across 27 calls; the same
skill on Sonnet 5.5 with the URL given cost $0.47. A single-call pipeline removes the loop
entirely and is estimated at $0.10 to $0.20. The target is under $1 per product with the
expensive model reserved for the few hard ones.

## Consequences

- The record format, validator and load SQL are shared between skill and pipeline, so a draft
  from either is loaded the same way.
- The output format is generated from `fields.json`, so a change to a field list changes what
  the model may answer with no code change.
- Per-brand discovery settings live in `pipeline/brands.json`.
- The first live run must be measured and compared with the skill's draft before the pipeline
  becomes the default for a product type.
