#!/usr/bin/env sh
set -eu

TARGET="${1:-postgres:5432}"
HOST="${TARGET%:*}"
PORT="${TARGET#*:}"
shift || true

until nc -z "$HOST" "$PORT"; do
  echo "Waiting for database at $HOST:$PORT..."
  sleep 1
done

exec "$@"

