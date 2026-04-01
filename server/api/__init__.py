from __future__ import annotations
from __future__ import annotations
from fastapi import APIRouter
from api.products import router as products_router
from api.system import router as system_router
from api.analytics import router as analytics_router
from api.events import router as events_router
from api.webhooks import router as webhooks_router

api_router = APIRouter()
api_router.include_router(products_router)
api_router.include_router(system_router)
api_router.include_router(analytics_router)
api_router.include_router(events_router)
api_router.include_router(webhooks_router)
