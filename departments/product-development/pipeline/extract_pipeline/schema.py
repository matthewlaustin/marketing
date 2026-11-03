"""Build the structured-output schema from a product type's field list, so the model can only emit agreed keys with valid values."""

def _value_schema(f):
    dt = f["data_type"]
    if dt == "number": return {"type": "number"}
    if dt == "boolean": return {"type": "boolean"}
    if dt == "text": return {"type": "string"}
    if dt == "enum": return {"type": "string", "enum": list(f["allowed_values"])}
    if dt == "multi_enum": return {"type": "array", "items": {"type": "string", "enum": list(f["allowed_values"])}}
    raise ValueError(dt)

def _obj(props, required=None):
    return {"type": "object", "properties": props, "required": list(required if required is not None else props.keys()), "additionalProperties": False}

def _nullable(s): return {"anyOf": [s, {"type": "null"}]}
S = {"type": "string"}

def build_schema(fields_json):
    keys = [f["key"] for f in fields_json["fields"]]
    specs = _obj({f["key"]: _nullable(_obj({"value": _value_schema(f), "source_url": S, "quote": S, "notes": _nullable(S)})) for f in fields_json["fields"]})
    product = _obj({
        "title": S, "long_description": S,
        "manufacturer_description": _nullable(S), "manufacturer_features": {"type": "array", "items": S}, "manufacturer_content_source_url": _nullable(S),
        "warranty_years": _nullable({"type": "number"}),
        "warranty_type": _nullable({"type": "string", "enum": ["full", "limited", "prorated"]}),
        "warranty_conditions": _nullable(S), "warranty_component_terms": _nullable(S), "warranty_source_url": _nullable(S),
    })
    left_out = {"type": "array", "items": _obj({"key": {"type": "string", "enum": keys}, "reason": S})}
    linked = {"type": "array", "items": _obj({"kind": {"type": "string", "enum": ["accessory", "replacement_part", "compatible_with"]}, "mpn": S, "title": S, "source_url": S, "notes": _nullable(S)})}
    proposed = {"type": "array", "items": _obj({"suggested_key": S, "suggested_label": S, "example_value": S, "source_url": S, "rationale": S})}
    return _obj({"product": product, "specs": specs, "left_out": left_out, "linked_products": linked, "proposed_spec_fields": proposed, "review_notes": {"type": "array", "items": S}})
