#!/usr/bin/env bash
# False-premise questions on Gemma with the verifier off, with patterns and with TRACE; resumable.
#   setsid nohup bash evaluation/run_fpq_gemma.sh > evaluation/results/fpq-gemma.log 2>&1 &
cd "$(dirname "$0")/.." || exit 1
export PYTHONWARNINGS=ignore LLM_MODEL=gemma-4-31b-it LLM_FALLBACK_MODEL=
for verifier in off patterns trace; do
  for round in $(seq 1 12); do
    LLM_VERIFIER=$verifier ../Backend/.venv/bin/python -m evaluation.run --suite fpq --name fpq-gemma-$verifier \
      --conditions grounded --retries 3 --retry-wait 120 2>&1 | grep -v -i "warning\|AFC" | tail -n 1
    n=$(wc -l < evaluation/results/fpq-gemma-$verifier/results.jsonl 2>/dev/null || echo 0)
    echo "$(date '+%d %b %H:%M') fpq-gemma-$verifier: $n of 44"
    [ "$n" -ge 44 ] && break
    sleep 1800
  done
done
echo "$(date '+%d %b %H:%M') finished"
