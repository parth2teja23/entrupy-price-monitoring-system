from fastapi import FastAPI
from app.config import settings

def create_app() -> FastAPI:
    application = FastAPI(
        title=settings.PROJECT_NAME,
        openapi_url=f"{settings.API_V1_STR}/openapi.json"
    )

    @application.get("/health", tags=["Health"])
    async def health_check():
        return {
            "status": "up",
            "project": settings.PROJECT_NAME
        }

    # TODO: Include routers here once defined
    # application.include_router(api_router, prefix=settings.API_V1_STR)

    return application

app = create_app()