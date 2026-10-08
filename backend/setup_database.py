"""
Database setup script for the URL shortener.

Loads environment variables from backend/.env, reads the SQL setup file,
and executes it against the Supabase Postgres database.
"""

import os
import sys

import psycopg2
from dotenv import load_dotenv

# Load .env from the same directory as this script
script_dir = os.path.dirname(os.path.abspath(__file__))
load_dotenv(os.path.join(script_dir, ".env"))

database_url = os.environ.get("DATABASE_URL")
if not database_url:
    print("ERROR: DATABASE_URL is not set in backend/.env")
    sys.exit(1)

# Read the SQL setup file
sql_path = os.path.join(script_dir, "sql", "setup.sql")
with open(sql_path, "r") as f:
    sql = f.read()

try:
    # Connect and execute the SQL
    conn = psycopg2.connect(database_url, connect_timeout=15)
    conn.autocommit = True
    cur = conn.cursor()
    cur.execute(sql)
    cur.close()
    conn.close()
    print("Database initialization completed successfully")
except Exception as e:
    # Print the error type and message, but never the connection URL
    print(f"ERROR: {type(e).__name__}: {e}")
    sys.exit(1)