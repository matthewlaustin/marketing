"""API list prices, dollars per million tokens, for the models the pipeline may use."""
RATES = {
    "claude-fable-5-1":  {"input": 10.0, "output": 50.0, "cache_read": 0.25, "cache_write": 12.50},
    "claude-opus-5-5":   {"input": 4.0,  "output": 20.0, "cache_read": 0.20, "cache_write": 5.0},
    "claude-sonnet-5-5": {"input": 2.0,  "output": 10.0, "cache_read": 0.20, "cache_write": 2.50},
    "claude-haiku-5-5":  {"input": 0.10, "output": 0.50, "cache_read": 0.01, "cache_write": 0.125},
}

def price(usage, model):
    r = RATES.get(model)
    if not r: return None
    g = lambda k: (getattr(usage, k, None) or 0)
    parts = {"input": g("input_tokens") * r["input"], "output": g("output_tokens") * r["output"],
             "cache_read": g("cache_read_input_tokens") * r["cache_read"], "cache_write": g("cache_creation_input_tokens") * r["cache_write"]}
    parts = {k: v / 1e6 for k, v in parts.items()}
    parts["total"] = sum(parts.values())
    return parts

def estimate_input_cost(chars, model):
    r = RATES.get(model); tokens = chars / 4
    return None if not r else {"tokens_est": int(tokens), "input_cost_est": tokens * r["input"] / 1e6}
