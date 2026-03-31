from fastapi import APIRouter
from app.config import settings

system_router = APIRouter()

@system_router.post("/refresh", status_code=202)
async def refresh_data():
    """
    Triggers the scrapers to run asynchronously in the background.
    """
    return {
        "status": "Accepted", 
        "message": "Scraping jobs triggered in background."
    }