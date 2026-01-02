from typing import Optional

from app.models.schemas import UserData, UserPatchRequest

# Les données utilisateur sont stockées en mémoire pour simplifier l’architecture

USER: Optional[UserData] = None


def get_user() -> Optional[UserData]:
    return USER


def create_user(user_data: UserData) -> UserData:
    global USER
    if USER is not None:
        raise ValueError("Un utilisateur existe déjà.")
    USER = user_data
    return USER


# Logique put : je renvoie l'utilisateur un utilisateur complet. 
def replace_user(user_data: UserData) -> UserData:
    global USER
    if USER is None:
        raise ValueError("Aucun utilisateur n'existe pour le remplacer.")
    USER = user_data
    return USER


def patch_user(partial: UserPatchRequest) -> UserData:
    global USER
    if USER is None:
        raise ValueError("Aucun utilisateur n'existe pour le modifier.")

    current = USER.model_dump()  # Pour récupérer un dicctionnaire python.
    updates = partial.model_dump(exclude_unset=True)

    current.update(updates)
    USER = UserData(**current)
    return USER
