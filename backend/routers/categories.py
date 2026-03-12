from uuid import UUID

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from auth import require_permission
from models.db.session import get_session
from request_schemas.schemas import CreateCategoryRequest, UpdateCategoryRequest
from response_schemas.schemas import Category
from services import category_service

router = APIRouter(prefix="/categories", tags=["categories"])


@router.get("/", response_model=list[Category])
def list_categories(session: Session = Depends(get_session)):
    return category_service.list_categories(session)


@router.get("/{category_id}", response_model=Category)
def get_category(category_id: UUID, session: Session = Depends(get_session)):
    return category_service.get_category(session, category_id)


@router.post("/", response_model=Category)
def create_category(
    payload: CreateCategoryRequest,
    user: dict = Depends(require_permission("create:category")),
    session: Session = Depends(get_session),
):
    return category_service.create_category(session, payload)


@router.put("/{category_id}", response_model=Category)
def update_category(
    category_id: UUID,
    payload: UpdateCategoryRequest,
    user: dict = Depends(require_permission("update:category")),
    session: Session = Depends(get_session),
):
    return category_service.update_category(session, category_id, payload)


@router.delete("/{category_id}", response_model=dict)
def delete_category(
    category_id: UUID,
    user: dict = Depends(require_permission("delete:category")),
    session: Session = Depends(get_session),
):
    return category_service.delete_category(session, category_id)
