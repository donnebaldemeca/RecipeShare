from fastapi import APIRouter
from .users import router as users_router
from .feed import router as feed_router

# Create a master router for this package
api_router = APIRouter()

# Include the sub-routers
api_router.include_router(users_router)
api_router.include_router(feed_router)