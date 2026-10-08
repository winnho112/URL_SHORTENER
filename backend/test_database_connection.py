"""
Database connection test script for the URL shortener.

Loads environment variables from backend/.env, connects to the database,
and confirms that the public.links table exists.
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

try:
    # Connect to the database
    conn = psycopg2.connect(database_url, connect_timeout=15)
    cur = conn.cursor()

    # Check that public.links exists in the database
    cur.execute(
        """
        SELECT EXISTS (
            SELECT 1
            FROM information_schema.tables
            WHERE table_schema = 'public'
              AND table_name   = 'links'
        );
        """
    )
    (exists,) = cur.fetchone()

    cur.close()
    conn.close()

    if exists:
        print("Database connection successful")
        print("Table found: public.links")
    else:
        print("Database connection successful")
        print("ERROR: Table public.links was NOT found")
        sys.exit(1)

except Exception as e:
    # Print the error type and message, but never the connection URL
    print(f"ERROR: {type(e).__name__}: {e}")
    sys.exit(1)