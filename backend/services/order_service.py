from uuid import UUID

from fastapi import HTTPException
from sqlalchemy.orm import Session

from models.db import order as order_repo
from models.db import order_item as order_item_repo
from models.db import product as product_repo
from request_schemas.schemas import (
    CreateOrderItemRequest,
    UpdateOrderItemRequest,
    UpdateOrderRequest,
)


VALID_ORDER_STATUSES = {"pending", "confirmed", "shipped", "delivered", "cancelled"}


def list_orders(session: Session, current_user: dict):
    if current_user["role"] == "admin":
        return order_repo.list_orders(session, load_items=True)
    return order_repo.list_orders(session, user_id=current_user["id"], load_items=True)


def get_order(session: Session, order_id: UUID, current_user: dict):
    orders = order_repo.list_orders(session, order_id=order_id, load_items=True)
    order = orders[0] if orders else None
    if order is None:
        raise HTTPException(status_code=404, detail="Order not found")
    if current_user["role"] != "admin" and order.user_id != current_user["id"]:
        raise HTTPException(status_code=403, detail="Forbidden")
    return order


def update_order(session: Session, order_id: UUID, payload: UpdateOrderRequest):
    order = order_repo.get_order_by_id(session, order_id)
    if order is None:
        raise HTTPException(status_code=404, detail="Order not found")
    if payload.status is not None and payload.status not in VALID_ORDER_STATUSES:
        raise HTTPException(
            status_code=400,
            detail=f"Invalid status. Must be one of: {', '.join(sorted(VALID_ORDER_STATUSES))}",
        )
    updates = payload.model_dump(exclude_unset=True)
    try:
        return order_repo.update_order(
            session,
            order_id,
            total_amount=updates.get("total_amount", order.total_amount),
            status=updates.get("status", order.status),
        )
    except ValueError as exc:
        raise HTTPException(status_code=404, detail="Order not found") from exc


def delete_order(session: Session, order_id: UUID) -> dict:
    order = order_repo.get_order_by_id(session, order_id)
    if order is None:
        raise HTTPException(status_code=404, detail="Order not found")
    order_repo.delete_order(session, order)
    return {"deleted": True, "id": str(order_id)}


# --- Order Items ---


def list_order_items(session: Session):
    return order_item_repo.list_order_items(session)


def get_order_item(session: Session, order_item_id: UUID):
    order_item = order_item_repo.get_order_item_by_id(session, order_item_id)
    if order_item is None:
        raise HTTPException(status_code=404, detail="Order item not found")
    return order_item


def create_order_item(session: Session, payload: CreateOrderItemRequest):
    if order_repo.get_order_by_id(session, payload.order_id) is None:
        raise HTTPException(status_code=400, detail="Invalid order_id: order not found")
    if product_repo.get_product_by_id(session, payload.product_id) is None:
        raise HTTPException(status_code=400, detail="Invalid product_id: product not found")
    return order_item_repo.create_order_item(session, payload.model_dump())


def update_order_item(session: Session, order_item_id: UUID, payload: UpdateOrderItemRequest):
    order_item = order_item_repo.get_order_item_by_id(session, order_item_id)
    if order_item is None:
        raise HTTPException(status_code=404, detail="Order item not found")
    updates = payload.model_dump(exclude_unset=True)
    try:
        return order_item_repo.update_order_item(
            session,
            order_item_id,
            quantity=updates.get("quantity", order_item.quantity),
            price_at_purchase=updates.get(
                "price_at_purchase", order_item.price_at_purchase
            ),
        )
    except ValueError as exc:
        raise HTTPException(status_code=404, detail="Order item not found") from exc


def delete_order_item(session: Session, order_item_id: UUID) -> dict:
    order_item = order_item_repo.get_order_item_by_id(session, order_item_id)
    if order_item is None:
        raise HTTPException(status_code=404, detail="Order item not found")
    order_item_repo.delete_order_item(session, order_item)
    return {"deleted": True, "id": str(order_item_id)}
