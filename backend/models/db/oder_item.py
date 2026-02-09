from sqlalchemy.orm import declarative_base
from sqlalchemy.orm import mapped_column, relationship
from sqlalchemy import (
    DateTime,
    Float,
    Integer,
    func,
)
from sqlalchemy.dialects.postgresql import UUID as PSQL_UUID
from sqlalchemy.orm import mapped_column, relationship
import uuid

Base = declarative_base()


class OrderItem(Base):
    __tablename__ = "order_item"

    id = mapped_column(PSQL_UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    order_id = mapped_column(PSQL_UUID(as_uuid=True), nullable=False)
    product_id = mapped_column(PSQL_UUID(as_uuid=True), nullable=False)
    quantity = mapped_column(Integer, nullable=False, default=0)
    price_at_purchase = mapped_column(Float, nullable=False)
    created_at = mapped_column(
        DateTime(timezone=True), nullable=False, default=func.now()
    )
    order = relationship("Order", back_populates="order_items")
    product = relationship("Product")
