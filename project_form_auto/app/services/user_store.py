from typing import Optional

from app.models.schemas import UserData, UserPatchRequest

USER: Optional[UserData] = None


def get_user() -> Optional[UserData]:
    return USER

