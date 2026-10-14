"""Start the API with host/port from .env: `python run.py` (auto-reload enabled for development)."""
import uvicorn

from app.core.config import settings

if __name__ == "__main__":
    uvicorn.run(
        "app.main:app",
        host=settings.backend_host,
        port=settings.backend_port,
        reload=settings.app_env.lower() != "production",
    )
