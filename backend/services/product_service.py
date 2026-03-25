from uuid import UUID

from fastapi import HTTPException
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from models.db import category as category_repo
from models.db import order_item as order_item_repo
from models.db import product as product_repo
from request_schemas.schemas import CreateProductRequest, UpdateProductRequest

PRODUCT_DELETE_BLOCKED_MESSAGE = (
    "This product can't be deleted because it is part of an existing order."
)


def list_products(
    session: Session,
    search: str | None = None,
    category_id: UUID | None = None,
    skip: int = 0,
    limit: int = 20,
    sort_by: str = "name",
    order: str = "asc",
):
    return product_repo.list_products(
        session,
        search=search,
        category_id=category_id,
        skip=skip,
        limit=limit,
        sort_by=sort_by,
        order=order,
    )


def get_product(session: Session, product_id: UUID):
    product = product_repo.get_product_by_id(session, product_id)
    if product is None:
        raise HTTPException(status_code=404, detail="Product not found")
    return product


def create_product(session: Session, payload: CreateProductRequest):
    if category_repo.get_category_by_id(session, payload.category_id) is None:
        raise HTTPException(status_code=400, detail="Invalid category_id: category not found")
    return product_repo.create_product(session, payload.model_dump())


def update_product(session: Session, product_id: UUID, payload: UpdateProductRequest):
    product = product_repo.get_product_by_id(session, product_id)
    if product is None:
        raise HTTPException(status_code=404, detail="Product not found")
    updates = payload.model_dump(exclude_unset=True)
    if (
        "category_id" in updates
        and category_repo.get_category_by_id(session, updates["category_id"]) is None
    ):
        raise HTTPException(status_code=400, detail="Invalid category_id: category not found")
    try:
        return product_repo.update_product(
            session,
            product_id,
            name=updates.get("name", product.name),
            description=updates.get("description", product.description),
            price=updates.get("price", product.price),
            category_id=updates.get("category_id", product.category_id),
            stock=updates.get("stock", product.stock),
            image_url=updates.get("image_url", product.image_url),
        )
    except ValueError as exc:
        raise HTTPException(status_code=404, detail="Product not found") from exc


def delete_product(session: Session, product_id: UUID) -> dict:
    product = product_repo.get_product_by_id(session, product_id)
    if product is None:
        raise HTTPException(status_code=404, detail="Product not found")

    if order_item_repo.has_order_items_for_product(session, product_id):
        raise HTTPException(status_code=409, detail=PRODUCT_DELETE_BLOCKED_MESSAGE)

    try:
        product_repo.delete_product(session, product)
    except IntegrityError as exc:
        session.rollback()
        raise HTTPException(
            status_code=409,
            detail=PRODUCT_DELETE_BLOCKED_MESSAGE,
        ) from exc

    return {"deleted": True, "id": str(product_id)}
