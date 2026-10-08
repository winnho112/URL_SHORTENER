"""
Link routes for the URL shortener.

Handles creating short links, listing a user's links,
and redirecting short codes to their original URLs.
"""

import os
import random
import string
from datetime import datetime, timezone

import psycopg2
from fastapi import APIRouter, Depends, HTTPException, Request
from fastapi.responses import RedirectResponse
from pydantic import BaseModel

from api.auth import get_current_user

# How many times to retry on duplicate short_code
MAX_RETRIES = 5

router = APIRouter(tags=["links"])


# ----- Request model for creating a link -----

class CreateLinkRequest(BaseModel):
    original_url: str


# ----- Helper: get a database connection -----

def get_db():
    """Open a Postgres connection using DATABASE_URL from the environment."""
    database_url = os.environ.get("DATABASE_URL")
    if not database_url:
        raise HTTPException(status_code=500, detail="DATABASE_URL not configured")
    conn = psycopg2.connect(database_url, connect_timeout=15)
    try:
        yield conn
    finally:
        conn.close()


# ----- Helper: generate a random 6-character short code -----

def generate_short_code(length: int = 6) -> str:
    """Return a random alphanumeric string of the given length."""
    chars = string.ascii_letters + string.digits
    return "".join(random.choices(chars, k=length))


# ----- Helper: build the short_url for a given code -----

def build_short_url(request: Request, short_code: str) -> str:
    """
    Build the full short URL.
    Uses APP_BASE_URL from env if set; otherwise falls back to the
    incoming request's base URL.
    """
    base = os.environ.get("APP_BASE_URL", "").rstrip("/")
    if not base:
        base = str(request.base_url).rstrip("/")
    return f"{base}/api/r/{short_code}"


# ----- POST /api/links — create a new short link -----

@router.post("/api/links")
def create_link(
    req: CreateLinkRequest,
    request: Request,
    user: dict = Depends(get_current_user),
    conn=Depends(get_db),
):
    """Create a shortened URL for the logged-in user."""
    url = req.original_url.strip()

    # Validate the URL starts with http:// or https://
    if not (url.startswith("http://") or url.startswith("https://")):
        raise HTTPException(
            status_code=400,
            detail="URL must start with http:// or https://",
        )

    user_id = user.get("id")
    cur = conn.cursor()

    # Try inserting with a unique short_code, retrying on collision
    for attempt in range(MAX_RETRIES):
        short_code = generate_short_code()
        try:
            cur.execute(
                """
                INSERT INTO public.links (user_id, original_url, short_code)
                VALUES (%s, %s, %s)
                RETURNING id, original_url, short_code, click_count, created_at
                """,
                (user_id, url, short_code),
            )
            row = cur.fetchone()
            conn.commit()
            cur.close()

            return {
                "id": str(row[0]),
                "original_url": row[1],
                "short_code": row[2],
                "click_count": row[3],
                "created_at": row[4].isoformat(),
                "short_url": build_short_url(request, row[2]),
            }
        except psycopg2.errors.UniqueViolation:
            # Rare collision — rollback and retry with a new code
            conn.rollback()
            continue

    cur.close()
    raise HTTPException(
        status_code=500,
        detail="Could not generate a unique short code. Please try again.",
    )


# ----- GET /api/links — list the current user's links -----

@router.get("/api/links")
def list_links(
    request: Request,
    user: dict = Depends(get_current_user),
    conn=Depends(get_db),
):
    """Return all links belonging to the logged-in user."""
    user_id = user.get("id")
    cur = conn.cursor()
    cur.execute(
        """
        SELECT id, original_url, short_code, click_count, created_at
        FROM public.links
        WHERE user_id = %s
        ORDER BY created_at DESC
        """,
        (user_id,),
    )
    rows = cur.fetchall()
    cur.close()

    links = []
    for row in rows:
        links.append({
            "id": str(row[0]),
            "original_url": row[1],
            "short_code": row[2],
            "click_count": row[3],
            "created_at": row[4].isoformat(),
            "short_url": build_short_url(request, row[2]),
        })

    return {"links": links}


# ----- GET /api/r/{short_code} — public redirect -----

@router.get("/api/r/{short_code}")
def redirect_link(short_code: str, conn=Depends(get_db)):
    """Look up a short code, track the click, and redirect."""
    cur = conn.cursor()
    cur.execute(
        """
        UPDATE public.links
        SET click_count = click_count + 1,
            last_clicked_at = %s
        WHERE short_code = %s
        RETURNING original_url
        """,
        (datetime.now(timezone.utc), short_code),
    )
    row = cur.fetchone()
    conn.commit()
    cur.close()

    if not row:
        raise HTTPException(status_code=404, detail="Link not found")

    return RedirectResponse(url=row[0], status_code=302)