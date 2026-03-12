import uuid
from uuid import UUID

from sqlalchemy import Boolean, DateTime, String, func, select
from sqlalchemy.dialects.postgresql import UUID as PSQL_UUID
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session, mapped_column, relationship, selectinload
from sqlalchemy.sql.expression import text

from .base import Base


class User(Base):
    __tablename__ = "user"

    id = mapped_column(PSQL_UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    auth0_sub = mapped_column(String, unique=True, nullable=False)
    is_admin = mapped_column(Boolean, nullable=False, server_default=text("false"))
    created_at = mapped_column(
        DateTime(timezone=True), nullable=False, default=func.now()
    )
    orders = relationship("Order", back_populates="user", cascade="all, delete-orphan")
    cart_items = relationship("CartItem", back_populates="user", cascade="all, delete-orphan")


def list_users(
    session: Session,
    user_id: UUID | None = None,
    auth0_sub: str | None = None,
    load_orders: bool = False,
) -> list[User]:
    stmt = select(User)
    if load_orders:
        stmt = stmt.options(selectinload(User.orders))
    if user_id is not None:
        stmt = stmt.where(User.id == user_id)
    if auth0_sub is not None:
        stmt = stmt.where(User.auth0_sub == auth0_sub)
    return session.scalars(stmt).all()


def get_user_by_id(session: Session, user_id: UUID) -> User | None:
    return session.scalar(select(User).where(User.id == user_id))


def get_user_by_auth0_sub(session: Session, auth0_sub: str) -> User | None:
    return session.scalar(select(User).where(User.auth0_sub == auth0_sub))


def create_user(session: Session, auth0_sub: str) -> User:
    user = User(auth0_sub=auth0_sub)
    session.add(user)
    session.flush()
    return user


def get_or_create_user_by_auth0_sub(session: Session, auth0_sub: str) -> User:
    existing = get_user_by_auth0_sub(session, auth0_sub)
    if existing is not None:
        return existing

    user = User(auth0_sub=auth0_sub)
    session.add(user)
    try:
        session.flush()
    except IntegrityError:
        session.rollback()
        race_winner = get_user_by_auth0_sub(session, auth0_sub)
        if race_winner is not None:
            return race_winner
        raise

    session.refresh(user)
    return user


def update_user(
    session: Session,
    user_id: UUID,
    *,
    is_admin: bool,
) -> User:
    user = get_user_by_id(session, user_id)
    if user is None:
        raise ValueError(f"User not found: {user_id}")

    user.is_admin = is_admin

    session.flush()
    return user


def delete_user(session: Session, user: User) -> None:
    session.delete(user)
