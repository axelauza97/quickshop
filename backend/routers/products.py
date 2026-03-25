from typing import Literal
from uuid import UUID

from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session

from auth import require_permission
from models.db.session import get_session
from request_schemas.schemas import CreateProductRequest, UpdateProductRequest
from response_schemas.schemas import PaginatedProducts, Product
from services import product_service

router = APIRouter(prefix="/products", tags=["products"])


@router.get("/", response_model=PaginatedProducts)
def list_products(
    search: str | None = None,
    category_id: UUID | None = None,
    skip: int = Query(default=0, ge=0),
    limit: int = Query(default=20, ge=1, le=100),
    sort_by: Literal["name", "category", "price", "stock", "created_at"] = "name",
    order: Literal["asc", "desc"] = "asc",
    session: Session = Depends(get_session),
):
    items, total = product_service.list_products(
        session,
        search=search,
        category_id=category_id,
        skip=skip,
        limit=limit,
        sort_by=sort_by,
        order=order,
    )
    return {"items": items, "total": total}


@router.get("/{product_id}", response_model=Product)
def get_product(product_id: UUID, session: Session = Depends(get_session)):
    return product_service.get_product(session, product_id)


@router.post("/", response_model=Product)
def create_product(
    payload: CreateProductRequest,
    user: dict = Depends(require_permission("create:product")),
    session: Session = Depends(get_session),
):
    return product_service.create_product(session, payload)


@router.put("/{product_id}", response_model=Product)
def update_product(
    product_id: UUID,
    payload: UpdateProductRequest,
    user: dict = Depends(require_permission("update:product")),
    session: Session = Depends(get_session),
):
    return product_service.update_product(session, product_id, payload)


@router.delete("/{product_id}", response_model=dict)
def delete_product(
    product_id: UUID,
    user: dict = Depends(require_permission("delete:product")),
    session: Session = Depends(get_session),
):
    return product_service.delete_product(session, product_id)
