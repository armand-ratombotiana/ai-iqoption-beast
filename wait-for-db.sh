#!/bin/bash
# wait-for-db.sh - Wait for PostgreSQL/TimescaleDB to be ready

set -e

host="$1"
shift
cmd="$@"

echo "⏳ Waiting for TimescaleDB at $host to be ready..."

until PGPASSWORD=$POSTGRES_PASSWORD psql -h "$host" -U "$POSTGRES_USER" -d "$POSTGRES_DB" -c '\q' 2>/dev/null; do
  >&2 echo "🔄 TimescaleDB is unavailable - sleeping"
  sleep 2
done

>&2 echo "✅ TimescaleDB is up - initializing schema"

# Initialize AI schema
PGPASSWORD=$POSTGRES_PASSWORD psql -h "$host" -U "$POSTGRES_USER" -d "$POSTGRES_DB" -f /app/app/KAEL/KAEL/database/init_ai_schema.sql

>&2 echo "✅ Schema initialized - executing command"
exec $cmd
