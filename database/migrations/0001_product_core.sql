-- 0001_product_core.sql
--
-- Creates the core product data model for the product development department.
-- See docs/architecture.md for the model in plain language and
-- docs/decisions/0002 and 0003 for why it is shaped this way.
--
-- Safe to run exactly once per database. Run it on a Neon branch first
-- (see database/README.md).

begin;

-- ---------------------------------------------------------------------------
-- Helper: keep updated_at current on any table that has the column.
-- ---------------------------------------------------------------------------
create or replace function set_updated_at() returns trigger
language plpgsql as $$
begin
  new.updated_at := now();
  return new;
end
$$;

-- ---------------------------------------------------------------------------
-- Manufacturers and brands
-- A manufacturer is the company that makes the product. It may own several
-- brands. Products attach to a brand.
-- ---------------------------------------------------------------------------
create table manufacturers (
  id          uuid primary key default gen_random_uuid(),
  name        text not null,
  slug        text not null unique check (slug ~ '^[a-z0-9]+(-[a-z0-9]+)*$'),
  website     text,
  created_at  timestamptz not null default now(),
  updated_at  timestamptz not null default now()
);

create trigger manufacturers_updated_at
  before update on manufacturers
  for each row execute function set_updated_at();

create table brands (
  id               uuid primary key default gen_random_uuid(),
  manufacturer_id  uuid not null references manufacturers(id),
  name             text not null,
  slug             text not null unique check (slug ~ '^[a-z0-9]+(-[a-z0-9]+)*$'),
  website          text,
  created_at       timestamptz not null default now(),
  updated_at       timestamptz not null default now()
);

create trigger brands_updated_at
  before update on brands
  for each row execute function set_updated_at();

-- ---------------------------------------------------------------------------
-- Product types and their agreed field lists (schema first)
-- ---------------------------------------------------------------------------
create table product_types (
  id           uuid primary key default gen_random_uuid(),
  slug         text not null unique check (slug ~ '^[a-z0-9]+(-[a-z0-9]+)*$'),
  name         text not null,
  description  text,
  -- draft: field list still being agreed. approved: extraction may begin.
  status       text not null default 'draft' check (status in ('draft', 'approved')),
  -- Bumped each time the agreed field list changes.
  version      integer not null default 1 check (version >= 1),
  created_at   timestamptz not null default now(),
  updated_at   timestamptz not null default now()
);

create trigger product_types_updated_at
  before update on product_types
  for each row execute function set_updated_at();

-- One row per agreed field per product type. This table IS the schema for a type.
create table spec_fields (
  id               uuid primary key default gen_random_uuid(),
  product_type_id  uuid not null references product_types(id),
  key              text not null check (key ~ '^[a-z][a-z0-9_]*$'),
  label            text not null,
  description      text,
  data_type        text not null check (data_type in ('text', 'number', 'boolean', 'enum')),
  unit             text,
  -- For enum fields only: a JSON array of the allowed string values.
  allowed_values   jsonb,
  is_required      boolean not null default false,
  sort_order       integer not null default 0,
  created_at       timestamptz not null default now(),
  updated_at       timestamptz not null default now(),
  unique (product_type_id, key),
  constraint enum_has_allowed_values check (
    data_type <> 'enum'
    or (allowed_values is not null
        and jsonb_typeof(allowed_values) = 'array'
        and jsonb_array_length(allowed_values) > 0)
  ),
  constraint only_enum_has_allowed_values check (
    data_type = 'enum' or allowed_values is null
  )
);

create trigger spec_fields_updated_at
  before update on spec_fields
  for each row execute function set_updated_at();

-- ---------------------------------------------------------------------------
-- Products
-- Shared fields are columns here. Type-specific fields are in product_specs.
-- ---------------------------------------------------------------------------
create table products (
  id                 uuid primary key default gen_random_uuid(),
  brand_id           uuid not null references brands(id),
  product_type_id    uuid not null references product_types(id),
  -- Manufacturer part number: the identifier the manufacturer itself uses.
  mpn                text not null,
  title              text,
  short_description  text,
  long_description   text,
  status             text not null default 'draft'
                     check (status in ('draft', 'in_review', 'approved', 'published')),
  created_at         timestamptz not null default now(),
  updated_at         timestamptz not null default now(),
  unique (brand_id, mpn)
);

-- ---------------------------------------------------------------------------
-- Product media
-- Files are hosted elsewhere; we store the URL and what it is.
-- ---------------------------------------------------------------------------
create table product_media (
  id          uuid primary key default gen_random_uuid(),
  product_id  uuid not null references products(id) on delete cascade,
  kind        text not null check (kind in ('image', 'manual', 'spec_sheet', 'video', 'other')),
  url         text not null,
  title       text,
  alt_text    text,
  sort_order  integer not null default 0,
  -- Where we found this media, if different from url.
  source_url  text,
  created_at  timestamptz not null default now()
);

-- ---------------------------------------------------------------------------
-- Product specification values
-- One row per product per agreed field. Exactly one value column is filled,
-- chosen by the field's data_type. Every value cites a source.
-- ---------------------------------------------------------------------------
create table product_specs (
  id               uuid primary key default gen_random_uuid(),
  product_id       uuid not null references products(id) on delete cascade,
  spec_field_id    uuid not null references spec_fields(id),
  value_text       text,       -- text and enum fields
  value_number     numeric,    -- number fields
  value_boolean    boolean,    -- boolean fields
  source_url       text,
  source_media_id  uuid references product_media(id) on delete set null,
  extracted_at     timestamptz not null default now(),
  extracted_by     text,       -- person or agent that captured the value
  verified_by      text,       -- person who checked it, if anyone
  verified_at      timestamptz,
  notes            text,
  created_at       timestamptz not null default now(),
  updated_at       timestamptz not null default now(),
  unique (product_id, spec_field_id),
  constraint exactly_one_value check (
    num_nonnulls(value_text, value_number, value_boolean) = 1
  ),
  constraint value_has_source check (
    source_url is not null or source_media_id is not null
  )
);

-- ---------------------------------------------------------------------------
-- Proposed specification fields
-- Holding area for data found during extraction that has no agreed field.
-- Feeds a revision of the field list; never becomes a spec on its own.
-- ---------------------------------------------------------------------------
create table proposed_spec_fields (
  id               uuid primary key default gen_random_uuid(),
  product_type_id  uuid not null references product_types(id),
  product_id       uuid references products(id) on delete set null,
  suggested_key    text not null check (suggested_key ~ '^[a-z][a-z0-9_]*$'),
  suggested_label  text,
  example_value    text,
  source_url       text,
  rationale        text,
  status           text not null default 'proposed'
                   check (status in ('proposed', 'accepted', 'rejected')),
  created_at       timestamptz not null default now(),
  resolved_at      timestamptz
);

-- ---------------------------------------------------------------------------
-- Rule: a spec value must fit its field, and the field must belong to the
-- product's type.
-- ---------------------------------------------------------------------------
create or replace function validate_product_spec() returns trigger
language plpgsql as $$
declare
  f        spec_fields%rowtype;
  p_type   uuid;
begin
  select product_type_id into p_type from products where id = new.product_id;
  select * into f from spec_fields where id = new.spec_field_id;

  if f.product_type_id is distinct from p_type then
    raise exception 'spec field "%" does not belong to this product''s type', f.key
      using errcode = 'check_violation';
  end if;

  case f.data_type
    when 'text' then
      if new.value_text is null then
        raise exception 'field "%" expects a text value in value_text', f.key
          using errcode = 'check_violation';
      end if;
    when 'enum' then
      if new.value_text is null then
        raise exception 'field "%" expects one of % in value_text', f.key, f.allowed_values
          using errcode = 'check_violation';
      end if;
      if not (f.allowed_values ? new.value_text) then
        raise exception 'value "%" is not allowed for field "%". Allowed: %',
          new.value_text, f.key, f.allowed_values
          using errcode = 'check_violation';
      end if;
    when 'number' then
      if new.value_number is null then
        raise exception 'field "%" expects a number in value_number', f.key
          using errcode = 'check_violation';
      end if;
    when 'boolean' then
      if new.value_boolean is null then
        raise exception 'field "%" expects true or false in value_boolean', f.key
          using errcode = 'check_violation';
      end if;
  end case;

  new.updated_at := now();
  return new;
end
$$;

create trigger product_specs_validate
  before insert or update on product_specs
  for each row execute function validate_product_spec();

-- ---------------------------------------------------------------------------
-- Rules on products:
--   * a product can only be created for an approved type (schema first);
--   * a product's type cannot be changed afterwards;
--   * a product cannot leave draft until it has a title and every required
--     field for its type has a value.
-- ---------------------------------------------------------------------------
create or replace function enforce_product_rules() returns trigger
language plpgsql as $$
declare
  t_status  text;
  missing   text;
begin
  if tg_op = 'INSERT' then
    select status into t_status from product_types where id = new.product_type_id;
    if t_status is distinct from 'approved' then
      raise exception 'product type is not approved. Agree its field list first (schema first).'
        using errcode = 'check_violation';
    end if;
  elsif new.product_type_id <> old.product_type_id then
    raise exception 'a product''s type cannot be changed once created'
      using errcode = 'check_violation';
  end if;

  if new.status <> 'draft' then
    if new.title is null or btrim(new.title) = '' then
      raise exception 'product cannot leave draft without a title'
        using errcode = 'check_violation';
    end if;

    select string_agg(sf.key, ', ' order by sf.sort_order, sf.key) into missing
    from spec_fields sf
    where sf.product_type_id = new.product_type_id
      and sf.is_required
      and not exists (
        select 1 from product_specs ps
        where ps.product_id = new.id and ps.spec_field_id = sf.id
      );

    if missing is not null then
      raise exception 'product cannot leave draft. Required fields missing: %', missing
        using errcode = 'check_violation';
    end if;
  end if;

  new.updated_at := now();
  return new;
end
$$;

create trigger products_enforce_rules
  before insert or update on products
  for each row execute function enforce_product_rules();

-- ---------------------------------------------------------------------------
-- Convenience view: one row per product with its specs as a JSON object.
-- Read-only. Storage stays in product_specs.
-- ---------------------------------------------------------------------------
create view product_specs_json as
select
  p.id        as product_id,
  b.slug      as brand,
  p.mpn,
  p.title,
  pt.slug     as product_type,
  p.status,
  coalesce(
    jsonb_object_agg(
      sf.key,
      coalesce(to_jsonb(ps.value_number), to_jsonb(ps.value_boolean), to_jsonb(ps.value_text))
    ) filter (where sf.key is not null),
    '{}'::jsonb
  ) as specs
from products p
join brands b          on b.id  = p.brand_id
join product_types pt  on pt.id = p.product_type_id
left join product_specs ps on ps.product_id = p.id
left join spec_fields sf   on sf.id = ps.spec_field_id
group by p.id, b.slug, p.mpn, p.title, pt.slug, p.status;

commit;
