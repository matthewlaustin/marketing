"""Find a product page URL from a brand's sitemaps and category pages. No model involved."""
import os, re, subprocess
from urllib.parse import urljoin

def _get(url, outpath):
    r = subprocess.run(["curl", "-sSL", "--max-time", "60", "-A", "marketing-extract/1.0", "-o", outpath, url], capture_output=True, text=True)
    return r.returncode == 0 and os.path.exists(outpath)

def _sitemap_urls(url, workdir, depth=0, seen=None, limit=25):
    seen = seen if seen is not None else set()
    if url in seen or len(seen) >= limit or depth > 2: return []
    seen.add(url)
    path = os.path.join(workdir, f"sitemap-{len(seen):02d}.xml")
    if not _get(url, path): return []
    data = open(path, errors="replace").read()
    locs = re.findall(r"<loc>\s*(.*?)\s*</loc>", data)
    if "<sitemapindex" in data[:2000]:
        out = []
        for child in locs: out += _sitemap_urls(child, workdir, depth + 1, seen, limit)
        return out
    return locs

def _page_links(url, workdir, name):
    path = os.path.join(workdir, f"{name}.html")
    if not _get(url, path): return []
    data = open(path, errors="replace").read()
    return [urljoin(url, h) for h in re.findall(r'href=["\']([^"\'#]+)', data)]

def discover(brand_cfg, mpn, workdir):
    """Returns (candidates, notes). candidates are product page URLs containing the MPN."""
    os.makedirs(workdir, exist_ok=True)
    key = mpn.lower(); notes = []; found = []
    for sm in brand_cfg.get("sitemaps", []):
        urls = _sitemap_urls(sm, workdir)
        hits = [u for u in urls if key in u.lower()]
        notes.append(f"sitemap {sm}: {len(urls)} urls, {len(hits)} containing {mpn}")
        found += hits
    if not found:
        for i, cp in enumerate(brand_cfg.get("category_pages", [])):
            links = _page_links(cp, workdir, f"category-{i:02d}")
            hits = [u for u in links if key in u.lower()]
            notes.append(f"category page {cp}: {len(links)} links, {len(hits)} containing {mpn}")
            found += hits
    domains = set(brand_cfg.get("domains", []))
    seen, out = set(), []
    for u in found:
        u = u.split("?")[0]
        host = u.split("//", 1)[-1].split("/", 1)[0]
        if u in seen or (domains and host not in domains): continue
        seen.add(u); out.append(u)
    html_pages = [u for u in out if not u.lower().endswith(".pdf")]
    return (html_pages or out), notes
