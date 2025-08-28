#!/bin/bash
#SBATCH -J purpletrader-bots
#SBATCH -o purpletrader-bots.%j.out
#SBATCH -e purpletrader-bots.%j.err
#SBATCH -N 1
#SBATCH -n 1
#SBATCH -c 4
#SBATCH --time=04:00:00

set -euo pipefail

ENGINE_URL="http://localhost:8080"
PYTHON_BIN="python3"

# Live Trading Engine paths (adjust if different on your cluster)
ENGINE_WORKDIR="${ENGINE_WORKDIR:-$HOME/live-trading-engine}"
ENGINE_BIN="${ENGINE_BIN:-$ENGINE_WORKDIR/build/apps/trading_engine/trading_engine}"

cleanup() {
  echo "Cleaning up at $(date)"
  if [[ -n "${ENGINE_PID:-}" ]]; then
    kill "${ENGINE_PID}" 2>/dev/null || true
  fi
  # Stop any child bots
  pkill -P $$ 2>/dev/null || true
}
trap cleanup EXIT

wait_for_health() {
  local url="$1"
  local timeout="${2:-60}"
  local start_ts now
  start_ts=$(date +%s)
  echo "Waiting for engine health at ${url} (timeout ${timeout}s)"
  until curl -fsS "${url}" >/dev/null 2>&1; do
    sleep 1
    now=$(date +%s)
    if (( now - start_ts > timeout )); then
      echo "Engine health check timed out after ${timeout}s" >&2
      return 1
    fi
  done
  echo "Engine is healthy."
}

echo "Starting bots on $(hostname) at $(date)"

# Start engine if available
if [[ -x "${ENGINE_BIN}" ]]; then
  echo "Starting trading engine from ${ENGINE_BIN} (workdir ${ENGINE_WORKDIR})"
  (
    cd "${ENGINE_WORKDIR}" && \
    "${ENGINE_BIN}" > "trading_engine.${SLURM_JOB_ID:-$$}.log" 2>&1
  ) &
  ENGINE_PID=$!
  # Wait for engine to be ready
  wait_for_health "${ENGINE_URL}/health" 90 || {
    echo "Engine failed to become healthy; exiting" >&2
    exit 1
  }
else
  echo "WARNING: Engine binary not found at ${ENGINE_BIN}. Skipping engine startup." >&2
fi

${PYTHON_BIN} -m bots.runner --base-url "$ENGINE_URL" --config "$(dirname "$0")/bots.yaml" &

wait


