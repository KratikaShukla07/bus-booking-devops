#!/usr/bin/env sh
set -eu
if [ "$#" -ne 1 ] || [ ! -f "$1" ]; then
  echo "Usage: ./scripts/restore.sh backups/file.dump" >&2
  exit 1
fi
echo "WARNING: this replaces current database contents."
docker compose exec -T db pg_restore -U busapp -d busbooking --clean --if-exists < "$1"
echo "Restore completed. Verify with: curl http://localhost:8080/health/ready"
