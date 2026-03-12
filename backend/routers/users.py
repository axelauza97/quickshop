from uuid import UUID

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from auth import get_current_user, require_permission
from models.db.session import get_session
from response_schemas.schemas import User
from services import user_service

router = APIRouter(prefix="/users", tags=["users"])


@router.get("/me", response_model=User)
def get_current_user_profile(
    user: dict = Depends(get_current_user),
    session: Session = Depends(get_session),
):
    return user_service.get_user(session, user["id"], user)


@router.get("/", response_model=list[User])
def list_users(
    user: dict = Depends(require_permission("read:user")),
    session: Session = Depends(get_session),
):
    return user_service.list_users(session, user)


@router.get("/{user_id}", response_model=User)
def get_user(
    user_id: UUID,
    user: dict = Depends(require_permission("read:user")),
    session: Session = Depends(get_session),
):
    return user_service.get_user(session, user_id, user)


@router.delete("/{user_id}", response_model=dict)
def delete_user(
    user_id: UUID,
    user: dict = Depends(require_permission("delete:user")),
    session: Session = Depends(get_session),
):
    return user_service.delete_user(session, user_id)
