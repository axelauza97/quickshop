from uuid import UUID

from fastapi import HTTPException
from sqlalchemy.orm import Session

from models.db import cart_item as cart_item_repo
from models.db import order as order_repo
from models.db import order_item as order_item_repo


def checkout(session: Session, user_id: UUID, shipping_address: str | None = None) -> dict:
    items = cart_item_repo.list_cart_items(session, user_id=user_id, load_product=True)
    if not items:
        raise HTTPException(status_code=400, detail="Cart is empty")

    total_amount = 0.0
    for item in items:
        if item.product is None:
            raise HTTPException(
                status_code=400,
                detail=f"Product no longer exists for cart item {item.id}",
            )
        if item.product.stock < item.quantity:
            raise HTTPException(
                status_code=400,
                detail=f"Insufficient stock for '{item.product.name}'. "
                f"Available: {item.product.stock}, requested: {item.quantity}",
            )
        total_amount += item.quantity * item.product.price

    total_amount = round(total_amount, 2)

    order = order_repo.Order(
        user_id=user_id,
        total_amount=total_amount,
        status="confirmed",
    )
    session.add(order)
    session.flush()

    for item in items:
        oi = order_item_repo.OrderItem(
            order_id=order.id,
            product_id=item.product_id,
            quantity=item.quantity,
            price_at_purchase=item.product.price,
        )
        session.add(oi)

        item.product.stock -= item.quantity

    cart_item_repo.clear_cart(session, user_id)

    session.flush()
    session.refresh(order)

    return {"order": order, "message": "Order placed successfully"}
