from uuid import UUID

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from auth import get_current_user, require_permission
from models.db.session import get_session
from request_schemas.schemas import (
    CheckoutRequest,
    CreateOrderItemRequest,
    UpdateOrderItemRequest,
    UpdateOrderRequest,
)
from response_schemas.schemas import CheckoutResponse, Order, OrderItem
from services import checkout_service, order_service

router = APIRouter(tags=["orders"])


# --- Orders ---


@router.get("/orders", response_model=list[Order])
def list_orders(
    user: dict = Depends(require_permission("read:order")),
    session: Session = Depends(get_session),
):
    return order_service.list_orders(session, user)


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
