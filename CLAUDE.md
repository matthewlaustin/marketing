# Instructions for Claude in this repository

Read `README.md` first, then the `README.md` and `CLAUDE.md` of whichever department you are
working in under `departments/`.

## Rules that apply everywhere

1. **The repository is the record.** Never change the database by hand. Any change to tables
   or reference data is a new numbered file under `database/migrations/` or `database/seeds/`,
   committed and reviewed before it is applied. See `database/README.md`.
2. **Do not build what has not been agreed.** Do not create new departments, product types,
   tables, skills or tooling on your own initiative. Propose them, and record the agreement in
   `docs/decisions/` before building.
3. **Write for people who are not engineers.** Every README explains its subject in plain
   language before any technical detail. Explain a term the first time you use it.
4. **Neon work is deliberate.** Apply database files to a Neon branch first, never straight to
   `main`. Do not experiment against Neon from a conversation whose purpose is something else.
5. **Application code is Python** (decision 0008), lives next to the department that owns it, and
   is added only by an agreed decision. Nothing in the repository holds product data; code reads
   and writes the database.
