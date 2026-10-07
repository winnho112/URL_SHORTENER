from fastapi import FastAPI

# Create the FastAPI application instance
app = FastAPI(title="URL Shortener API")


@app.get("/api/health")
def health_check():
    """Simple health check endpoint to confirm the API is running."""
    return {"status": "ok"}