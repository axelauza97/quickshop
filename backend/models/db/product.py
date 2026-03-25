import uuid
from uuid import UUID

from sqlalchemy import DateTime, Float, ForeignKey, Integer, String, Select, func, or_, select
from sqlalchemy.dialects.postgresql import UUID as PSQL_UUID
from sqlalchemy.orm import Session, mapped_column, relationship, selectinload
from sqlalchemy.sql.expression import text

from .base import Base
from .category import Category


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
    # Let the database enforce product delete rules so SQLAlchemy does not try
    # to null out non-nullable product_id foreign keys first.
    order_items = relationship(
        "OrderItem", back_populates="product", passive_deletes="all"
    )
    cart_items = relationship(
        "CartItem", back_populates="product", passive_deletes="all"
    )


def _apply_product_filters(
    stmt: Select,
    *,
    product_id: UUID | None = None,
    category_id: UUID | None = None,
    search: str | None = None,
) -> Select:
    if product_id is not None:
        stmt = stmt.where(Product.id == product_id)
    if category_id is not None:
        stmt = stmt.where(Product.category_id == category_id)
    if search is not None:
        pattern = f"%{search}%"
        stmt = stmt.where(
            or_(Product.name.ilike(pattern), Product.description.ilike(pattern))
        )
    return stmt


def _apply_product_sort(stmt: Select, *, sort_by: str, order: str) -> Select:
    sort_column = {
        "name": Product.name,
        "category": Category.name,
        "price": Product.price,
        "stock": Product.stock,
        "created_at": Product.created_at,
    }[sort_by]
    if sort_by == "category":
        stmt = stmt.outerjoin(Category, Product.category_id == Category.id)
    direction = sort_column.desc() if order == "desc" else sort_column.asc()
    tie_breaker = Product.id.desc() if order == "desc" else Product.id.asc()
    return stmt.order_by(direction, tie_breaker)


def list_products(
    session: Session,
    product_id: UUID | None = None,
    category_id: UUID | None = None,
    search: str | None = None,
    skip: int = 0,
    limit: int = 20,
    sort_by: str = "name",
    order: str = "asc",
    load_category: bool = False,
    load_order_items: bool = False,
) -> tuple[list[Product], int]:
    stmt = select(Product)
    if load_category:
        stmt = stmt.options(selectinload(Product.category))
    if load_order_items:
        stmt = stmt.options(selectinload(Product.order_items))
    stmt = _apply_product_filters(
        stmt,
        product_id=product_id,
        category_id=category_id,
        search=search,
    )
    stmt = _apply_product_sort(stmt, sort_by=sort_by, order=order)
    stmt = stmt.offset(skip).limit(limit)

    count_stmt = _apply_product_filters(
        select(func.count(Product.id)),
        product_id=product_id,
        category_id=category_id,
        search=search,
    )

    items = session.scalars(stmt).all()
    total = session.scalar(count_stmt) or 0
    return items, total


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
    session.flush()
