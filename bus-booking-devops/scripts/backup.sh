#!/usr/bin/env sh
set -eu
mkdir -p backups
STAMP="$(date -u +%Y%m%dT%H%M%SZ)"
docker compose exec -T db pg_dump -U busapp -d busbooking -Fc > "backups/busbooking-${STAMP}.dump"
echo "Backup created: backups/busbooking-${STAMP}.dump"
