from fastapi import APIRouter

router = APIRouter(
    prefix="/users",
    tags=["User"]
)

@router.get("/me")
async def get_my_profile():
    pass

@router.patch("/me")
async def update_my_profile():
    pass

@router.get("/me/privacy")
async def get_privacy_settings():
    pass

@router.patch("/me/privacy")
async def update_privacy_settings():
    pass

@router.get("/{user_id}")
async def get_user_profile():
    pass

@router.get("/{user_id}/posts")
async def get_user_posts():
    pass
