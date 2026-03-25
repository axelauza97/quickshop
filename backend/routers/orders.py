from typing import Literal
from uuid import UUID

from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session

from auth import require_permission
from models.db.session import get_session
from request_schemas.schemas import (
    CheckoutRequest,
    CreateOrderItemRequest,
    UpdateOrderItemRequest,
    UpdateOrderRequest,
)
from response_schemas.schemas import CheckoutResponse, Order, OrderItem, PaginatedOrders
from services import checkout_service, order_service

router = APIRouter(tags=["orders"])

@router.get("/orders", response_model=PaginatedOrders)
def list_orders(
    sort_by: Literal["created_at", "total_amount", "status"] = "created_at",
    order: Literal["asc", "desc"] = "desc",
    skip: int = Query(default=0, ge=0),
    limit: int = Query(default=100, ge=1, le=100),
    user: dict = Depends(require_permission("read:order")),
    session: Session = Depends(get_session),
):
    items, total = order_service.list_orders(
        session,
        user,
        sort_by=sort_by,
        order=order,
        skip=skip,
        limit=limit,
    )
    return {"items": items, "total": total}


@router.get("/orders/{order_id}", response_model=Order)
def get_order(
    order_id: UUID,
    user: dict = Depends(require_permission("read:order")),
    session: Session = Depends(get_session),
):
    return order_service.get_order(session, order_id, user)


@router.put("/orders/{order_id}", response_model=Order)
def update_order(
    order_id: UUID,
    payload: UpdateOrderRequest,
    user: dict = Depends(require_permission("update:order")),
    session: Session = Depends(get_session),
):
    return order_service.update_order(session, order_id, payload)


@router.delete("/orders/{order_id}", response_model=dict)
def delete_order(
    order_id: UUID,
    user: dict = Depends(require_permission("delete:order")),
    session: Session = Depends(get_session),
):
    return order_service.delete_order(session, order_id)


# --- Order Items ---


@router.get("/order-items", response_model=list[OrderItem])
def list_order_items(
    user: dict = Depends(require_permission("read:order_item")),
    session: Session = Depends(get_session),
):
    return order_service.list_order_items(session)


@router.get("/order-items/{order_item_id}", response_model=OrderItem)
def get_order_item(
    order_item_id: UUID,
    user: dict = Depends(require_permission("read:order_item")),
    session: Session = Depends(get_session),
):
    return order_service.get_order_item(session, order_item_id)


@router.post("/order-items", response_model=OrderItem)
def create_order_item(
    payload: CreateOrderItemRequest,
    user: dict = Depends(require_permission("create:order_item")),
    session: Session = Depends(get_session),
):
    return order_service.create_order_item(session, payload)


@router.put("/order-items/{order_item_id}", response_model=OrderItem)
def update_order_item(
    order_item_id: UUID,
    payload: UpdateOrderItemRequest,
    user: dict = Depends(require_permission("update:order_item")),
    session: Session = Depends(get_session),
):
    return order_service.update_order_item(session, order_item_id, payload)


@router.delete("/order-items/{order_item_id}", response_model=dict)
def delete_order_item(
    order_item_id: UUID,
    user: dict = Depends(require_permission("delete:order_item")),
    session: Session = Depends(get_session),
):
    return order_service.delete_order_item(session, order_item_id)


# --- Checkout ---


@router.post("/checkout", response_model=CheckoutResponse)
def checkout(
    payload: CheckoutRequest,
    user: dict = Depends(require_permission("create:checkout")),
    session: Session = Depends(get_session),
):
    return checkout_service.checkout(session, user["id"], payload.shipping_address)
