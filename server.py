"""ASGI entrypoint bridge for Render and deployment environments.

Allows Render's default start command:
    uvicorn server:app --host 0.0.0.0 --port $PORT
to work seamlessly without configuration errors.
"""

from __future__ import annotations

import os

from app.main import app

__all__ = ["app"]

if __name__ == "__main__":
    import uvicorn

    port = int(os.environ.get("PORT", 8000))
    uvicorn.run("server:app", host="0.0.0.0", port=port)
