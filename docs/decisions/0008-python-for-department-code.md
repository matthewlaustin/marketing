# 0008. Python is the language for department code

Date: 2026-11-03
Status: agreed (owner asked for the extraction pipeline in chat)

## Decision

Where a department needs application code, it is written in Python 3, using only the standard
library plus the official Anthropic SDK unless a decision adds more. The first such code is the
product development extraction pipeline (decision 0009).

## Why

- The skill's helper scripts were already Python; the pipeline reuses them.
- Python runs anywhere the database session or a scheduled job runs, with no build step.
- One language keeps the repository readable by one set of people.

## Consequences

- Root `CLAUDE.md` rule 5 ("no application code yet") is replaced by: application code is
  Python, lives next to the department that owns it, and is added only by an agreed decision.
- Any consumer of the data (website, feed export) that needs another language is a new decision.
