#!/usr/bin/env bash
# The remaining evaluation runs, in three lanes that use separate resources: Gemini quota, Gemma quota and the
# CPU (MiniCheck). Every step resumes where it stopped, so this can be started again at any time:
#   setsid nohup bash evaluation/run_remaining.sh gemini   > evaluation/results/trace/lane-gemini.log 2>&1 &
#   setsid nohup bash evaluation/run_remaining.sh gemma    > evaluation/results/trace/lane-gemma.log 2>&1 &
#   setsid nohup bash evaluation/run_remaining.sh minicheck > evaluation/results/trace/lane-minicheck.log 2>&1 &
cd "$(dirname "$0")/.." || exit 1
export PYTHONWARNINGS=ignore LLM_FALLBACK_MODEL=
PY=../Backend/.venv/bin/python

# Runs a step until it reports nothing left to do: an hour between tries after the daily limit, five minutes
# after any other failure, at most 40 tries.
step() {  # name, pattern of the "nothing left" line, command...
  local name=$1 none=$2; shift 2
  for round in $(seq 1 40); do
    output=$("$@" 2>&1 | grep -v -i "warning\|AFC\|frozen site")
    echo "$output" | grep -v RESOURCE_EXHAUSTED | tail -n 2
    if echo "$output" | grep -q "$none"; then echo "$(date '+%d %b %H:%M') $name: done"; return 0; fi
    if echo "$output" | grep -q -i "daily limit\|RESOURCE_EXHAUSTED"; then wait=3600; else wait=300; fi
    echo "$(date '+%d %b %H:%M') $name: not finished (try $round), next try in $((wait / 60)) min"
    sleep $wait
  done
}

fpq() {  # model, name, verifier: the 44 false-premise questions
  for round in $(seq 1 24); do
    LLM_MODEL=$1 LLM_VERIFIER=$3 $PY -m evaluation.run --suite fpq --name "$2" --conditions grounded --retries 3 \
      --retry-wait 120 2>&1 | grep -v -i "warning\|AFC" | tail -n 1
    n=$(wc -l < "evaluation/results/$2/results.jsonl" 2>/dev/null || echo 0)
    echo "$(date '+%d %b %H:%M') $2: $n of 44"
    [ "$n" -ge 44 ] && return 0
    sleep 1800
  done
}

case $1 in
  gemini)
    export LLM_MODEL=gemini-3.5-flash-lite
    step "judge gemini on heldout-gemma" "^0 texts to judge" $PY -m evaluation.trace_baselines judge --set heldout-gemma
    for verifier in off patterns trace; do fpq gemini-3.5-flash-lite fpq-gemini-$verifier $verifier; done
    step "natural extraction" ", 0 to extract" $PY -m evaluation.trace_natural extract --scope sampled
    step "natural judge gemini" "^0 texts to judge" $PY -m evaluation.trace_natural judge --scope sampled
    ;;
  gemma)
    export LLM_MODEL=gemma-4-31b-it
    for set in heldout-gemini heldout-gemma; do
      step "judge gemma on $set" "^0 texts to judge" $PY -m evaluation.trace_baselines judge --set $set
    done
    fpq gemma-4-31b-it fpq-gemma-trace trace
    step "natural judge gemma" "^0 texts to judge" $PY -m evaluation.trace_natural judge --scope sampled
    ;;
  minicheck)
    for keys in heldout natural; do
      ~/.venvs/minicheck/bin/python evaluation/minicheck_run.py --keys evaluation/results/trace/minicheck-keys-$keys.txt \
        2>&1 | grep -v -i "warn\|Loading weights" | tail -n 2
      echo "$(date '+%d %b %H:%M') minicheck $keys: done"
    done
    ;;
esac
echo "$(date '+%d %b %H:%M') lane $1 finished"
