-- Seed: pool-pump product type and its agreed field list.
--
-- Source of truth for this list is
-- departments/product-development/product-types/pool-pump/fields.json.
-- This file must be kept in step with it. Re-running is safe: existing rows
-- are updated in place, matched by (product type, key).
--
-- The type is loaded with the status given in fields.json. It becomes
-- 'approved' only after the field list has been reviewed and agreed.

begin;

insert into product_types (slug, name, description, status, version)
values (
  'pool-pump',
  'Pool pump',
  'A pump that circulates water through a swimming pool''s filtration system.',
  'draft',
  1
)
on conflict (slug) do update
  set name        = excluded.name,
      description = excluded.description,
      status      = excluded.status,
      version     = excluded.version;

with t as (select id from product_types where slug = 'pool-pump'),
f(sort_order, key, label, description, data_type, unit, allowed_values, is_required) as (
  values
  (10, 'horsepower',               'Horsepower',               'Rated motor horsepower as stated by the manufacturer.',                                   'number',  'hp',  null,                                               true),
  (20, 'total_horsepower',         'Total horsepower',         'Total horsepower including service factor, where the manufacturer states it.',           'number',  'hp',  null,                                               false),
  (30, 'speed_type',               'Speed type',               'Whether the motor runs at one speed, two speeds, or a continuously variable speed.',       'enum',    null,  '["single", "dual", "variable"]'::jsonb,            true),
  (40, 'voltage',                  'Voltage',                  'Supply voltage the pump is designed for.',                                               'enum',    'V',   '["115", "230", "115/230"]'::jsonb,                  true),
  (50, 'phase',                    'Phase',                    'Single-phase or three-phase electrical supply.',                                         'enum',    null,  '["single", "three"]'::jsonb,                        false),
  (60, 'max_amperage',             'Maximum amperage',         'Highest current draw stated by the manufacturer.',                                       'number',  'A',   null,                                               false),
  (70, 'max_flow_rate',            'Maximum flow rate',        'Highest flow rate stated by the manufacturer, in US gallons per minute.',                'number',  'gpm', null,                                               false),
  (80, 'application',              'Application',              'The kind of pool the pump is intended for.',                                             'enum',    null,  '["inground", "aboveground", "inground_or_aboveground"]'::jsonb, true),
  (90, 'self_priming',             'Self priming',             'Whether the pump can lift water and start on its own without being manually filled.',    'boolean', null,  null,                                               false),
  (100, 'port_size',               'Port size',                'Diameter of the inlet and outlet connections. Text, because unions and mixed sizes occur.', 'text',   'in',  null,                                               true),
  (110, 'housing_material',        'Housing material',         'Material of the pump housing, as stated by the manufacturer.',                           'text',    null,  null,                                               false),
  (120, 'strainer_basket_included','Strainer basket included', 'Whether a hair and lint strainer basket is included.',                                   'boolean', null,  null,                                               false),
  (130, 'energy_star_certified',   'ENERGY STAR certified',    'Whether the pump carries ENERGY STAR certification.',                                    'boolean', null,  null,                                               false),
  (140, 'weighted_energy_factor',  'Weighted energy factor',   'The US Department of Energy efficiency rating (WEF), where published.',                  'number',  null,  null,                                               false),
  (150, 'certifications',          'Certifications',           'Safety and performance listings, for example UL, CSA, NSF/ANSI 50, as a comma-separated list.', 'text', null, null,                                          false),
  (160, 'weight',                  'Weight',                   'Shipping or unit weight in pounds, as stated by the manufacturer.',                      'number',  'lb',  null,                                               false),
  (170, 'dimensions',              'Dimensions',               'Length by width by height in inches, as stated by the manufacturer.',                    'text',    'in',  null,                                               false),
  (180, 'warranty',                'Warranty',                 'The manufacturer''s warranty terms, in the manufacturer''s own words.',                  'text',    null,  null,                                               false)
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
