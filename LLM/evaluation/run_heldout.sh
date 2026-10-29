#!/usr/bin/env bash
# Runs the held-out pipeline to the end, waiting out the free-tier daily limit. Every step resumes where it
# stopped, so this can be started again at any time. Start it detached so it survives the terminal:
#   setsid nohup bash evaluation/run_heldout.sh > evaluation/results/trace/pipeline.log 2>&1 &
cd "$(dirname "$0")/.." || exit 1
export PYTHONWARNINGS=ignore LLM_FALLBACK_MODEL=
PY=../Backend/.venv/bin/python

# Runs a step until it reports nothing left to do: an hour between tries after the daily limit, five minutes
# after any other failure, at most 40 tries.
step() {  # name, pattern of the "nothing left" line, command...
  local name=$1 none=$2; shift 2
  for round in $(seq 1 40); do
    output=$("$@" 2>&1 | grep -v -i "warning\|AFC\|frozen site")
    echo "$output" | grep -v RESOURCE_EXHAUSTED | tail -2
    if echo "$output" | grep -q "$none"; then echo "$(date '+%d %b %H:%M') $name: done"; return 0; fi
    if echo "$output" | grep -q -i "daily limit\|RESOURCE_EXHAUSTED"; then wait=3600; else wait=300; fi
    echo "$(date '+%d %b %H:%M') $name: not finished (try $round), next try in $((wait / 60)) min"
    sleep $wait
  done
}

LLM_MODEL=gemma-4-31b-it step "Gemma rewrites" "^0 texts to rewrite" \
  $PY -m evaluation.trace_testset perturb --writer gemma
LLM_MODEL=gemini-3.5-flash-lite step "TRACE extraction" ", 0 to extract" \
  $PY -m evaluation.trace_score extract
before=$(wc -l < evaluation/results/trace/minicheck-input.jsonl)
for set in heldout-gemini heldout-gemma; do
  for model in gemini-3.5-flash-lite gemma-4-31b-it; do
    LLM_MODEL=$model step "judge $model on $set" "^0 texts to judge" \
      $PY -m evaluation.trace_baselines judge --set $set
  done
  $PY -m evaluation.trace_baselines minicheck-prep --set $set 2>&1 | tail -1
done
added=$(( $(wc -l < evaluation/results/trace/minicheck-input.jsonl) - before ))
minicheck() { ~/.venvs/minicheck/bin/python evaluation/minicheck_run.py "$@" 2>&1 | grep -v -i "warn\|Loading weights" | tail -2; }
[ "$added" -gt 0 ] && minicheck --newest-first --limit "$added"  # the held-out texts first
$PY -m evaluation.trace_score report 2>&1 | grep -v -i "warning\|frozen site" | tail -3
echo "$(date '+%d %b %H:%M') held-out report written"

# False-premise questions on Gemini, all three settings (Gemma runs separately)
for verifier in off patterns trace; do
  for round in $(seq 1 12); do
    LLM_MODEL=gemini-3.5-flash-lite LLM_VERIFIER=$verifier $PY -m evaluation.run --suite fpq --name fpq-gemini-$verifier \
      --conditions grounded --retries 3 --retry-wait 120 2>&1 | grep -v -i "warning\|AFC" | tail -1
    [ "$(wc -l < evaluation/results/fpq-gemini-$verifier/results.jsonl 2>/dev/null || echo 0)" -ge 44 ] && break
    sleep 3600
  done
done
minicheck  # the natural-error texts (about 15 hours on the CPU)
echo "$(date '+%d %b %H:%M') pipeline finished"
