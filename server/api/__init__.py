from fastapi import APIRouter
from api.products import router as products_router

api_router = APIRouter()
api_router.include_router(products_router, prefix="/products", tags=["Products"])