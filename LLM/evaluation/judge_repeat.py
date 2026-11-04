# Second judge run (repeat 1) on the first 50 distinct held-out texts written by Gemini, for repeatability.
from evaluation.trace_baselines import judge_texts
from evaluation.trace_score import load, pool_items
pool = pool_items(); texts = []
for r in load("gemini"): texts += [pool[r["id"]]["text"], r.get("rewritten", "")]
judge_texts(list(dict.fromkeys(t for t in texts if t))[:50], repeat=1)
