#!/bin/bash
set -e

echo "Creating ARS database and users..."

# Create the main database
psql -v ON_ERROR_STOP=1 --username "$POSTGRES_USER" --dbname "$POSTGRES_DB" <<-EOSQL
    CREATE USER ars_user WITH PASSWORD 'ars_password';
    CREATE DATABASE ars_db OWNER ars_user;
    GRANT ALL PRIVILEGES ON DATABASE ars_db TO ars_user;
EOSQL

echo "ARS database initialized successfully!"