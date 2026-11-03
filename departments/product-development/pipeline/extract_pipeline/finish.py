"""Finish an extraction whose model answer came from somewhere else (for example a Claude Code
subagent that read the dry-run prompt). Converts the answer into a draft record, validates it
and writes the load SQL.

  python -m extract_pipeline.finish <dryrun.json> <answer.json> [--model <name used>]
"""
import argparse, json, os, subprocess, sys
from . import config
from .extract import to_record

def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("dryrun"); ap.add_argument("answer"); ap.add_argument("--model", default="claude-code-subagent")
    a = ap.parse_args()
    d = json.load(open(a.dryrun)); data = json.load(open(a.answer))
    fields = config.load_fields(d["type"]); brand_cfg = config.brand_config(d["brand"])
    rec = to_record(data, fields, d["bundle"], brand_cfg, d["brand"], d["mpn"], a.model, d["url"])
    tag = f"{d['brand']}__{d['mpn']}"
    outdir = os.path.dirname(os.path.abspath(a.dryrun))
    out_json = os.path.join(outdir, tag + ".json"); json.dump(rec, open(out_json, "w"), indent=2)
    val = subprocess.run([sys.executable, "-I", os.path.join(config.SKILL_SCRIPTS, "validate_record.py"), out_json], capture_output=True, text=True)
    print(val.stdout.strip())
    if val.returncode == 0:
        gen = subprocess.run([sys.executable, "-I", os.path.join(config.SKILL_SCRIPTS, "draft_to_sql.py"), out_json], capture_output=True, text=True)
        if gen.returncode == 0:
            out_sql = os.path.join(outdir, tag + ".sql"); open(out_sql, "w").write(gen.stdout); print("load file:", out_sql)
        else: print("SQL generation failed:", gen.stderr.strip())
    print("draft:", out_json)
    for n in rec.get("review_notes", []): print("review:", n)
    sys.exit(val.returncode)

if __name__ == "__main__":
    main()
