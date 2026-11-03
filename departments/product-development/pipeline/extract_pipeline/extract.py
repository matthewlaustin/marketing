"""One model call that turns the source bundle into a draft record."""
import datetime, json
from .schema import build_schema
from .prepare import bundle_text

def build_messages(fields_json, bundle, brand_name, mpn):
    fl = [{k: f.get(k) for k in ("key", "label", "data_type", "unit", "required", "allowed_values", "description") if f.get(k) is not None} for f in fields_json["fields"]]
    head = (f"Product type: {fields_json['name']} ({fields_json['slug']}).\nBrand: {brand_name}. Manufacturer part number: {mpn}.\n"
            f"Agreed field list (JSON):\n{json.dumps(fl, indent=1)}\n\nDocuments follow. Each begins with '===== SOURCE n' and its URL; use that URL as source_url.\n")
    return [{"role": "user", "content": [{"type": "text", "text": head}, {"type": "text", "text": bundle_text(bundle)}]}]

def call_model(client, model, effort, system_text, messages, schema, max_tokens=16000, fallbacks=False):
    kwargs = dict(model=model, max_tokens=max_tokens,
                  system=[{"type": "text", "text": system_text, "cache_control": {"type": "ephemeral"}}],
                  messages=messages, output_config={"effort": effort, "format": {"type": "json_schema", "schema": schema}})
    if fallbacks:
        resp = client.beta.messages.create(betas=["server-side-fallback-2026-07-01"], fallbacks="default", **kwargs)
    else:
        resp = client.messages.create(**kwargs)
    if resp.stop_reason == "refusal":
        raise RuntimeError("the model declined this request (stop_reason refusal): " + str(getattr(resp, "stop_details", "")))
    if resp.stop_reason == "max_tokens":
        raise RuntimeError("output was cut off at max_tokens; raise --max-tokens")
    text = next(b.text for b in resp.content if b.type == "text")
    return json.loads(text), resp

def to_record(data, fields_json, bundle, brand_cfg, brand_slug, mpn, model, product_url):
    today = datetime.date.today().isoformat()
    specs = []
    for f in fields_json["fields"]:
        e = data["specs"].get(f["key"])
        if not e: continue
        s = {"key": f["key"], "value": e["value"], "source_url": e["source_url"], "quote": e.get("quote", ""), "extracted_at": today, "extracted_by": "pipeline:" + model, "verified_by": None}
        if e.get("notes"): s["notes"] = e["notes"]
        specs.append(s)
    p = data["product"]
    product = {"product_type": fields_json["slug"], "mpn": mpn, "title": p.get("title"), "short_description": p.get("short_description"), "long_description": p.get("long_description"),
               "warranty_years": p.get("warranty_years"), "warranty_type": p.get("warranty_type"), "warranty_conditions": p.get("warranty_conditions"),
               "warranty_component_terms": p.get("warranty_component_terms"), "warranty_source_url": p.get("warranty_source_url"), "status": "draft"}
    rec = {
        "_note": f"Drafted by the extraction pipeline ({model}) from {product_url}. Review before loading.",
        "manufacturer": brand_cfg["manufacturer"],
        "brand": {"name": brand_cfg["name"], "slug": brand_slug, "website": brand_cfg.get("website")},
        "product": product,
        "specs": specs,
        "left_out": {x["key"]: x["reason"] for x in data.get("left_out", [])},
        "media": bundle["media"],
        "linked_products": [{"kind": l["kind"], "linked_product": {"brand": brand_slug, "mpn": l["mpn"], "title": l.get("title"), "status": "draft"}, "source_url": l["source_url"], "notes": l.get("notes")} for l in data.get("linked_products", [])],
        "proposed_spec_fields": data.get("proposed_spec_fields", []),
        "sources": [{"url": s["url"], "kind": s["kind"], "fetched_at": s["fetched_at"], "title": s.get("title", ""), "used": s.get("used", True), "truncated": s.get("truncated", False)} for s in bundle["sources"]],
        "review_notes": data.get("review_notes", []),
    }
    return rec
