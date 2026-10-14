#!/usr/bin/env bash
# Keeps asking Gemini for the claim-test rewrites until all are collected. When the free models are
# overloaded each attempt stops early; five texts go in one request (both rewrites); this waits 10 minutes and tries again, cycling through the
# models. Answers already collected are never asked twice.
#
#   ./run_claims_rewrites.sh                  # 60 texts = 120 rewrites
#   CLAIMS_TEXTS=30 ./run_claims_rewrites.sh  # a smaller test
cd "$(dirname "$0")"
export PYTHONWARNINGS=ignore
file=evaluation/results/claims/perturbations.jsonl
texts=${CLAIMS_TEXTS:-60}
target=$((texts * 2))
count() { wc -l < "$file" 2>/dev/null || echo 0; }
while [ "$(count)" -lt "$target" ]; do
  for model in gemini-3.5-flash gemini-3.5-flash-lite gemini-3.8-flash; do
    LLM_MODEL=$model ../Backend/.venv/bin/python -m evaluation.claims_eval perturb-batched --limit "$texts" 2>&1 \
      | grep -v "RuntimeWarning\|AFC"
    [ "$(count)" -ge "$target" ] && break 2
  done
  echo "$(date +%T): $(count) of $target collected; waiting 10 minutes"
  sleep 600
done
echo "All $target rewrites collected."
