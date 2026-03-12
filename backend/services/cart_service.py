from uuid import UUID

from fastapi import HTTPException
from sqlalchemy.orm import Session

from models.db import cart_item as cart_item_repo
from models.db import product as product_repo


def get_cart(session: Session, user_id: UUID) -> dict:
    items = cart_item_repo.list_cart_items(session, user_id=user_id, load_product=True)
    total = sum(
        item.quantity * item.product.price
        for item in items
        if item.product is not None
    )
    return {"items": items, "total": round(total, 2)}


def add_item(session: Session, user_id: UUID, product_id: UUID, quantity: int):
    product = product_repo.get_product_by_id(session, product_id)
    if product is None:
        raise HTTPException(status_code=400, detail="Product not found")
    if quantity < 1:
        raise HTTPException(status_code=400, detail="Quantity must be at least 1")
    if product.stock < quantity:
        raise HTTPException(status_code=400, detail="Insufficient stock")

    existing = cart_item_repo.get_cart_item(session, user_id, product_id)
    if existing is not None:
        new_qty = existing.quantity + quantity
        if product.stock < new_qty:
            raise HTTPException(status_code=400, detail="Insufficient stock")
        try:
            return cart_item_repo.update_cart_item(
                session,
                user_id,
                product_id,
                quantity=new_qty,
            )
        except ValueError as exc:
            raise HTTPException(status_code=404, detail="Item not in cart") from exc

    return cart_item_repo.create_cart_item(
        session, {"user_id": user_id, "product_id": product_id, "quantity": quantity}
    )


def update_item(session: Session, user_id: UUID, product_id: UUID, quantity: int):
    existing = cart_item_repo.get_cart_item(session, user_id, product_id)
    if existing is None:
        raise HTTPException(status_code=404, detail="Item not in cart")

    if quantity <= 0:
        deleted_item = {
            "id": existing.id,
            "product_id": existing.product_id,
            "quantity": 0,
            "created_at": existing.created_at,
            "product": existing.product,
        }
        cart_item_repo.delete_cart_item(session, existing)
        return deleted_item

    product = product_repo.get_product_by_id(session, product_id)
    if product is not None and product.stock < quantity:
        raise HTTPException(status_code=400, detail="Insufficient stock")

    try:
        return cart_item_repo.update_cart_item(
            session,
            user_id,
            product_id,
            quantity=quantity,
        )
    except ValueError as exc:
        raise HTTPException(status_code=404, detail="Item not in cart") from exc


def remove_item(session: Session, user_id: UUID, product_id: UUID) -> dict:
    existing = cart_item_repo.get_cart_item(session, user_id, product_id)
    if existing is None:
        raise HTTPException(status_code=404, detail="Item not in cart")
    cart_item_repo.delete_cart_item(session, existing)
    return {"deleted": True, "product_id": str(product_id)}


def clear_cart(session: Session, user_id: UUID) -> dict:
    cart_item_repo.clear_cart(session, user_id)
    return {"cleared": True}
