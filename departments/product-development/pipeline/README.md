# Extraction pipeline

The cheap way to draft a product record. The `extract-product` skill lets Claude work a product
out step by step, which is right for hard cases but costs several dollars per product in model
time. This pipeline does the mechanical parts with ordinary code and asks the model once.

## What it does

1. **Find** the manufacturer's product page from the brand's sitemap or category pages
   (`brands.json` says where to look), or take the URL you give it.
2. **Fetch** the page and the manual and spec sheet it links to, and turn them into text. No
   model is involved, so dead ends cost nothing.
3. **Ask the model once**, with the text, the type's agreed field list and a strict output
   format built from that list, so the answer can only contain agreed fields with valid values.
4. **Validate** the draft with the same checker the skill uses, and write the load SQL.
5. **Report** what was filled, what was left out and why, and the cost at API list prices.

Anything the validator rejects, any required field left empty, or any source conflict is for a
person or for the skill to look at. Most products should never need that.

## Running it

From this folder:

```
pip install -r requirements.txt
export ANTHROPIC_API_KEY=...        # billed per token on the API, not through a Claude subscription
python -m extract_pipeline --brand hayward --mpn VSP32940 --url https://www.hayward.com/tristar-vs-940-pump-4-0hp-vsp32940.html
```

Leave out `--url` to let it search the brand's site. Add `--dry-run` to fetch and prepare
without calling the model; it writes the exact prompt and estimates the input cost. `--model`
and `--effort` choose the model (default Claude Sonnet 5.5, medium effort). Output goes to
`work/drafts/pipeline/`, which git ignores.

## Running it from Claude Code, without an API key

The model step can also be done by a Claude Code subagent on the subscription instead of the
API. Run the pipeline with `--dry-run`, which writes `work/drafts/pipeline/<brand>__<mpn>.dryrun.json`
holding the instructions, the documents and the output format. Ask Claude to have a subagent of
the chosen model read that file, write its answer as `<brand>__<mpn>.answer.json`, and run:

```
python -m extract_pipeline.finish work/drafts/pipeline/<brand>__<mpn>.dryrun.json work/drafts/pipeline/<brand>__<mpn>.answer.json --model claude-sonnet-5-5
```

The finish step converts the answer into the draft record, validates it and writes the load
SQL, exactly as the API path does.

## Cost

Measured and estimated per product, at API list prices:

| Way of running | Model | Cost per product |
|---|---|---|
| Skill, agent loop, discontinued product with discovery | Fable 5.1 | $7.19 |
| Skill, agent loop, current product with discovery | Fable 5.1 | $4.37 |
| Skill, agent loop, URL given, low effort | Sonnet 5.5 | $0.47 |
| Pipeline, one call, URL given (estimate until measured) | Sonnet 5.5 | $0.10 to $0.20 |

## Adding a brand

Add an entry to `brands.json` with the manufacturer, the website, the hosts that count as the
manufacturer, and the sitemap and category page URLs to scan for part numbers.

## Not yet verified against the live API

This session had no API key, so the model call has not been exercised end to end. Everything
before it (discovery, fetching, the prompt, the output schema) and after it (validation, SQL)
has. The first real run should use `--dry-run` once, then a real call on a known product, and
compare the draft with the skill's draft of the same product.
