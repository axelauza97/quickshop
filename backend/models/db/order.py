from sqlalchemy.orm import declarative_base
from sqlalchemy.orm import mapped_column, relationship
from sqlalchemy import (
    DateTime,
    Float,
    func,
)
from sqlalchemy.dialects.postgresql import UUID as PSQL_UUID
from sqlalchemy.orm import mapped_column, relationship
import uuid

Base = declarative_base()


class Order(Base):
    __tablename__ = "order"

    id = mapped_column(PSQL_UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = mapped_column(PSQL_UUID(as_uuid=True), nullable=False)
    total_amount = mapped_column(Float, nullable=False)
    created_at = mapped_column(
        DateTime(timezone=True), nullable=False, default=func.now()
    )
    order_items = relationship(
        "OrderItem", back_populates="order", cascade="all, delete-orphan"
    )
