import uuid
from uuid import UUID

from sqlalchemy import DateTime, Float, ForeignKey, Integer, func, select
from sqlalchemy.dialects.postgresql import UUID as PSQL_UUID
from sqlalchemy.orm import Session, mapped_column, relationship, selectinload

from .base import Base


class OrderItem(Base):
    __tablename__ = "order_item"

    id = mapped_column(PSQL_UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    order_id = mapped_column(
        PSQL_UUID(as_uuid=True),
        ForeignKey("order.id", ondelete="CASCADE"),
        nullable=False,
    )
    product_id = mapped_column(
        PSQL_UUID(as_uuid=True),
        ForeignKey("product.id", ondelete="CASCADE"),
        nullable=False,
    )
    quantity = mapped_column(Integer, nullable=False, default=0)
    price_at_purchase = mapped_column(Float, nullable=False)
    created_at = mapped_column(
        DateTime(timezone=True), nullable=False, default=func.now()
    )
    order = relationship("Order", back_populates="order_items")
    product = relationship("Product", back_populates="order_items")


def list_order_items(
    session: Session,
    order_item_id: UUID | None = None,
    order_id: UUID | None = None,
    product_id: UUID | None = None,
    load_order: bool = False,
    load_product: bool = False,
) -> list[OrderItem]:
    stmt = select(OrderItem)
    if load_order:
        stmt = stmt.options(selectinload(OrderItem.order))
    if load_product:
        stmt = stmt.options(selectinload(OrderItem.product))
    if order_item_id is not None:
        stmt = stmt.where(OrderItem.id == order_item_id)
    if order_id is not None:
        stmt = stmt.where(OrderItem.order_id == order_id)
    if product_id is not None:
        stmt = stmt.where(OrderItem.product_id == product_id)
    return session.scalars(stmt).all()


def get_order_item_by_id(session: Session, order_item_id: UUID) -> "OrderItem | None":
    return session.scalar(select(OrderItem).where(OrderItem.id == order_item_id))


def create_order_item(session: Session, values: dict) -> OrderItem:
    order_item = OrderItem(**values)
    session.add(order_item)
    session.flush()
    return order_item


def update_order_item(
    session: Session,
    order_item_id: UUID,
    *,
    quantity: int,
    price_at_purchase: float,
) -> OrderItem:
    order_item = get_order_item_by_id(session, order_item_id)
    if order_item is None:
        raise ValueError(f"Order item not found: {order_item_id}")

    order_item.quantity = quantity
    order_item.price_at_purchase = price_at_purchase

    session.flush()
    return order_item


def delete_order_item(session: Session, order_item: OrderItem) -> None:
    session.delete(order_item)
