"""Judge one shard of the texts still to judge, so several workers can share a slow, overloaded API.

Each worker takes the texts whose hash falls in its shard, so no two workers ask about the same text, even when
they restart at different times. Results
go to the same judge cache as trace_baselines and trace_natural (appending one line per text), and whatever a
worker skips is picked up by the next run.

    LLM_MODEL=gemma-4-31b-it ../Backend/.venv/bin/python -m evaluation.judge_shard heldout-gemma 0 4
    LLM_MODEL=gemma-4-31b-it ../Backend/.venv/bin/python -m evaluation.judge_shard natural 1 4
"""
import hashlib
import json
import sys

from evaluation.trace_baselines import OUT, JudgeCache, judge_texts


def texts_of(name: str) -> list[str]:
    if name == "natural":
        from evaluation import trace_natural

        sampled = {json.loads(line)["answer_id"] for line in (trace_natural.OUT / "sample.jsonl").read_text().splitlines()}
        return [item["text"] for item in trace_natural.answers() if item["id"] in sampled]
    records = [json.loads(line) for line in (OUT / f"{name}.jsonl").read_text().splitlines()]
    return [text for record in records for text in (record.get("original"), record.get("rewritten")) if text]


def main() -> None:
    name, shard, shards = sys.argv[1], int(sys.argv[2]), int(sys.argv[3])
    from app.core.config import get_settings

    model, cache = get_settings().llm_model, JudgeCache()
    mine = [text for text in dict.fromkeys(texts_of(name))
            if int(hashlib.sha256(text.encode()).hexdigest(), 16) % shards == shard]
    judge_texts([text for text in mine if cache.get(model, 0, text) is None])


if __name__ == "__main__":
    main()
