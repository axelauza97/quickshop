from uuid import UUID

from fastapi import HTTPException
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from models.db import user as user_repo


def resolve_role(roles: list[str]) -> str:
    if "admin" in roles:
        return "admin"
    if "customer" in roles:
        return "customer"
    raise HTTPException(status_code=403, detail="Unsupported role.")


def get_or_create_authenticated_user(
    session: Session, auth0_sub: str, roles: list[str]
) -> dict:
    try:
        db_user = user_repo.get_or_create_user_by_auth0_sub(session, auth0_sub)
    except IntegrityError as exc:
        raise HTTPException(status_code=400, detail="Failed to auto-provision user") from exc

    role = resolve_role(roles)
    is_admin = role == "admin"

    if db_user.is_admin != is_admin:
        try:
            user_repo.update_user(session, db_user.id, is_admin=is_admin)
        except ValueError as exc:
            raise HTTPException(status_code=404, detail="User not found") from exc

    return {
        "id": db_user.id,
        "auth0_sub": db_user.auth0_sub,
        "created_at": db_user.created_at,
        "role": role,
    }


def list_users(session: Session, current_user: dict):
    if current_user["role"] == "admin":
        return user_repo.list_users(session)
    user = user_repo.get_user_by_id(session, current_user["id"])
    if user is None:
        raise HTTPException(status_code=404, detail="User not found")
    return [user]


def get_user(session: Session, user_id: UUID, current_user: dict):
    if current_user["role"] != "admin" and user_id != current_user["id"]:
        raise HTTPException(status_code=403, detail="Forbidden")
    user = user_repo.get_user_by_id(session, user_id)
    if user is None:
        raise HTTPException(status_code=404, detail="User not found")
    return user


def delete_user(session: Session, user_id: UUID) -> dict:
    db_user = user_repo.get_user_by_id(session, user_id)
    if db_user is None:
        raise HTTPException(status_code=404, detail="User not found")
    user_repo.delete_user(session, db_user)
    return {"deleted": True, "id": str(user_id)}
