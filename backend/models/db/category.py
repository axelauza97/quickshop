from sqlalchemy.orm import declarative_base
from sqlalchemy.orm import mapped_column, relationship
from sqlalchemy import (
    DateTime,
    String,
    func,
)
from sqlalchemy.dialects.postgresql import UUID as PSQL_UUID
from sqlalchemy.orm import mapped_column, relationship
import uuid

Base = declarative_base()


class Category(Base):
    __tablename__ = "category"

    id = mapped_column(PSQL_UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    name = mapped_column(String, unique=True, nullable=False)
    created_at = mapped_column(
        DateTime(timezone=True), nullable=False, default=func.now()
    )

    products = relationship(
        "Product", back_populates="category", cascade="all, delete-orphan"
    )
