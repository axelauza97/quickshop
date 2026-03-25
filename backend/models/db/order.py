import uuid
from uuid import UUID

from sqlalchemy import DateTime, Float, ForeignKey, Select, String, func, select
from sqlalchemy.dialects.postgresql import UUID as PSQL_UUID
from sqlalchemy.orm import Session, mapped_column, relationship, selectinload
from sqlalchemy.sql.expression import text

from .base import Base


class Order(Base):
    __tablename__ = "order"

    id = mapped_column(PSQL_UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = mapped_column(
        PSQL_UUID(as_uuid=True),
        ForeignKey("user.id", ondelete="CASCADE"),
        nullable=False,
    )
    total_amount = mapped_column(Float, nullable=False)
    status = mapped_column(String, nullable=False, server_default=text("'pending'"))
    created_at = mapped_column(
        DateTime(timezone=True), nullable=False, default=func.now()
    )
    user = relationship("User", back_populates="orders")
    order_items = relationship(
        "OrderItem", back_populates="order", cascade="all, delete-orphan"
    )


def _apply_order_filters(
    stmt: Select,
    *,
    user_id: UUID | None = None,
    order_id: UUID | None = None,
) -> Select:
    if user_id is not None:
        stmt = stmt.where(Order.user_id == user_id)
    if order_id is not None:
        stmt = stmt.where(Order.id == order_id)
    return stmt


def _apply_order_sort(stmt: Select, *, sort_by: str, order: str) -> Select:
    sort_column = {
        "created_at": Order.created_at,
        "total_amount": Order.total_amount,
        "status": Order.status,
    }[sort_by]
    direction = sort_column.desc() if order == "desc" else sort_column.asc()
    tie_breaker = Order.id.desc() if order == "desc" else Order.id.asc()
    return stmt.order_by(direction, tie_breaker)


def list_orders(
    session: Session,
    user_id: UUID | None = None,
    order_id: UUID | None = None,
    sort_by: str = "created_at",
    order: str = "desc",
    skip: int = 0,
    limit: int = 100,
    load_items: bool = False,
) -> tuple[list[Order], int]:
    stmt = select(Order)
    if load_items:
        stmt = stmt.options(selectinload(Order.order_items))
    stmt = _apply_order_filters(stmt, user_id=user_id, order_id=order_id)
    stmt = _apply_order_sort(stmt, sort_by=sort_by, order=order)
    stmt = stmt.offset(skip).limit(limit)

    count_stmt = _apply_order_filters(
        select(func.count(Order.id)),
        user_id=user_id,
        order_id=order_id,
    )

    items = session.scalars(stmt).all()
    total = session.scalar(count_stmt) or 0
    return items, total


def get_order_by_id(session: Session, order_id: UUID) -> "Order | None":
    return session.scalar(select(Order).where(Order.id == order_id))


def create_order(session: Session, values: dict) -> Order:
    order = Order(**values)
    session.add(order)
    session.flush()
    return order


def update_order(
    session: Session,
    order_id: UUID,
    *,
    total_amount: float,
    status: str,
) -> Order:
    order = get_order_by_id(session, order_id)
    if order is None:
        raise ValueError(f"Order not found: {order_id}")

    order.total_amount = total_amount
    order.status = status

    session.flush()
    return order


def delete_order(session: Session, order: Order) -> None:
    session.delete(order)
    session.flush()
