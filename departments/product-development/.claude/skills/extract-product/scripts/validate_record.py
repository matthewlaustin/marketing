#!/usr/bin/env python3
"""Validate a draft product record against its product type's agreed field list.

Usage: python3 -I validate_record.py <record.json> [<fields.json>]

If fields.json is not given it is found from product.product_type under
departments/product-development/product-types/<type>/fields.json, relative to the repository
root (the nearest ancestor of this script containing CLAUDE.md). Exit code 1 on any error.
"""
import json, os, re, sys

def repo_root():
    d = os.path.dirname(os.path.abspath(__file__))
    while d != "/" and not os.path.exists(os.path.join(d, "CLAUDE.md")) or os.path.basename(d) == "product-development":
        if os.path.exists(os.path.join(d, "database")) and os.path.exists(os.path.join(d, "departments")): break
        d = os.path.dirname(d)
    return d

def main():
    if len(sys.argv) < 2:
        print(__doc__); sys.exit(2)
    rec = json.load(open(sys.argv[1]))
    errors, warnings = [], []
    prod = rec.get("product") or {}
    ptype = prod.get("product_type")
    if len(sys.argv) > 2:
        fpath = sys.argv[2]
    else:
        if not ptype: print("ERROR: product.product_type missing"); sys.exit(1)
        fpath = os.path.join(repo_root(), "departments", "product-development", "product-types", ptype, "fields.json")
    if not os.path.exists(fpath):
        print(f"ERROR: field list not found at {fpath}"); sys.exit(1)
    ft = json.load(open(fpath))
    if ft.get("status") != "approved":
        errors.append(f"product type {ft.get('slug')} is {ft.get('status')}, not approved: nothing may be extracted for it (schema first)")
    fields = {f["key"]: f for f in ft.get("fields", [])}

    for key in ("manufacturer", "brand"):
        o = rec.get(key) or {}
        if not o.get("name") or not o.get("slug"): errors.append(f"{key} needs name and slug")
        elif not re.fullmatch(r"[a-z0-9]+(-[a-z0-9]+)*", o["slug"]): errors.append(f"{key}.slug must be lowercase with hyphens: {o['slug']}")
    if not prod.get("mpn"): errors.append("product.mpn is required")
    if prod.get("status") != "draft": errors.append("product.status must be draft from extraction")
    if not prod.get("title"): warnings.append("product.title is empty; the product cannot leave draft without it")
    wt = prod.get("warranty_type")
    if wt not in (None, "full", "limited", "prorated"): errors.append(f"warranty_type must be full, limited or prorated, not {wt!r}")
    wy = prod.get("warranty_years")
    if wy is not None and (not isinstance(wy, (int, float)) or isinstance(wy, bool) or wy < 0): errors.append("warranty_years must be a non-negative number")
    if any(prod.get(k) not in (None, "") for k in ("warranty_years", "warranty_type", "warranty_conditions", "warranty_component_terms")) and not prod.get("warranty_source_url"):
        errors.append("warranty fields are set but warranty_source_url is missing")

    seen = set()
    for i, s in enumerate(rec.get("specs") or []):
        k = s.get("key"); where = f"specs[{i}] ({k})"
        if k not in fields: errors.append(f"{where}: not an agreed field of {ptype}; use proposed_spec_fields instead"); continue
        if k in seen: errors.append(f"{where}: duplicate key"); continue
        seen.add(k)
        f = fields[k]; v = s.get("value"); dt = f["data_type"]
        ok = (dt == "number" and isinstance(v, (int, float)) and not isinstance(v, bool)) or \
             (dt == "boolean" and isinstance(v, bool)) or \
             (dt == "text" and isinstance(v, str) and v.strip() != "") or \
             (dt == "enum" and isinstance(v, str) and v in f.get("allowed_values", [])) or \
             (dt == "multi_enum" and isinstance(v, list) and v and len(set(v)) == len(v) and all(isinstance(x, str) and x in f.get("allowed_values", []) for x in v))
        if not ok: errors.append(f"{where}: value {v!r} does not fit {dt}" + (f" from {f.get('allowed_values')}" if dt in ("enum", "multi_enum") else ""))
        if not s.get("source_url"): errors.append(f"{where}: every value needs a source_url")
        if s.get("verified_by"): errors.append(f"{where}: verified_by must be null from extraction; verification is a person's action")
        if not s.get("extracted_at"): errors.append(f"{where}: extracted_at missing")
        if not s.get("quote"): warnings.append(f"{where}: no quote from the source; a reviewer will have to re-read the document")
        txt = " ".join(str(s.get(x, "")) for x in ("quote", "notes")).lower()
        if "optional" in txt and dt == "multi_enum": warnings.append(f"{where}: the source mentions 'optional'; make sure optional sizes are linked as accessories, not recorded")

    missing_req = [k for k, f in fields.items() if f.get("required") and k not in seen]
    missing_opt = [k for k, f in fields.items() if not f.get("required") and k not in seen]
    if missing_req: warnings.append("required fields without a value (product stays in draft): " + ", ".join(missing_req))
    if missing_opt: warnings.append("optional fields without a value: " + ", ".join(missing_opt))

    for i, m in enumerate(rec.get("media") or []):
        if m.get("kind") not in ("image", "manual", "spec_sheet", "video", "other") or not m.get("url"): errors.append(f"media[{i}]: needs a kind (image, manual, spec_sheet, video, other) and a url")
    for i, l in enumerate(rec.get("linked_products") or []):
        lp = l.get("linked_product") or {}
        if l.get("kind") not in ("accessory", "replacement_part", "compatible_with"): errors.append(f"linked_products[{i}]: kind must be accessory, replacement_part or compatible_with")
        if not lp.get("brand") or not lp.get("mpn"): errors.append(f"linked_products[{i}]: linked_product needs brand and mpn")
        if not l.get("source_url"): errors.append(f"linked_products[{i}]: needs a source_url")
    for i, p in enumerate(rec.get("proposed_spec_fields") or []):
        if not re.fullmatch(r"[a-z][a-z0-9_]*", p.get("suggested_key", "")): errors.append(f"proposed_spec_fields[{i}]: suggested_key must be lowercase with underscores")
        if not p.get("source_url"): errors.append(f"proposed_spec_fields[{i}]: needs a source_url")

    total, req = len(fields), sum(1 for f in fields.values() if f.get("required"))
    print(f"Type: {ptype} ({ft.get('status')}, v{ft.get('version')}). Filled {len(seen)} of {total} fields, {req - len(missing_req)} of {req} required.")
    for w in warnings: print("WARNING:", w)
    for e in errors: print("ERROR:", e)
    print("RESULT:", "errors" if errors else "ok")
    sys.exit(1 if errors else 0)

if __name__ == "__main__":
    main()
