"""Baselines for TRACE: other ways to check an assistant's statements, on the same texts.

    LLM_MODEL=gemini-3.5-flash-lite ../Backend/.venv/bin/python -m evaluation.trace_baselines judge --set heldout-gemini
    LLM_MODEL=gemma-4-31b-it        ../Backend/.venv/bin/python -m evaluation.trace_baselines judge --set heldout-gemini

LLM judge: the model is given the same evidence TRACE checks against (the overview of every product and
supplier the text names, as the assistant's tools return it, and the knowledge base's rule, workflow and
role passages) and lists every statement the evidence contradicts. This is how LLM-as-judge factuality
checking is usually done (e.g. RAGAs faithfulness). Replies are cached by model, prompt version, repeat
number and text, so repeats measure how stable the verdicts are.
"""
import argparse
import hashlib
import json
import re
import time
from pathlib import Path

from evaluation.claims_eval import RESULTS
from evaluation.context import open_context

from app.knowledge.content import get_knowledge_base
from app.llm.recommendations import RecommendationChecker

OUT = RESULTS / "trace"
JUDGE_CACHE = OUT / "judge.jsonl"
JUDGE_VERSION = "judge-1"
MAX_PRODUCTS = 8

JUDGE_PROMPT = """\
You check a text written by the AI assistant of an ERP system against the system's data and the company's \
rules, given below as evidence. List every statement in the text that the evidence CONTRADICTS. Do not list \
statements the evidence supports, statements it does not mention, advice, or questions. Copy each \
contradicted statement exactly as it appears in the text.

Reply with JSON only: {{"contradicted": [{{"quote": "...", "reason": "what the evidence says instead"}}]}} \
(an empty list if nothing is contradicted).

<evidence>
{evidence}
</evidence>

<text>
{text}
</text>"""


def evidence_for(text: str, checker: RecommendationChecker, rules_text: str) -> str:
    """The facts a fair judge needs: every product and supplier the text names, and the company's rules."""
    parts = []
    for product_id in list(dict.fromkeys(re.findall(r"\bP\d{3}\b", text)))[:MAX_PRODUCTS]:
        try:
            parts.append(f"Product {product_id}: {json.dumps(checker.product_facts(product_id), default=str)}")
        except Exception:
            parts.append(f"Product {product_id}: not found in the system")
    for supplier_id in list(dict.fromkeys(re.findall(r"\bS\d{3}\b", text)))[:MAX_PRODUCTS]:
        try:
            parts.append(f"Supplier {supplier_id}: {json.dumps(checker.supplier_facts(supplier_id), default=str)}")
        except Exception:
            parts.append(f"Supplier {supplier_id}: not found in the system")
    for order_id in list(dict.fromkeys(re.findall(r"\bPO-\d+\b", text)))[:MAX_PRODUCTS]:
        parts.append(f"Purchase order {order_id}: see the product's procurement facts")
    parts.append(f"Company rules:\n{rules_text}")
    return "\n\n".join(parts)


def rules_passages() -> str:
    knowledge = get_knowledge_base()
    return "\n".join(f"- {entry.title}: {entry.text}" for entry in knowledge.entries
                     if entry.category in ("rule", "workflow", "access", "definition"))


class JudgeCache:
    def __init__(self, path: Path = JUDGE_CACHE):
        self.path, self.records = path, {}
        if path.exists():
            for line in path.read_text().splitlines():
                record = json.loads(line)
                self.records[record["key"]] = record

    @staticmethod
    def key(model: str, repeat: int, text: str) -> str:
        return hashlib.sha256(f"{JUDGE_VERSION}\n{model}\n{repeat}\n{text}".encode()).hexdigest()

    def get(self, model: str, repeat: int, text: str) -> list[dict] | None:
        record = self.records.get(self.key(model, repeat, text))
        return None if record is None else record["contradicted"]

    def put(self, model: str, repeat: int, text: str, contradicted: list[dict], used_model: str, seconds: float) -> None:
        record = {"key": self.key(model, repeat, text), "version": JUDGE_VERSION, "requested_model": model,
                  "model": used_model, "repeat": repeat, "seconds": seconds, "contradicted": contradicted}
        self.records[record["key"]] = record
        self.path.parent.mkdir(parents=True, exist_ok=True)
        with self.path.open("a") as handle:
            handle.write(json.dumps(record) + "\n")


def ask_judge(prompt: str) -> tuple[list[dict], str, float]:
    from evaluation.trace_testset import ask

    started = time.monotonic()
    reply = ask(prompt, temperature=0.0)  # as deterministic as the API allows; repeats measure the rest
    items = [item for item in reply.get("contradicted", []) if isinstance(item, dict) and item.get("quote")]
    return items, reply.get("model", ""), round(time.monotonic() - started, 1)


def judge_texts(texts: list[str], repeat: int = 0) -> None:
    from app.core.config import get_settings

    model = get_settings().llm_model
    cache = JudgeCache()
    todo = [text for text in dict.fromkeys(texts) if text and cache.get(model, repeat, text) is None]
    print(f"{len(todo)} texts to judge with {model} (repeat {repeat})", flush=True)
    with open_context() as ctx:
        checker = RecommendationChecker(ctx.analytics, ctx.suppliers)
        rules_text = rules_passages()
        for index, text in enumerate(todo, 1):
            items, used, seconds = ask_judge(JUDGE_PROMPT.format(evidence=evidence_for(text, checker, rules_text), text=text))
            cache.put(model, repeat, text, items, used, seconds)
            if index % 10 == 0:
                print(f"  {index} of {len(todo)}", flush=True)


def main() -> None:
    parser = argparse.ArgumentParser(description="Run a baseline checker on a rewrite set.")
    parser.add_argument("step", choices=["judge"])
    parser.add_argument("--set", required=True, help="a rewrite file in results/trace or results/claims, without .jsonl")
    parser.add_argument("--repeat", type=int, default=0)
    args = parser.parse_args()
    path = OUT / f"{args.set}.jsonl"
    if not path.exists():
        path = RESULTS / "claims" / f"{args.set}.jsonl"
    records = [json.loads(line) for line in path.read_text().splitlines()]
    texts = [text for record in records for text in (record.get("original"), record.get("rewritten"))]
    judge_texts(texts, args.repeat)


if __name__ == "__main__":
    main()
