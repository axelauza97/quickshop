from uuid import UUID

from fastapi import HTTPException
from sqlalchemy.orm import Session

from models.db import category as category_repo
from request_schemas.schemas import CreateCategoryRequest, UpdateCategoryRequest


def list_categories(session: Session):
    return category_repo.list_categories(session)


def get_category(session: Session, category_id: UUID):
    categories = category_repo.list_categories(
        session, category_id=category_id, load_products=True
    )
    category = categories[0] if categories else None
    if category is None:
        raise HTTPException(status_code=404, detail="Category not found")
    return category


def create_category(session: Session, payload: CreateCategoryRequest):
    return category_repo.create_category(session, payload.model_dump())


def update_category(session: Session, category_id: UUID, payload: UpdateCategoryRequest):
    category = category_repo.get_category_by_id(session, category_id)
    if category is None:
        raise HTTPException(status_code=404, detail="Category not found")

    updates = payload.model_dump(exclude_unset=True)
    try:
        return category_repo.update_category(
            session,
            category_id,
            name=updates.get("name", category.name),
        )
    except ValueError as exc:
        raise HTTPException(status_code=404, detail="Category not found") from exc


def delete_category(session: Session, category_id: UUID) -> dict:
    category = category_repo.get_category_by_id(session, category_id)
    if category is None:
        raise HTTPException(status_code=404, detail="Category not found")
    category_repo.delete_category(session, category)
    return {"deleted": True, "id": str(category_id)}
