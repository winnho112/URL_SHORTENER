import sys
from pathlib import Path
import importlib.util

backend_dir = Path(__file__).resolve().parent.parent / "backend"

# Remove any cached "api" modules (the root api/ package loaded by Vercel)
# so that we can register backend/api/ as the real "api" package.
for key in list(sys.modules):
    if key == "api" or key.startswith("api."):
        del sys.modules[key]

# Register backend/api/ as the "api" Python package so that
# backend/api/index.py can use relative imports (.auth, .links)
api_spec = importlib.util.spec_from_file_location(
    "api",
    backend_dir / "api" / "__init__.py",
    submodule_search_locations=[str(backend_dir / "api")],
)
api_pkg = importlib.util.module_from_spec(api_spec)
sys.modules["api"] = api_pkg
api_spec.loader.exec_module(api_pkg)

# Import the FastAPI app from the backend's api/index.py
from api.index import app  # noqa: E402, F401