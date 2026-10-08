"""
Authentication routes for the URL shortener.

Handles signup, login, and token verification by communicating
with Supabase Auth via its REST API.
"""

import os

import httpx
from fastapi import APIRouter, HTTPException, Header
from pydantic import BaseModel

# Supabase credentials from environment
SUPABASE_URL = os.environ.get("SUPABASE_URL", "")
SUPABASE_KEY = os.environ.get("SUPABASE_PUBLISHABLE_KEY", "")

router = APIRouter(prefix="/api/auth", tags=["auth"])


# ----- Request models -----

class SignupRequest(BaseModel):
    email: str
    password: str
    full_name: str


class LoginRequest(BaseModel):
    email: str
    password: str


# ----- Helper: verify an access token with Supabase -----

def get_current_user(authorization: str) -> dict:
    """
    Verify an access token with Supabase Auth.
    Returns the user dict on success, raises HTTPException 401 on failure.
    """
    # Expect "Bearer <token>" header
    if not authorization.startswith("Bearer "):
        raise HTTPException(status_code=401, detail="Invalid authorization header")

    token = authorization.removeprefix("Bearer ")

    resp = httpx.get(
        f"{SUPABASE_URL}/auth/v1/user",
        headers={
            "apikey": SUPABASE_KEY,
            "Authorization": f"Bearer {token}",
        },
        timeout=10,
    )

    if resp.status_code != 200:
        raise HTTPException(status_code=401, detail="Invalid or expired token")

    return resp.json()


# ----- POST /api/auth/signup -----

@router.post("/signup")
def signup(req: SignupRequest):
    """Create a new user account via Supabase Auth."""
    resp = httpx.post(
        f"{SUPABASE_URL}/auth/v1/signup",
        headers={
            "apikey": SUPABASE_KEY,
            "Content-Type": "application/json",
        },
        json={
            "email": req.email,
            "password": req.password,
            "data": {"full_name": req.full_name},
        },
        timeout=10,
    )

    if resp.status_code != 200:
        # Supabase returns error details in the JSON body
        error = resp.json()
        message = error.get("msg", error.get("message", "Signup failed"))
        raise HTTPException(status_code=400, detail=message)

    data = resp.json()
    return {
        "message": "Signup successful",
        "user": {
            "id": data.get("id"),
            "email": data.get("email"),
        },
    }


# ----- POST /api/auth/login -----

@router.post("/login")
def login(req: LoginRequest):
    """Log in an existing user and return tokens."""
    resp = httpx.post(
        f"{SUPABASE_URL}/auth/v1/token?grant_type=password",
        headers={
            "apikey": SUPABASE_KEY,
            "Content-Type": "application/json",
        },
        json={
            "email": req.email,
            "password": req.password,
        },
        timeout=10,
    )

    if resp.status_code != 200:
        error = resp.json()
        message = error.get("error_description", error.get("msg", "Login failed"))
        raise HTTPException(status_code=401, detail=message)

    data = resp.json()
    return {
        "access_token": data["access_token"],
        "refresh_token": data["refresh_token"],
        "expires_in": data["expires_in"],
        "token_type": data["token_type"],
        "user": data.get("user"),
    }