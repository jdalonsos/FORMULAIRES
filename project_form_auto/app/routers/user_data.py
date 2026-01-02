from fastapi import APIRouter, HTTPException, status

from app.models.schemas import UserData, UserPatchRequest, UserResponse
from app.services.user_store import (
    create_user,
    delete_user,
    get_user,
    patch_user,
    replace_user,
)

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


@router.post("", response_model=UserResponse, status_code=status.HTTP_201_CREATED)
def create_user_endpoint(user_data: UserData) -> UserResponse:
    try:
        user = create_user(user_data)
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=str(e),
        ) from e
    return UserResponse(user=user)


@router.put("", response_model=UserResponse)
def replace_user_endpoint(user_data: UserData) -> UserResponse:
    try:
        user = replace_user(user_data)
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(e),
        ) from e
    return UserResponse(user=user)


@router.patch("", response_model=UserResponse)
def patch_user_endpoint(patch: UserPatchRequest) -> UserResponse:
    try:
        user = patch_user(patch)
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(e),
        ) from e
    return UserResponse(user=user)

@router.delete("", status_code=status.HTTP_204_NO_CONTENT)
def delete_user_endpoint() -> None:
    delete_user()
    return None
