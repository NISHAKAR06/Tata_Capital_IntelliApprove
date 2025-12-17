"""FastAPI application factory for the IntelliApprove backend."""
from __future__ import annotations

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.api.middleware.cors_config import add_cors

from app.api.v1 import (
    admin_routes,
    chat_routes,
    otp_routes,
    sanction_routes,
    upload_routes,
    offermart_routes,
    bureau_routes,
    underwriting_routes,
    loan_routes,
)
from app.config.settings import get_settings


def create_app() -> FastAPI:
    """Create and configure the FastAPI application instance."""
    settings = get_settings()

    app = FastAPI(
        title=settings.project_name,
        version="0.1.0",
    )
    # Use centralized CORS config per target structure
    add_cors(app)

    prefix = settings.api_v1_prefix.rstrip("/")
    app.include_router(chat_routes.router, prefix=prefix)
    app.include_router(upload_routes.router, prefix=prefix)
    app.include_router(otp_routes.router, prefix=prefix)
    app.include_router(sanction_routes.router, prefix=prefix)
    app.include_router(admin_routes.router, prefix=prefix)
    app.include_router(offermart_routes.router, prefix=prefix)
    app.include_router(bureau_routes.router, prefix=prefix)
    app.include_router(underwriting_routes.router, prefix=prefix)
    app.include_router(loan_routes.router, prefix=prefix)

    @app.get("/health", tags=["System"])
    def healthcheck() -> dict[str, str]:
        return {"status": "ok"}

    # Debug: Print all routes on startup
    @app.on_event("startup")
    async def startup_event():
        print("\n✅ Registered Routes:")
        for route in app.routes:
            if hasattr(route, "path"):
                print(f"   {route.methods} {route.path}")
        print("\n")

    return app


app = create_app()
