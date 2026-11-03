"""Run the extraction pipeline for one product.

  python -m extract_pipeline --brand hayward --mpn VSP32940 [--url <product page>]
         [--type pool-pump] [--model claude-sonnet-5-5] [--effort medium] [--dry-run] [--fallbacks]

Needs ANTHROPIC_API_KEY in the environment unless --dry-run. Writes work/drafts/pipeline/<brand>__<mpn>.json and .sql,
runs the validator, and prints token usage and cost at API list prices.
"""
import argparse, json, os, subprocess, sys, time
from . import config
from .discover import discover
from .prepare import prepare
from .schema import build_schema
from .extract import build_messages, call_model, to_record
from .cost import price, estimate_input_cost

def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--brand", required=True, help="brand slug as in brands.json, e.g. hayward")
    ap.add_argument("--mpn", required=True, help="manufacturer part number, exactly as the manufacturer writes it")
    ap.add_argument("--url", help="the manufacturer's product page; skips discovery")
    ap.add_argument("--type", default="pool-pump", help="product type slug (must be approved)")
    ap.add_argument("--model", default="claude-sonnet-5-5")
    ap.add_argument("--effort", default="medium", choices=["low", "medium", "high", "xhigh", "max"])
    ap.add_argument("--max-tokens", type=int, default=16000)
    ap.add_argument("--max-pdfs", type=int, default=3)
    ap.add_argument("--dry-run", action="store_true", help="fetch and prepare only; write the prompt bundle and estimate cost, no model call")
    ap.add_argument("--fallbacks", action="store_true", help="use the server-side refusal fallback (beta)")
    a = ap.parse_args()

    t0 = time.time()
    brand_cfg = config.brand_config(a.brand)
    fields = config.load_fields(a.type)
    tag = f"{a.brand}__{a.mpn}"
    srcdir = os.path.join(config.WORK_DIR, "sources", "pipeline", tag)
    outdir = os.path.join(config.WORK_DIR, "drafts", "pipeline"); os.makedirs(outdir, exist_ok=True)

    url = a.url
    if not url:
        cands, notes = discover(brand_cfg, a.mpn, os.path.join(srcdir, "discovery"))
        for n in notes: print("discover:", n)
        if not cands:
            print(f"No product page found for {a.mpn} on {brand_cfg['name']}'s site. Give it with --url."); sys.exit(2)
        url = cands[0]
        if len(cands) > 1: print("discover: several candidates, using the first:", *cands, sep="\n  ")
    print("product page:", url)

    bundle = prepare(url, srcdir, max_pdfs=a.max_pdfs)
    used = [s for s in bundle["sources"] if s.get("used")]
    print(f"sources: {len(used)} used ({', '.join(s['kind'] for s in used)}), {len(bundle['sources']) - len(used)} without text, {len(bundle['skipped'])} skipped; {bundle['total_chars']:,} characters")
    for s in bundle["sources"]:
        if s.get("truncated"): print("  truncated:", s["url"])

    messages = build_messages(fields, bundle, brand_cfg["name"], a.mpn)
    schema = build_schema(fields)
    system_text = config.system_prompt()
    if a.dry_run:
        dry = os.path.join(outdir, tag + ".dryrun.json")
        slim = dict(bundle); slim["sources"] = [{k: v for k, v in s.items() if k != "text"} for s in bundle["sources"]]
        json.dump({"model": a.model, "brand": a.brand, "mpn": a.mpn, "type": a.type, "url": url, "bundle": slim,
                   "system": system_text, "messages": messages, "schema": schema}, open(dry, "w"), indent=1)
        chars = len(system_text) + sum(len(c["text"]) for c in messages[0]["content"])
        est = estimate_input_cost(chars, a.model)
        print(f"dry run: prompt written to {dry}; about {est['tokens_est']:,} input tokens, input cost about ${est['input_cost_est']:.3f} at {a.model} rates (output extra)")
        return

    if not os.environ.get("ANTHROPIC_API_KEY") and not os.environ.get("ANTHROPIC_AUTH_TOKEN"):
        print("ANTHROPIC_API_KEY is not set. Add it to the environment (or use --dry-run)."); sys.exit(2)
    import anthropic
    client = anthropic.Anthropic()
    data, resp = call_model(client, a.model, a.effort, system_text, messages, schema, max_tokens=a.max_tokens, fallbacks=a.fallbacks)
    rec = to_record(data, fields, bundle, brand_cfg, a.brand, a.mpn, resp.model, url)
    out_json = os.path.join(outdir, tag + ".json")
    json.dump(rec, open(out_json, "w"), indent=2)

    val = subprocess.run([sys.executable, "-I", os.path.join(config.SKILL_SCRIPTS, "validate_record.py"), out_json], capture_output=True, text=True)
    print(val.stdout.strip())
    sql_ok = False
    if val.returncode == 0:
        out_sql = os.path.join(outdir, tag + ".sql")
        gen = subprocess.run([sys.executable, "-I", os.path.join(config.SKILL_SCRIPTS, "draft_to_sql.py"), out_json], capture_output=True, text=True)
        if gen.returncode == 0:
            open(out_sql, "w").write(gen.stdout); sql_ok = True
        else:
            print("SQL generation failed:", gen.stderr.strip())

    u = resp.usage
    cost = price(u, resp.model)
    print(f"\nmodel served: {resp.model}  effort: {a.effort}  time: {time.time() - t0:.0f}s")
    print(f"tokens: input {u.input_tokens:,}  output {u.output_tokens:,}  cache read {(u.cache_read_input_tokens or 0):,}  cache write {(u.cache_creation_input_tokens or 0):,}")
    if cost: print(f"cost at API list prices: ${cost['total']:.3f}  (input ${cost['input']:.3f}, output ${cost['output']:.3f}, cache read ${cost['cache_read']:.3f}, cache write ${cost['cache_write']:.3f})")
    print(f"draft: {out_json}" + (f"\nload file: {out_sql}" if sql_ok else "\nno load file: fix the validator errors first"))
    for n in rec.get("review_notes", []): print("review:", n)

if __name__ == "__main__":
    main()
