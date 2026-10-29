# Pool pump

**Status:** draft, field list awaiting review. **Version:** 1.

A pool pump circulates water through a swimming pool's filtration system. This is the first
product type and the template for all others. The field list below is what we have agreed to
collect for every pool pump. The same list, in machine-readable form, is in `fields.json`, and
`example.json` shows one filled-in product.

## Shared fields (every product type has these)

These are columns on the `products` table and are not repeated per type: brand, manufacturer
part number (MPN), title, short description, long description, status.

## Specification fields

Required fields must have a value before a product can leave `draft`.

| Key | Label | Type | Unit | Required | Meaning |
|---|---|---|---|---|---|
| `horsepower` | Horsepower | number | hp | yes | Rated motor horsepower as stated by the manufacturer |
| `total_horsepower` | Total horsepower | number | hp | no | Total horsepower including service factor, where the manufacturer states it |
| `speed_type` | Speed type | enum: `single`, `dual`, `variable` | | yes | Whether the motor runs at one speed, two speeds, or a continuously variable speed |
| `voltage` | Voltage | enum: `115`, `230`, `115/230` | V | yes | Supply voltage the pump is designed for |
| `phase` | Phase | enum: `single`, `three` | | no | Single-phase or three-phase electrical supply |
| `max_amperage` | Maximum amperage | number | A | no | Highest current draw stated by the manufacturer |
| `max_flow_rate` | Maximum flow rate | number | gpm | no | Highest flow rate stated by the manufacturer, in US gallons per minute |
| `application` | Application | enum: `inground`, `aboveground`, `inground_or_aboveground` | | yes | The kind of pool the pump is intended for |
| `self_priming` | Self priming | boolean | | no | Whether the pump can lift water and start on its own without being manually filled |
| `port_size` | Port size | text | in | yes | Diameter of the inlet and outlet connections. Text, because unions and mixed sizes occur |
| `housing_material` | Housing material | text | | no | Material of the pump housing, as stated by the manufacturer |
| `strainer_basket_included` | Strainer basket included | boolean | | no | Whether a hair and lint strainer basket is included |
| `energy_star_certified` | ENERGY STAR certified | boolean | | no | Whether the pump carries ENERGY STAR certification |
| `weighted_energy_factor` | Weighted energy factor | number | | no | The US Department of Energy efficiency rating (WEF), where published |
| `certifications` | Certifications | text | | no | Safety and performance listings, for example UL, CSA, NSF/ANSI 50, as a comma-separated list |
| `weight` | Weight | number | lb | no | Shipping or unit weight in pounds, as stated by the manufacturer |
| `dimensions` | Dimensions | text | in | no | Length by width by height in inches, as stated by the manufacturer |
| `warranty` | Warranty | text | | no | The manufacturer's warranty terms, in the manufacturer's own words |

## Notes for extraction

- Record numbers without units; the unit is fixed by the field.
- If a manufacturer gives horsepower as a range or as "up to", record the stated rated value
  in `horsepower` and put the rest in the value's notes.
- `port_size` is text on purpose: write it the way the manufacturer does, for example
  `2 x 2.5 union`.
- Anything useful that is not in this table (noise level, cord length, motor frame, flow
  curves) is a proposed field, not a spec. See the department `README.md`.

## Open questions for review

- Is `voltage` better as text? The enum covers the common North American cases and refuses
  anything else, which is the point, but a 208 V or dual-rated pump would need a new value.
- Should `warranty` be split into a number of years and a text note? Kept as text for now
  because manufacturers phrase warranties inconsistently.
