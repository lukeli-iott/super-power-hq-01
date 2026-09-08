#!/usr/bin/env sh
# Regenerate heroes.db from source.
# Only needed if your SQLite driver can't open the supplied binary heroes.db.
#
# Usage:  sh build-db.sh

set -e

rm -f heroes.db
sqlite3 heroes.db < schema.sql
sqlite3 heroes.db < seed.sql

echo "Built heroes.db ($(sqlite3 heroes.db 'SELECT COUNT(*) FROM submissions;') rows)"
