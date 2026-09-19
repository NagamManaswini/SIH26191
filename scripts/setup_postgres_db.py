"""PostgreSQL Database setup and initialization script for SIH Disaster Management."""

import sys
import os
import psycopg2
from psycopg2.extensions import ISOLATION_LEVEL_AUTOCOMMIT

sys.path.insert(0, os.path.abspath("."))

def setup_database():
    host = "localhost"
    port = 5432
    user = "postgres"
    password = "sql123"
    dbname = "sih_disaster"

    print(f"Connecting to PostgreSQL server at {host}:{port} as user '{user}'...")
    conn = psycopg2.connect(
        host=host,
        port=port,
        user=user,
        password=password,
        database="postgres"
    )
    conn.set_isolation_level(ISOLATION_LEVEL_AUTOCOMMIT)
    cur = conn.cursor()

    cur.execute("SELECT 1 FROM pg_database WHERE datname = %s", (dbname,))
    exists = cur.fetchone()
    if not exists:
        print(f"Creating database '{dbname}'...")
        cur.execute(f'CREATE DATABASE "{dbname}"')
        print(f"Database '{dbname}' created successfully.")
    else:
        print(f"Database '{dbname}' already exists.")

    cur.close()
    conn.close()

if __name__ == "__main__":
    setup_database()
