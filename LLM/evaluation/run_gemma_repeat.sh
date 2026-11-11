#!/usr/bin/env bash
# One worker of the Gemma judge's repeat run (repeatability), in a resumable loop.
#   setsid nohup bash evaluation/run_gemma_repeat.sh 0 4 > evaluation/results/trace/lane-gemma-repeat-0.log 2>&1 &
cd "$(dirname "$0")/.." || exit 1
export PYTHONWARNINGS=ignore LLM_FALLBACK_MODEL= LLM_MODEL=gemma-4-31b-it
for round in $(seq 1 60); do
  output=$(../Backend/.venv/bin/python -m evaluation.judge_repeat "$1" "$2" 2>&1 | grep -v -i "warning\|AFC")
  echo "$output" | tail -n 2
  echo "$output" | grep -q "^0 texts to judge" && { echo "$(date '+%d %b %H:%M') repeat shard $1/$2: done"; exit 0; }
  echo "$(date '+%d %b %H:%M') repeat shard $1/$2: not finished (try $round)"
  sleep 120
done
