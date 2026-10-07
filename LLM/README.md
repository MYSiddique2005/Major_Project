# IntelliERP assistant: evaluation (Phase 8)

The application's LLM code lives in the backend (`Backend/app/llm`, `Backend/app/knowledge`,
`Backend/app/services/ai_service.py`), because it runs inside the backend's services, permissions and
database session. This folder holds what is separate from the running application: the experiments
that measure how well the assistant works.

## What is measured

| Research question | How it is tested |
|---|---|
| RQ1 Grounding | 7 questions about the company's own terms and rules, plus 3 cross-module questions, each asked with the knowledge base and without it |
| RQ1 Factual retrieval | 5 questions with one correct figure from one module |
| RQ2 Cross-module reasoning | 5 questions whose answer needs sales, inventory and procurement together |
| RQ3 Proactive intelligence | The insights stored by the scheduled and manual scans, and the server's checks on them |
| RQ4 Controlled actions | 4 cases: a draft that should be created, a draft a role may not have, data a role may not see, and a request to place and approve an order |
| RQ5 Reliability | 3 questions the data cannot answer, and across every answer the figures that nothing supports |

The correct answers are not written down. Each case computes its expectation from the application's own
services when the evaluation runs (`evaluation/cases.py`), so the key cannot go stale as the data's dates
move. Scoring is automatic and uses no model as a judge (`evaluation/scoring.py`): facts are matched by
number (within 1%) or phrase, and a figure in an answer counts as unsupported when it appears in none of
the question, the tool results and the knowledge passages.

## Running it

```bash
cd LLM
../Backend/.venv/bin/python -m evaluation.run --name main      # asks whatever has not been asked yet
../Backend/.venv/bin/python -m evaluation.report --name main   # rebuilds the report from stored answers
../Backend/.venv/bin/python -m pytest evaluation -q            # tests of the scoring
```

It uses the model and database configured in `Backend/.env`. Answers are appended to
`evaluation/results/<name>/results.jsonl` as they arrive and are never asked twice, so a run stopped by
a rate limit continues where it left off; `--limit`, `--cases`, `--category` and `--conditions` select a
part. To compare models, set `LLM_PROVIDER` / `LLM_MODEL` and use a different `--name`. The action cases
create draft purchase orders and delete them again; every question also adds an `AI_QUERY` line to the
audit log of the database it runs on.

## Results

Two runs of 34 answers each were made on 6 October 2026, on Gemini's free tier (almost all on
`gemini-3.5-flash-lite`), on the Wide World Importers dataset.

| | Passed | Facts found | Unsupported figures |
|---|---:|---:|---:|
| **Run 1** (`results/main`): all 24 questions, with grounding | 23 (96%) | 96% | 0 of 119 |
| Run 1: 10 paired questions, with grounding | 10 of 10 | 100% | 0 of 72 |
| Run 1: the same 10, without grounding | 5 of 10 | 72% | 3 of 64 |
| **Run 2** (`results/rules-v2`): all 24 questions, with grounding | 24 (100%) | 100% | 1 of 100 |
| Run 2: 10 paired questions, with grounding | 10 of 10 | 100% | 0 of 60 |
| Run 2: the same 10, without grounding | 5 of 10 | 62% | 1 of 51 |

Run 2 was made later the same day, after three changes to the system: the assistant is told what the
user's role does not include (which fixed run 1's one failure), the stockout-risk and supplier-trend
rules were refined, and the analytics measure from the data's last day. The correct answers are
recomputed each run, so the two runs are scored against the rules in force at the time. The one
unsupported figure in run 2 is a difference the model worked out correctly from two tool figures
(328.4 - 246.8 = 81.6); the check counts any derived figure as unsupported.

Read these with their limits in mind:

- **Small.** 24 questions, asked once per run. Two runs agreeing is some evidence of consistency, but the
  system changed between them, so they are not repeats of one experiment. These are indications, not
  statistically reliable rates.
- **Written by the system's author.** The questions were written by whoever built the knowledge base and
  tools, so they favour what the system covers. Questions from real users would be harder.
- **Keyword scoring.** A correct answer worded unexpectedly is marked wrong, and a wrong answer that
  happens to contain the expected words is marked right. Two key entries were corrected after reading the
  answers; `results/main/notes.md` records them.
- **Two models.** The free tier's daily limits pushed most questions onto the smallest model.
- **Simulated supply data.** Purchase orders and stock levels are simulated (see `Data/README.md`).
- **The figure check is a lookup.** It cannot tell a derived figure from an invented one, or a real figure
  used in the wrong place.
