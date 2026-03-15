#!/bin/bash
# Creates the umami database if it doesn't already exist.
# Mounted as a Postgres docker-entrypoint-initdb.d script.
set -e

psql -v ON_ERROR_STOP=1 --username "$POSTGRES_USER" --dbname "$POSTGRES_DB" <<-EOSQL
    SELECT 'CREATE DATABASE umami'
    WHERE NOT EXISTS (SELECT FROM pg_database WHERE datname = 'umami')\gexec
    GRANT ALL PRIVILEGES ON DATABASE umami TO $POSTGRES_USER;
EOSQL
