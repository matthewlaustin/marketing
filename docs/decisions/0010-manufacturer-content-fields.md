# 0010. Products keep the manufacturer's own description and features

Date: 2026-11-03
Status: agreed (owner, in chat)

## Decision

Every product has three more shared columns: `manufacturer_description` (the manufacturer's
product description, word for word), `manufacturer_features` (its feature bullets as a list of
strings, word for word) and `manufacturer_content_source_url` (where they came from). Our own
`short_description` and `long_description` stay separate.

## Why

The owner asked for them. Keeping the manufacturer's words verbatim beside our own gives a
reviewer the raw material our copy was written from, and gives other departments text they can
quote or rewrite without going back to the source.

## Consequences

- Extraction copies, never paraphrases, into these fields.
- Migration 0001 is edited in place (still unapplied); the validator, load SQL, record format,
  skill and pipeline all carry the fields.
