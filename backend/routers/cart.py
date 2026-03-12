from uuid import UUID

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from auth import get_current_user
from models.db.session import get_session
from request_schemas.schemas import AddCartItemRequest, UpdateCartItemRequest
from response_schemas.schemas import CartItemResponse, CartResponse
from services import cart_service

router = APIRouter(prefix="/cart", tags=["cart"])


@router.get("/", response_model=CartResponse)
def get_cart(
    user: dict = Depends(get_current_user),
    session: Session = Depends(get_session),
):
    return cart_service.get_cart(session, user["id"])


@router.post("/items", response_model=CartItemResponse)
def add_cart_item(
    payload: AddCartItemRequest,
    user: dict = Depends(get_current_user),
    session: Session = Depends(get_session),
):
    return cart_service.add_item(session, user["id"], payload.product_id, payload.quantity)


@router.put("/items/{product_id}", response_model=CartItemResponse)
def update_cart_item(
    product_id: UUID,
    payload: UpdateCartItemRequest,
    user: dict = Depends(get_current_user),
    session: Session = Depends(get_session),
):
    return cart_service.update_item(session, user["id"], product_id, payload.quantity)


@router.delete("/items/{product_id}", response_model=dict)
def remove_cart_item(
    product_id: UUID,
    user: dict = Depends(get_current_user),
    session: Session = Depends(get_session),
):
    return cart_service.remove_item(session, user["id"], product_id)


@router.delete("/", response_model=dict)
def clear_cart(
    user: dict = Depends(get_current_user),
    session: Session = Depends(get_session),
):
    return cart_service.clear_cart(session, user["id"])
