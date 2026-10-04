#!/usr/bin/env bash
# Project-owned PostgreSQL instance for local development. Needs no sudo: it runs as
# your user, keeps its data in Backend/.pgdata and listens only on localhost:5434.
#
#   scripts/dev_db.sh start    create it on first use, then start it
#   scripts/dev_db.sh stop
#   scripts/dev_db.sh status
#
# It does not start automatically after a reboot: run "start" before the backend.
# The role/password/database are intellierp/intellierp/intellierp (development only).
set -euo pipefail

BACKEND_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
DATA_DIR="$BACKEND_DIR/.pgdata"
PORT=5434
DB_USER=intellierp
DB_NAME=intellierp

PG_BIN="$(ls -d /usr/lib/postgresql/*/bin 2>/dev/null | sort -V | tail -1 || true)"
if [[ -z "$PG_BIN" || ! -x "$PG_BIN/initdb" ]]; then
  echo "PostgreSQL server binaries not found under /usr/lib/postgresql." >&2
  exit 1
fi

running() { "$PG_BIN/pg_ctl" -D "$DATA_DIR" status >/dev/null 2>&1; }

case "${1:-}" in
  start)
    if [[ ! -f "$DATA_DIR/PG_VERSION" ]]; then
      password_file="$(mktemp)"
      echo "$DB_USER" > "$password_file"   # development password, same as the role name
      "$PG_BIN/initdb" -D "$DATA_DIR" -U "$DB_USER" --pwfile="$password_file" \
        --auth-local=scram-sha-256 --auth-host=scram-sha-256 -E UTF8 >/dev/null
      rm -f "$password_file"
      echo "Created database cluster in $DATA_DIR"
    fi
    if running; then
      echo "Already running on port $PORT"
    else
      "$PG_BIN/pg_ctl" -D "$DATA_DIR" -l "$DATA_DIR/server.log" -w \
        -o "-p $PORT -c listen_addresses=localhost -c unix_socket_directories=''" start >/dev/null
      echo "Started on localhost:$PORT"
    fi
    if ! PGPASSWORD="$DB_USER" "$PG_BIN/psql" -h localhost -p "$PORT" -U "$DB_USER" -d postgres -Atc \
        "SELECT 1 FROM pg_database WHERE datname = '$DB_NAME'" | grep -q 1; then
      PGPASSWORD="$DB_USER" "$PG_BIN/createdb" -h localhost -p "$PORT" -U "$DB_USER" "$DB_NAME"
      echo "Created database $DB_NAME"
    fi
    ;;
  stop)
    if running; then "$PG_BIN/pg_ctl" -D "$DATA_DIR" -m fast -w stop >/dev/null && echo "Stopped"; else echo "Not running"; fi
    ;;
  status)
    if running; then echo "Running on localhost:$PORT (data in $DATA_DIR)"; else echo "Not running"; fi
    ;;
  *)
    echo "Usage: $0 {start|stop|status}" >&2
    exit 2
    ;;
esac
