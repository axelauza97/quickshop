import uuid
from uuid import UUID

from sqlalchemy import DateTime, ForeignKey, Integer, UniqueConstraint, func, select, delete
from sqlalchemy.dialects.postgresql import UUID as PSQL_UUID
from sqlalchemy.orm import Session, mapped_column, relationship, selectinload
from sqlalchemy.sql.expression import text

from .base import Base


class CartItem(Base):
    __tablename__ = "cart_item"
    __table_args__ = (UniqueConstraint("user_id", "product_id"),)

    id = mapped_column(PSQL_UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = mapped_column(
        PSQL_UUID(as_uuid=True),
        ForeignKey("user.id", ondelete="CASCADE"),
        nullable=False,
    )
    product_id = mapped_column(
        PSQL_UUID(as_uuid=True),
        ForeignKey("product.id", ondelete="CASCADE"),
        nullable=False,
    )
    quantity = mapped_column(Integer, nullable=False, server_default=text("1"))
    created_at = mapped_column(
        DateTime(timezone=True), nullable=False, default=func.now()
    )
    user = relationship("User", back_populates="cart_items")
    product = relationship("Product", back_populates="cart_items")


def list_cart_items(
    session: Session,
    user_id: UUID | None = None,
    product_id: UUID | None = None,
    load_product: bool = False,
) -> list[CartItem]:
    stmt = select(CartItem)
    if load_product:
        stmt = stmt.options(selectinload(CartItem.product))
    if user_id is not None:
        stmt = stmt.where(CartItem.user_id == user_id)
    if product_id is not None:
        stmt = stmt.where(CartItem.product_id == product_id)
    return session.scalars(stmt).all()


def get_cart_item(session: Session, user_id: UUID, product_id: UUID) -> CartItem | None:
    return session.scalar(
        select(CartItem).where(
            CartItem.user_id == user_id, CartItem.product_id == product_id
        )
    )


def create_cart_item(session: Session, values: dict) -> CartItem:
    cart_item = CartItem(**values)
    session.add(cart_item)
    session.flush()
    return cart_item


def update_cart_item(
    session: Session,
    user_id: UUID,
    product_id: UUID,
    *,
    quantity: int,
) -> CartItem:
    cart_item = get_cart_item(session, user_id, product_id)
    if cart_item is None:
        raise ValueError(
            f"Cart item not found for user {user_id} and product {product_id}"
        )

    cart_item.quantity = quantity

    session.flush()
    return cart_item


def delete_cart_item(session: Session, cart_item: CartItem) -> None:
    session.delete(cart_item)


def clear_cart(session: Session, user_id: UUID) -> None:
    session.execute(delete(CartItem).where(CartItem.user_id == user_id))
