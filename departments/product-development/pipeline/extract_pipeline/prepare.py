"""Fetch the product page and the documents it links to, and build the text bundle for the model."""
import os, re
from urllib.parse import urljoin
from .config import fetch_one

CAPS = {"html": 60_000, "manual": 160_000, "spec_sheet": 50_000, "other": 40_000}
TOTAL_CAP = 280_000  # characters, roughly 70k tokens
SKIP = ("curve", "drawing", "dimension", "cad", "dxf", "dwg", "parts_list", "exploded", "map_", "policy", "price")

def classify(url):
    u = url.lower()
    if any(k in u for k in SKIP): return None
    if "manual" in u or "instruction" in u or "/is" in u: return "manual"
    if any(k in u for k in ("literature", "sell", "spec", "brochure", "sheet", "catalog", "lit")): return "spec_sheet"
    return "other"

def _links(html, base):
    return [urljoin(base, h) for h in re.findall(r'(?:href|src)=["\']([^"\'#]+)', html)]

def _meta(html, prop):
    m = re.search(r'<meta[^>]+(?:property|name)=["\']' + re.escape(prop) + r'["\'][^>]+content=["\']([^"\']+)', html, re.I)
    return m.group(1) if m else None

def prepare(product_url, srcdir, max_pdfs=3):
    page = fetch_one(product_url, srcdir)
    html = open(page["raw"], errors="replace").read()
    text = open(page["text"], errors="replace").read()
    sources = [{"url": product_url, "kind": "html", "title": page["title"], "text": text[:CAPS["html"]], "chars": len(text), "truncated": len(text) > CAPS["html"], "fetched_at": page["fetched_at"], "used": True}]
    pdfs = []
    for l in _links(html, product_url):
        if ".pdf" not in l.lower(): continue
        kind = classify(l)
        if kind is None or any(p["url"] == l for p in pdfs): continue
        pdfs.append({"url": l, "kind": kind})
    order = {"manual": 0, "spec_sheet": 1, "other": 2}
    pdfs.sort(key=lambda p: order[p["kind"]])
    skipped = []
    have_core = any(p["kind"] in ("manual", "spec_sheet") for p in pdfs)
    for p in pdfs:
        # A PDF of unknown kind (a pricing policy, a catalog) is only worth tokens when nothing better exists.
        if p["kind"] == "other" and have_core: skipped.append(p["url"]); continue
        if sum(1 for s in sources if s["kind"] != "html") >= max_pdfs: skipped.append(p["url"]); continue
        try:
            rec = fetch_one(p["url"], srcdir)
        except RuntimeError as e:
            skipped.append(p["url"] + " (" + str(e)[:80] + ")"); continue
        t = open(rec["text"], errors="replace").read()
        if len(t.strip()) < 200:
            sources.append({"url": p["url"], "kind": p["kind"], "title": "", "text": "", "chars": len(t), "truncated": False, "fetched_at": rec["fetched_at"], "used": False, "note": "no extractable text"})
            continue
        cap = CAPS.get(p["kind"], CAPS["other"])
        sources.append({"url": p["url"], "kind": p["kind"], "title": "", "text": t[:cap], "chars": len(t), "truncated": len(t) > cap, "fetched_at": rec["fetched_at"], "used": True})
    total = 0
    for s in sources:
        room = max(0, TOTAL_CAP - total)
        if len(s["text"]) > room: s["text"] = s["text"][:room]; s["truncated"] = True
        total += len(s["text"])
    media = []
    img = _meta(html, "og:image")
    if img: media.append({"kind": "image", "url": urljoin(product_url, img), "source_url": product_url})
    for s in sources:
        if s["kind"] in ("manual", "spec_sheet"): media.append({"kind": s["kind"], "url": s["url"], "source_url": product_url})
    return {"product_url": product_url, "page_title": page["title"], "sources": sources, "media": media, "skipped": skipped, "total_chars": total}

def bundle_text(bundle):
    parts = []
    for i, s in enumerate(bundle["sources"], 1):
        if not s.get("used"): continue
        parts.append(f"===== SOURCE {i}: {s['kind']} =====\nURL: {s['url']}\n" + (f"TITLE: {s['title']}\n" if s.get("title") else "") + ("(truncated)\n" if s["truncated"] else "") + "\n" + s["text"] + "\n")
    return "\n".join(parts)
