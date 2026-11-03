# Draft record format

One JSON object per product. Keys that start with `_` are ignored by the scripts and may hold
notes. The pool pump `example.json` in the type folder is a complete instance.

| Key | Required | Content |
|---|---|---|
| `manufacturer` | yes | `name`, `slug` (lowercase, hyphens), optional `website` |
| `brand` | yes | `name`, `slug`, optional `website`. Belongs to the manufacturer above |
| `product` | yes | see below |
| `specs` | yes | list of values, one per agreed field, see below |
| `media` | no | list of `{kind, url, title?, alt_text?, sort_order?, source_url?}`; `kind` is `image`, `manual`, `spec_sheet`, `video` or `other` |
| `linked_products` | no | list of `{kind, linked_product: {brand, mpn, title, status: "draft"}, source_url, notes?}`; `kind` is `accessory`, `replacement_part` or `compatible_with` |
| `proposed_spec_fields` | no | list of `{suggested_key, suggested_label?, example_value, source_url, rationale}` |
| `left_out` | recommended | object: field key → one sentence on why no value was recorded (not found, sources disagree, only stated for a variant part number) |
| `sources` | no | list of `{url, kind, fetched_at, title?, used}` for every document read; `used: false` keeps a dead end on record without deleting it |

## `product`

| Key | Required | Content |
|---|---|---|
| `product_type` | yes | the type's slug, for example `pool-pump` |
| `mpn` | yes | manufacturer part number, exactly as the manufacturer writes it |
| `title` | yes for leaving draft | our title |
| `short_description`, `long_description` | no | our text, every claim traceable to a source |
| `manufacturer_description` | recommended | the manufacturer's own product description, word for word |
| `manufacturer_features` | recommended | list of strings: the manufacturer's feature bullets, word for word |
| `manufacturer_content_source_url` | when either is set | where they came from |
| `warranty_years` | no | number |
| `warranty_type` | no | `full`, `limited` or `prorated` |
| `warranty_conditions`, `warranty_component_terms` | no | text |
| `warranty_source_url` | when any warranty field is set | where the warranty came from |
| `status` | yes | always `draft` |

## One entry in `specs`

| Key | Required | Content |
|---|---|---|
| `key` | yes | a field key from the type's `fields.json` |
| `value` | yes | number for `number`; `true`/`false` for `boolean`; string for `text` and `enum`; list of strings for `multi_enum` |
| `source_url` | yes | the page or document the value came from |
| `quote` | recommended | the exact words in the source that give the value |
| `extracted_at` | yes | date, `YYYY-MM-DD` |
| `extracted_by` | yes | `claude`, or a person's name |
| `verified_by` | yes | always `null` from extraction |
| `notes` | no | conversions, ambiguity, why a value was left out |

A field that was not found is absent from `specs` and explained in `left_out`. Do not add a
spec entry with an empty value.
