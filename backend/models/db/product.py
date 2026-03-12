import uuid
from uuid import UUID

from sqlalchemy import DateTime, Float, ForeignKey, Integer, String, func, or_, select
from sqlalchemy.dialects.postgresql import UUID as PSQL_UUID
from sqlalchemy.orm import Session, mapped_column, relationship, selectinload
from sqlalchemy.sql.expression import text

from .base import Base


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
    image_url = mapped_column(String, nullable=True)
    created_at = mapped_column(
        DateTime(timezone=True), nullable=False, default=func.now()
    )
    category = relationship("Category", back_populates="products")
    order_items = relationship("OrderItem", back_populates="product")
    cart_items = relationship("CartItem", back_populates="product")


def list_products(
    session: Session,
    product_id: UUID | None = None,
    category_id: UUID | None = None,
    search: str | None = None,
    skip: int = 0,
    limit: int = 20,
    load_category: bool = False,
    load_order_items: bool = False,
) -> list[Product]:
    stmt = select(Product)
    if load_category:
        stmt = stmt.options(selectinload(Product.category))
    if load_order_items:
        stmt = stmt.options(selectinload(Product.order_items))
    if product_id is not None:
        stmt = stmt.where(Product.id == product_id)
    if category_id is not None:
        stmt = stmt.where(Product.category_id == category_id)
    if search is not None:
        pattern = f"%{search}%"
        stmt = stmt.where(
            or_(Product.name.ilike(pattern), Product.description.ilike(pattern))
        )
    stmt = stmt.offset(skip).limit(limit)
    return session.scalars(stmt).all()


def get_product_by_id(session: Session, product_id: UUID) -> Product | None:
    return session.scalar(select(Product).where(Product.id == product_id))


def create_product(session: Session, values: dict) -> Product:
    product = Product(**values)
    session.add(product)
    session.flush()
    return product


def update_product(
    session: Session,
    product_id: UUID,
    *,
    name: str,
    description: str | None,
    price: float,
    category_id: UUID,
    stock: int,
    image_url: str | None,
) -> Product:
    product = get_product_by_id(session, product_id)
    if product is None:
        raise ValueError(f"Product not found: {product_id}")

    product.name = name
    product.description = description
    product.price = price
    product.category_id = category_id
    product.stock = stock
    product.image_url = image_url

    session.flush()
    return product


def delete_product(session: Session, product: Product) -> None:
    session.delete(product)
