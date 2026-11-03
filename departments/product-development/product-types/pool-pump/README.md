# Pool pump

**Status:** approved. **Version:** 3. Version 1 was reviewed field by field on the Marketing
page on 2026-11-02. Version 2 added 208 and 575 to the voltage list. Version 3 writes port
sizes with their unit, reads "2 x 2.5 in" as two sizes, and drops housing material and strainer
basket (all 2026-11-03, owner's decisions in chat). The shared short description was dropped the
same day (Marketing page, question 24).

A pool pump circulates water through a swimming pool's filtration system. This is the first
product type and the template for all others. The field list below is what we have agreed to
collect for every pool pump. The same list, in machine-readable form, is in `fields.json`, and
`example.json` shows one filled-in product.

## Shared fields (every product type has these)

These are columns on the `products` table and are not repeated per type.

| Field | Meaning |
|---|---|
| brand | The brand the product is sold under. Each brand belongs to a manufacturer |
| mpn | Manufacturer part number: the identifier the manufacturer itself uses. Unique within a brand |
| title | Our product title. Required before a product leaves draft |
| long_description | Our description |
| manufacturer_description | The manufacturer's own product description, word for word |
| manufacturer_features | The manufacturer's own feature bullets, one per line, word for word |
| manufacturer_content_source_url | Where the description and features came from |
| warranty_years | The headline warranty term as a number of years, so products compare across brands |
| warranty_type | One of `full`, `limited`, `prorated` |
| warranty_conditions | What the manufacturer requires for the full term, in its own words |
| warranty_component_terms | Only when parts differ, for example motor 3 years and wet end 1 year |
| status | `draft`, `in_review`, `approved`, `published` |

Warranty is standardized this way across brands and product types (decision 0005), so there
is no pump-specific warranty field.

## Specification fields

Required fields must have a value before a product can leave `draft`. "Several from a list"
means more than one of the allowed values can be recorded for one product.

| Key | Label | Type | Unit | Required | Meaning |
|---|---|---|---|---|---|
| `horsepower` | Horsepower | number | hp | yes | Rated motor horsepower as stated by the manufacturer |
| `total_horsepower` | Total horsepower | number | hp | no | Total horsepower including service factor, where the manufacturer states it |
| `speed_type` | Speed type | one of: `single`, `dual`, `variable` | | yes | Whether the motor runs at one speed, two speeds, or a continuously variable speed |
| `voltage` | Voltage | several from: `115`, `208`, `230`, `460`, `575` | V | yes | Every supply voltage the pump itself is rated for. A 115/230 pump records both; a 208-230 pump records 208 and 230 |
| `phase` | Phase | one of: `single`, `three` | | no | Single-phase or three-phase electrical supply |
| `max_amperage` | Maximum amperage | number | A | no | Highest current draw stated by the manufacturer |
| `max_flow_rate` | Maximum flow rate | number | gpm | no | Highest flow rate stated by the manufacturer, in US gallons per minute |
| `application` | Application | several from: `aboveground`, `inground` | | yes | Every kind of pool the pump is intended for. A pump suited to both records both |
| `self_priming` | Self priming | yes/no | | no | Whether the pump can lift water and start on its own without being manually filled |
| `port_size` | Port size | several from: `1.0 in`, `1.5 in`, `2.0 in`, `2.5 in`, `3.0 in`, `3.5 in`, `4.0 x 6.0 in ANSI flange` | | yes | Every connection size the pump itself accepts |
| `energy_star_certified` | ENERGY STAR certified | yes/no | | no | Whether the pump carries ENERGY STAR certification |
| `weighted_energy_factor` | Weighted energy factor | number | | no | The US Department of Energy efficiency rating (WEF), where published |
| `certifications` | Certifications | text | | no | Safety and performance listings, for example UL, CSA, NSF/ANSI 50, as a comma-separated list |
| `weight` | Weight | number | lb | no | Shipping or unit weight in pounds, as stated by the manufacturer |
| `dimensions` | Dimensions | text | in | no | Length by width by height in inches, as stated by the manufacturer |

## Rules for extraction

- Record numbers without units; the unit is fixed by the field.
- **Voltage and phase are separate facts.** 115, 208 and 230 are usually single-phase; 460 and
  575 are three-phase only, so a product with either must have `phase` = `three`. A "208-230 V"
  rating records both 208 and 230.
- **Record every size and voltage the product itself has.** A pump rated 115/230 gets both
  voltages. A pump described as having "2 x 2.5 in unions" gets both `2.0 in` and `2.5 in`;
  that phrasing means the unions fit both sizes.
- **A size or voltage the manufacturer marks "optional" is not recorded.** Optional means an
  accessory makes it possible; the product is not that size. The accessory becomes a draft
  product of its own and is linked to the pump in `product_links` with kind `accessory`.
- If a manufacturer gives horsepower as a range or as "up to", record the stated rated value
  in `horsepower` and put the rest in the value's notes.
- Anything useful that is not in this table (noise level, cord length, motor frame, flow
  curves) is a proposed field, not a spec. See the department `README.md`.

## Pending

- **Port size list.** The seven values come from the owner's knowledge of the catalog. A review
  of real listings was requested and is waiting on network access to poolgeek.com. If the review
  finds other sizes, the list is extended as version 2.
