import uuid
from uuid import UUID

from sqlalchemy import DateTime, String, func, select
from sqlalchemy.dialects.postgresql import UUID as PSQL_UUID
from sqlalchemy.orm import Session, mapped_column, relationship, selectinload

from .base import Base


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


def list_categories(
    session: Session,
    category_id: UUID | None = None,
    load_products: bool = False,
) -> list[Category]:
    stmt = select(Category)
    if load_products:
        stmt = stmt.options(selectinload(Category.products))
    if category_id is not None:
        stmt = stmt.where(Category.id == category_id)
    return session.scalars(stmt).all()


def get_category_by_id(session: Session, category_id: UUID) -> Category | None:
    return session.scalar(select(Category).where(Category.id == category_id))


def create_category(session: Session, values: dict) -> Category:
    category = Category(**values)
    session.add(category)
    session.flush()
    return category


def update_category(
    session: Session,
    category_id: UUID,
    *,
    name: str,
) -> Category:
    category = get_category_by_id(session, category_id)
    if category is None:
        raise ValueError(f"Category not found: {category_id}")

    category.name = name

    session.flush()
    return category


def delete_category(session: Session, category: Category) -> None:
    session.delete(category)
    session.flush()
