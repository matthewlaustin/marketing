-- Seed: pool-pump product type and its agreed field list.
--
-- Source of truth for this list is
-- departments/product-development/product-types/pool-pump/fields.json.
-- This file must be kept in step with it. Re-running is safe: existing rows
-- are updated in place, matched by (product type, key).
--
-- Status: approved, version 3. Version 1 was reviewed field by field on the Marketing
-- page on 2026-11-02; version 2 (2026-11-03) adds 208 and 575 to the voltage list;
-- version 3 (2026-11-03) writes port sizes with their unit, reads "2 x 2.5 in" as two
-- sizes, and drops housing_material and strainer_basket_included.
-- The port_size list stands as proposed until the catalog review.

begin;

insert into product_types (slug, name, description, status, version)
values (
  'pool-pump',
  'Pool pump',
  'A pump that circulates water through a swimming pool''s filtration system.',
  'approved',
  3
)
on conflict (slug) do update
  set name        = excluded.name,
      description = excluded.description,
      status      = excluded.status,
      version     = excluded.version;

with t as (select id from product_types where slug = 'pool-pump'),
f(sort_order, key, label, description, data_type, unit, allowed_values, is_required) as (
  values
  (10,  'horsepower',               'Horsepower',               'Rated motor horsepower as stated by the manufacturer.',                                            'number',     'hp',  null,                                                                          true),
  (20,  'total_horsepower',         'Total horsepower',         'Total horsepower including service factor, where the manufacturer states it.',                    'number',     'hp',  null,                                                                          false),
  (30,  'speed_type',               'Speed type',               'Whether the motor runs at one speed, two speeds, or a continuously variable speed.',                'enum',       null,  '["single", "dual", "variable"]'::jsonb,                                       true),
  (40,  'voltage',                  'Voltage',                  'Every supply voltage the pump itself is rated for. A 115/230 pump records both; a 208-230 pump records 208 and 230. 460 and 575 are three-phase only.', 'multi_enum', 'V', '["115", "208", "230", "460", "575"]'::jsonb, true),
  (50,  'phase',                    'Phase',                    'Single-phase or three-phase electrical supply.',                                                  'enum',       null,  '["single", "three"]'::jsonb,                                                   false),
  (60,  'max_amperage',             'Maximum amperage',         'Highest current draw stated by the manufacturer.',                                                'number',     'A',   null,                                                                          false),
  (70,  'max_flow_rate',            'Maximum flow rate',        'Highest flow rate stated by the manufacturer, in US gallons per minute.',                         'number',     'gpm', null,                                                                          false),
  (80,  'application',              'Application',              'Every kind of pool the pump is intended for. A pump suited to both records both.',                 'multi_enum', null,  '["aboveground", "inground"]'::jsonb,                                          true),
  (90,  'self_priming',             'Self priming',             'Whether the pump can lift water and start on its own without being manually filled.',             'boolean',    null,  null,                                                                          false),
  (100, 'port_size',                'Port size',                'Every connection size the pump itself accepts. "2 x 2.5 in unions" means 2.0 in and 2.5 in. A size the manufacturer marks optional is not recorded.', 'multi_enum', null, '["1.0 in", "1.5 in", "2.0 in", "2.5 in", "3.0 in", "3.5 in", "4.0 x 6.0 in ANSI flange"]'::jsonb, true),
  (130, 'energy_star_certified',    'ENERGY STAR certified',    'Whether the pump carries ENERGY STAR certification.',                                             'boolean',    null,  null,                                                                          false),
  (140, 'weighted_energy_factor',   'Weighted energy factor',   'The US Department of Energy efficiency rating (WEF), where published.',                           'number',     null,  null,                                                                          false),
  (150, 'certifications',           'Certifications',           'Safety and performance listings, for example UL, CSA, NSF/ANSI 50, as a comma-separated list.',   'text',       null,  null,                                                                          false),
  (160, 'weight',                   'Weight',                   'Shipping or unit weight in pounds, as stated by the manufacturer.',                               'number',     'lb',  null,                                                                          false),
  (170, 'dimensions',               'Dimensions',               'Length by width by height in inches, as stated by the manufacturer.',                             'text',       'in',  null,                                                                          false)
)
insert into spec_fields (product_type_id, sort_order, key, label, description, data_type, unit, allowed_values, is_required)
select t.id, f.sort_order, f.key, f.label, f.description, f.data_type, f.unit, f.allowed_values, f.is_required
from t, f
on conflict (product_type_id, key) do update
  set sort_order     = excluded.sort_order,
      label          = excluded.label,
      description    = excluded.description,
      data_type      = excluded.data_type,
      unit           = excluded.unit,
      allowed_values = excluded.allowed_values,
      is_required    = excluded.is_required;

commit;
