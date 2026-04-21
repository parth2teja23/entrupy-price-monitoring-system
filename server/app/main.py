from __future__ import annotations
from __future__ import annotations
from pathlib import Path
from fastapi import FastAPI, Request, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles
from app.config import settings

def create_app() -> FastAPI:
    application = FastAPI(
        title=settings.PROJECT_NAME,
        openapi_url=f"{settings.API_V1_STR}/openapi.json"
    )

    application.add_middleware(
        CORSMiddleware,
        allow_origins=["*"],
        allow_credentials=False,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    @application.get("/health", tags=["Health"])
    async def health_check():
        return {
            "status": "up",
            "project": settings.PROJECT_NAME
        }

    from api import api_router
    from api.marketplaces import router as marketplaces_router

    project_root = Path(__file__).resolve().parents[2]
    client_dist = project_root / "client" / "dist"

    application.include_router(api_router, prefix=settings.API_V1_STR)
    application.include_router(marketplaces_router, prefix="/internal")

    if client_dist.exists():
        assets_dir = client_dist / "assets"
        if assets_dir.exists():
            application.mount("/assets", StaticFiles(directory=assets_dir), name="assets")

        @application.get("/{full_path:path}", include_in_schema=False)
        async def spa_fallback(request: Request, full_path: str):
            if request.url.path.startswith(settings.API_V1_STR) or request.url.path == "/health" or request.url.path.startswith("/internal"):
                raise HTTPException(status_code=404, detail="Not found")
            return FileResponse(client_dist / "index.html")
    else:
        from webapp.routes import router as webapp_router

        application.include_router(webapp_router)

    return application

app = create_app()