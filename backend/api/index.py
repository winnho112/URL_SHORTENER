import os

from dotenv import load_dotenv
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

# Load environment variables from backend/.env
load_dotenv(os.path.join(os.path.dirname(__file__), "..", ".env"))

from api.auth import router as auth_router  # noqa: E402

# Create the FastAPI application instance
app = FastAPI(title="URL Shortener API")

# Allow the React dev server and Vercel preview deployments
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:5173",
        "https://localhost:5173",
    ],
    allow_origin_regex=r"https://.*\.vercel\.app$",
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include auth routes
app.include_router(auth_router)


@app.get("/api/health")
def health_check():
    """Simple health check endpoint to confirm the API is running."""
    return {"status": "ok"}