#!/usr/bin/env bash
# Runs, or continues, the three repeated runs of the extended evaluation and rebuilds the summary.
#
#   ./run_extended.sh
#
# Every run is pinned to one model with no fallback, so all answers in the comparison come from the
# same model. Answers already collected are never asked again: when the free tier's limit stops a
# run, run this script again later (the next day for a daily limit) and it carries on from there.
#
#   EVAL_PREFIX=extended ./run_extended.sh                        # another set of runs (default: fixed)
#   EVAL_PREFIX=flash EVAL_MODEL=gemini-3.5-flash ./run_extended.sh
#   EVAL_PREFIX=gemma4 EVAL_MODEL=gemma-4-31b-it EVAL_RUNS=1 ./run_extended.sh   # a single run
set -uo pipefail
cd "$(dirname "$0")"

export PYTHONWARNINGS=ignore
export LLM_MODEL="${EVAL_MODEL:-gemini-3.5-flash-lite}"
export LLM_FALLBACK_MODEL=
prefix="${EVAL_PREFIX:-fixed}"
python=../Backend/.venv/bin/python
runs=$(seq -s, -f "$prefix-%g" 1 "${EVAL_RUNS:-3}")

for run in ${runs//,/ }; do
  "$python" -m evaluation.run --name "$run" --retries "${EVAL_RETRIES:-3}" --retry-wait 120
  status=$?
  if [ "$status" -ne 0 ]; then
    echo "$run is not finished (the model's limit was reached). Run this script again later to continue."
    break
  fi
done
"$python" -m evaluation.compare --names "$runs" --out "$prefix"
