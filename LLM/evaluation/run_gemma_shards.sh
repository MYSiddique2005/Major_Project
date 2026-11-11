#!/usr/bin/env bash
# One sharded Gemma judge worker in a resumable loop (see evaluation/judge_shard.py).
#   setsid nohup bash evaluation/run_gemma_shards.sh natural 0 4 > evaluation/results/trace/lane-shard-natural-0.log 2>&1 &
cd "$(dirname "$0")/.." || exit 1
export PYTHONWARNINGS=ignore LLM_FALLBACK_MODEL= LLM_MODEL=gemma-4-31b-it
for round in $(seq 1 60); do
  output=$(../Backend/.venv/bin/python -m evaluation.judge_shard "$1" "$2" "$3" 2>&1 | grep -v -i "warning\|AFC")
  echo "$output" | tail -n 2
  echo "$output" | grep -q "^0 texts to judge" && { echo "$(date '+%d %b %H:%M') $1 shard $2/$3: done"; exit 0; }
  echo "$(date '+%d %b %H:%M') $1 shard $2/$3: not finished (try $round)"
  sleep 120
done
