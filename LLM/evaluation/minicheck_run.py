"""MiniCheck (Tang, Laban and Durrett, EMNLP 2024): a small trained fact-checker, run locally on the CPU.

    ~/.venvs/minicheck/bin/python evaluation/minicheck_run.py [--limit N]

Reads results/trace/minicheck-input.jsonl (written by trace_baselines minicheck-prep: a fact sheet and the
sentences to check), writes results/trace/minicheck.jsonl with each sentence's support probability. Needs only
torch and transformers, so it runs in its own environment, apart from the backend.

As in the MiniCheck paper: the document is split into chunks of about CHUNK_WORDS words, each (chunk, sentence)
pair is scored, and the sentence's support is the highest over the chunks. The model reads
"premise: <chunk> hypothesis: <sentence>" and answers 1 (supported) or 0; support is the probability of 1.
Resumable: texts already scored are skipped.
"""
import argparse
import json
import time
from pathlib import Path

import torch
from transformers import AutoModelForSeq2SeqLM, AutoTokenizer

MODEL = "lytang/MiniCheck-Flan-T5-Large"
CHUNK_WORDS = 400
MAX_TOKENS = 1024
OUT = Path(__file__).resolve().parent / "results" / "trace"


def chunks(document: str) -> list[str]:
    """Pieces of about CHUNK_WORDS words, cut between lines so no fact is split."""
    pieces, current, count = [], [], 0
    for line in document.splitlines():
        words = len(line.split())
        if current and count + words > CHUNK_WORDS:
            pieces.append("\n".join(current))
            current, count = [], 0
        current.append(line)
        count += words
    if current:
        pieces.append("\n".join(current))
    return pieces or [""]


class MiniCheck:
    def __init__(self):
        self.tokenizer = AutoTokenizer.from_pretrained(MODEL)
        self.model = AutoModelForSeq2SeqLM.from_pretrained(MODEL).eval()
        self.one = self.tokenizer("1", add_special_tokens=False).input_ids[-1]
        self.zero = self.tokenizer("0", add_special_tokens=False).input_ids[-1]

    @torch.inference_mode()
    def support(self, pieces: list[str], claims: list[str], batch: int = 8) -> list[float]:
        pairs = [(index, f"premise: {piece} hypothesis: {claim}") for index, claim in enumerate(claims) for piece in pieces]
        best = [0.0] * len(claims)
        for start in range(0, len(pairs), batch):
            group = pairs[start:start + batch]
            encoded = self.tokenizer([text for _, text in group], return_tensors="pt", padding=True, truncation=True,
                                     max_length=MAX_TOKENS)
            start_token = torch.full((len(group), 1), self.model.config.decoder_start_token_id)
            logits = self.model(**encoded, decoder_input_ids=start_token).logits[:, 0, :]
            probabilities = torch.softmax(logits[:, [self.zero, self.one]], dim=-1)[:, 1].tolist()
            for (index, _), probability in zip(group, probabilities):
                best[index] = max(best[index], probability)
        return best


def main() -> None:
    parser = argparse.ArgumentParser(description="Score sentences with MiniCheck on the CPU.")
    parser.add_argument("--limit", type=int, default=0)
    args = parser.parse_args()
    cache_path = OUT / "minicheck.jsonl"
    done = {json.loads(line)["key"] for line in cache_path.read_text().splitlines()} if cache_path.exists() else set()
    todo = [record for record in map(json.loads, (OUT / "minicheck-input.jsonl").read_text().splitlines())
            if record["key"] not in done]
    if args.limit:
        todo = todo[:args.limit]
    print(f"{len(todo)} texts to score with {MODEL}", flush=True)
    checker = MiniCheck()
    with cache_path.open("a") as handle:
        for number, record in enumerate(todo, 1):
            started = time.monotonic()
            scores = checker.support(chunks(record["document"]), record["claims"]) if record["claims"] else []
            handle.write(json.dumps({"key": record["key"], "model": MODEL, "seconds": round(time.monotonic() - started, 2),
                                     "scores": [{"claim": claim, "support": round(score, 4)}
                                                for claim, score in zip(record["claims"], scores)]}) + "\n")
            handle.flush()
            if number % 10 == 0:
                print(f"  {number} of {len(todo)}", flush=True)


if __name__ == "__main__":
    main()
