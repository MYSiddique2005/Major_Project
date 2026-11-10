#!/usr/bin/env bash
# One Gemma judge job in its own loop, so the held-out sets and the natural answers are judged in parallel
# (the free API is slow per request, not limited by request rate). Resumable; the main gemma lane skips
# whatever these have judged.
#   setsid nohup bash evaluation/run_gemma_parallel.sh heldout-gemma > evaluation/results/trace/lane-gemma-b.log 2>&1 &
#   setsid nohup bash evaluation/run_gemma_parallel.sh natural       > evaluation/results/trace/lane-gemma-c.log 2>&1 &
cd "$(dirname "$0")/.." || exit 1
export PYTHONWARNINGS=ignore LLM_FALLBACK_MODEL= LLM_MODEL=gemma-4-31b-it
case $1 in
  natural) cmd=(-m evaluation.trace_natural judge --scope sampled) ;;
  *)       cmd=(-m evaluation.trace_baselines judge --set "$1") ;;
esac
for round in $(seq 1 60); do
  output=$(../Backend/.venv/bin/python "${cmd[@]}" 2>&1 | grep -v -i "warning\|AFC")
  echo "$output" | tail -n 2
  echo "$output" | grep -q "^0 texts to judge" && { echo "$(date '+%d %b %H:%M') $1: done"; exit 0; }
  echo "$(date '+%d %b %H:%M') $1: not finished (try $round)"
  sleep 300
done
