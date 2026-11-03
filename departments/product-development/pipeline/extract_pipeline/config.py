import importlib.util, json, os, re

HERE = os.path.dirname(os.path.abspath(__file__))
PIPELINE_DIR = os.path.dirname(HERE)
DEPT_DIR = os.path.dirname(PIPELINE_DIR)
REPO_ROOT = os.path.dirname(os.path.dirname(DEPT_DIR))
SKILL_SCRIPTS = os.path.join(DEPT_DIR, ".claude", "skills", "extract-product", "scripts")
WORK_DIR = os.path.join(REPO_ROOT, "work")

def load_module(name, path):
    spec = importlib.util.spec_from_file_location(name, path)
    mod = importlib.util.module_from_spec(spec); spec.loader.exec_module(mod)
    return mod

fetch_mod = load_module("fetch_mod", os.path.join(SKILL_SCRIPTS, "fetch.py"))
fetch_one = fetch_mod.fetch_one

def load_brands():
    return json.load(open(os.path.join(PIPELINE_DIR, "brands.json")))

def brand_config(slug):
    b = load_brands().get(slug)
    if not b:
        raise SystemExit(f"brand '{slug}' is not in pipeline/brands.json; add it with its domains, sitemap and category pages")
    return b

def load_fields(type_slug):
    path = os.path.join(DEPT_DIR, "product-types", type_slug, "fields.json")
    if not os.path.exists(path):
        raise SystemExit(f"no field list at {path}")
    ft = json.load(open(path))
    if ft.get("status") != "approved":
        raise SystemExit(f"product type {type_slug} is {ft.get('status')}, not approved: nothing is extracted for it (schema first)")
    return ft

def slugify(s):
    return re.sub(r"[^a-z0-9]+", "-", s.lower()).strip("-")

def system_prompt():
    return open(os.path.join(PIPELINE_DIR, "prompts", "system.md")).read()
