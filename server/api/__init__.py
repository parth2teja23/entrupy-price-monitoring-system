from fastapi import APIRouter, Depends
from api.products import router as products_router
from api.deps import verify_api_key

api_router = APIRouter()
api_router.include_router(
    products_router, 
    prefix="/products", 
    tags=["Products"],
    dependencies=[Depends(verify_api_key)]
)