#!/usr/bin/env bash
# The 86 evaluation questions with TRACE as the verifier (harm check), on the model of runs fixed-1..3; resumable.
#   setsid nohup bash evaluation/run_trace_harm.sh > evaluation/results/trace/lane-harm.log 2>&1 &
cd "$(dirname "$0")/.." || exit 1
export PYTHONWARNINGS=ignore LLM_MODEL=gemini-3.5-flash-lite LLM_FALLBACK_MODEL= LLM_VERIFIER=trace
for round in $(seq 1 24); do
  ../Backend/.venv/bin/python -m evaluation.run --name trace-1 --conditions grounded --retries 3 --retry-wait 120 \
    2>&1 | grep -v -i "warning\|AFC" | tail -n 1
  n=$(wc -l < evaluation/results/trace-1/results.jsonl 2>/dev/null || echo 0)
  echo "$(date '+%d %b %H:%M') trace-1: $n of 86"
  [ "$n" -ge 86 ] && break
  sleep 1800
done
