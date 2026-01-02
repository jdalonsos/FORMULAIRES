from typing import Optional

from app.models.schemas import UserData, UserPatchRequest

# Les données utilisateur sont stockées en mémoire pour simplifier l’architecture

_USER: Optional[UserData] = None


def get_user() -> Optional[UserData]:
    return _USER


def create_user(user_data: UserData) -> UserData:
    global _USER
    if _USER is not None:
        raise ValueError("Un utilisateur existe déjà.")
    _USER = user_data
    return _USER


# Logique put : je renvoie l'utilisateur un utilisateur complet. 
def replace_user(user_data: UserData) -> UserData:
    global _USER
    if _USER is None:
        raise ValueError("Aucun utilisateur n'existe pour le remplacer.")
    _USER = user_data
    return _USER


def patch_user(partial: UserPatchRequest) -> UserData:
    global _USER
    if _USER is None:
        raise ValueError("Aucun utilisateur n'existe pour le modifier.")

    current = _USER.model_dump()  # Pour récupérer un dicctionnaire python.
    updates = partial.model_dump(exclude_unset=True)

    current.update(updates)
    _USER = UserData(**current)
    return _USER
