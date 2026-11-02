# 0004. Media files live in Cloudflare R2

Date: 2026-11-02
Status: agreed (Marketing page, questions 6 and 13)

## Decision

Product media files (images, manuals, spec sheets, videos) are stored in Cloudflare R2, which
we already use. The database stores only each file's URL and what it is, in `product_media`.

## Why

- We already have R2; one less vendor and one less bill.
- Keeping files out of the database keeps the database small and the files servable from a CDN.

## Consequences

- Nothing is built now. Until the first upload is needed, `product_media.url` may point at
  manufacturer-hosted files.
- When upload is needed, the bucket name, folder layout and who may write are a new decision.
