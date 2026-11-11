"""Second judge run (repeat 1) on the first 50 distinct held-out texts written by Gemini, for repeatability.

The judge model is the configured one (LLM_MODEL). Optional shard arguments let several workers share the texts:

    ../Backend/.venv/bin/python -m evaluation.judge_repeat            # all 50 texts
    ../Backend/.venv/bin/python -m evaluation.judge_repeat 0 4        # the texts of shard 0 of 4
    ../Backend/.venv/bin/python -m evaluation.judge_repeat compare    # writes results/trace/repeat-judge.md
"""
import hashlib
import sys

from evaluation.trace_baselines import judge_texts
from evaluation.trace_score import load, pool_items


def repeat_texts() -> list[str]:
    pool, texts = pool_items(), []
    for record in load("gemini"):
        texts += [pool[record["id"]]["text"], record.get("rewritten", "")]
    return list(dict.fromkeys(text for text in texts if text))[:50]


def compare() -> None:
    """Writes results/trace/repeat-judge.md: how often two runs of each judge agree on the same texts."""
    from evaluation.trace_baselines import OUT, JudgeCache
    from evaluation.trace_score import JUDGE_MODELS

    cache, texts = JudgeCache(), repeat_texts()
    lines = ["# LLM judge repeatability: the same texts asked twice", "",
             "The first 50 distinct held-out texts written by Gemini, same prompt and evidence, temperature 0.", "",
             "| Judge | Texts with both runs | Same flag decision | Same set of contradicted statements | "
             "Same set, among texts flagged in either run |", "|---|---:|---:|---:|---:|"]
    for model in JUDGE_MODELS:
        pairs = [(cache.get(model, 0, text), cache.get(model, 1, text)) for text in texts]
        pairs = [(first, second) for first, second in pairs if first is not None and second is not None]
        quotes = [({item["quote"] for item in first}, {item["quote"] for item in second}) for first, second in pairs]
        flagged = [(first, second) for first, second in quotes if first or second]
        lines.append(f"| {model} | {len(pairs)} | {sum(bool(a) == bool(b) for a, b in quotes)} | "
                     f"{sum(a == b for a, b in quotes)} | {sum(a == b for a, b in flagged)} of {len(flagged)} |")
    (OUT / "repeat-judge.md").write_text("\n".join(lines) + "\n")
    print("\n".join(lines))


if __name__ == "__main__":
    if sys.argv[1:] == ["compare"]:
        compare()
        raise SystemExit
    texts = repeat_texts()
    if len(sys.argv) == 3:
        shard, shards = int(sys.argv[1]), int(sys.argv[2])
        texts = [text for text in texts if int(hashlib.sha256(text.encode()).hexdigest(), 16) % shards == shard]
    judge_texts(texts, repeat=1)
