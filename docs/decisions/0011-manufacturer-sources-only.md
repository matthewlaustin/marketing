# 0011. Only the manufacturer's own documents are sources

Date: 2026-11-03
Status: agreed (Marketing page, questions 17 and 19)

## Decision

A specification value may come only from the manufacturer's own documents for the exact part
number: its product page, spec sheet, manual or warranty terms. Reseller pages are never a
source. A variant part number (a suffix letter, a regional code, a two-speed marker) is a
different product and is disregarded, not even used as corroboration.

## Why

The owner chose "never" for reseller values and "disregard" for variants. Resellers copy each
other's mistakes, and a value that cannot be traced to the manufacturer is not worth having. A
variant may differ in exactly the fields that matter.

## Consequences

- A discontinued product the manufacturer no longer documents stays in draft with whatever the
  manufacturer still says, which may be nothing. That is the correct outcome.
- The Hayward SP2610X15 trial draft, which used reseller values, does not meet this rule and is
  not loaded.
- The skill and the pipeline's instructions say this in so many words.
