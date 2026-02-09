from sqlalchemy.orm import declarative_base
from sqlalchemy.orm import mapped_column, relationship
from sqlalchemy import (
    DateTime,
    Float,
    Integer,
    String,
    func,
)
from sqlalchemy.dialects.postgresql import UUID as PSQL_UUID
from sqlalchemy.orm import mapped_column, relationship
from sqlalchemy.sql.expression import text
from sqlalchemy import ForeignKey
import uuid

Base = declarative_base()


class Product(Base):
    __tablename__ = "product"

    id = mapped_column(PSQL_UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    name = mapped_column(String, nullable=False)
    description = mapped_column(String, nullable=True)
    price = mapped_column(Float, nullable=False)
    category_id = mapped_column(
        PSQL_UUID(as_uuid=True),
        ForeignKey("category.id", ondelete="CASCADE"),
        nullable=False,
    )
    stock = mapped_column(Integer, nullable=False, server_default=text("0"))
    created_at = mapped_column(
        DateTime(timezone=True), nullable=False, default=func.now()
    )
    category = relationship("Category", back_populates="products")
