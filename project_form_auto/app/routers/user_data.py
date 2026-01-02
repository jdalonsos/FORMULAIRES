from fastapi import APIRouter, HTTPException, status

from app.models.schemas import UserResponse
from app.services.user_store import get_user

router = APIRouter(prefix="/user", tags=["user"])

@router.get("", response_model=UserResponse)
def read_user() -> UserResponse:
    user = get_user()
    if user is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found",
        )
    return UserResponse(user=user)
