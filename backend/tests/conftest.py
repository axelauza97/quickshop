import sys
import uuid
from collections.abc import Iterator
from datetime import datetime, timezone
from pathlib import Path

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import Session, sessionmaker
from sqlalchemy.pool import StaticPool

BACKEND_DIR = Path(__file__).resolve().parents[1]
if str(BACKEND_DIR) not in sys.path:
    sys.path.insert(0, str(BACKEND_DIR))


import main as _main_module

_main_module._initialize_app_state = lambda: None  # skip DB init during tests

from auth import get_current_user
from main import app
from models.db.base import Base
from models.db.category import Category
from models.db.order import Order
from models.db.order_item import OrderItem
from models.db.product import Product
from models.db.session import get_session
from models.db.user import User


TEST_DATABASE_URL = "sqlite+pysqlite:///:memory:"


@pytest.fixture(scope="session")
def test_engine():
    engine = create_engine(
        TEST_DATABASE_URL,
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
    )
    yield engine
    engine.dispose()


@pytest.fixture(scope="session")
def session_factory(test_engine):
    return sessionmaker(bind=test_engine, autoflush=False, autocommit=False)


@pytest.fixture(autouse=True)
def reset_schema(test_engine):
    Base.metadata.drop_all(bind=test_engine)
    Base.metadata.create_all(bind=test_engine)
    yield
    Base.metadata.drop_all(bind=test_engine)


@pytest.fixture
def auth_context():
    now = datetime.now(timezone.utc)
    user_id = uuid.uuid4()
    return {
        "id": user_id,
        "auth0_sub": f"auth0|{user_id}",
        "created_at": now,
        "role": "admin",
    }


@pytest.fixture
def set_actor(auth_context):
    def _set(user_id: uuid.UUID, role: str, auth0_sub: str | None = None) -> None:
        auth_context["id"] = user_id
        auth_context["role"] = role
        auth_context["auth0_sub"] = auth0_sub or f"auth0|{user_id}"
        auth_context["created_at"] = datetime.now(timezone.utc)

    return _set


@pytest.fixture
def client(session_factory, auth_context):
    def override_get_session() -> Iterator[Session]:
        session = session_factory()
        try:
            yield session
            session.commit()
        except Exception:
            session.rollback()
            raise
        finally:
            session.close()

    def override_current_user() -> dict:
        return auth_context

    app.dependency_overrides[get_session] = override_get_session
    app.dependency_overrides[get_current_user] = override_current_user

    with TestClient(app) as test_client:
        yield test_client

    app.dependency_overrides.clear()


@pytest.fixture
def seed_user(session_factory):
    def _seed(*, user_id: uuid.UUID, auth0_sub: str, is_admin: bool) -> dict:
        with session_factory() as session:
            user = User(id=user_id, auth0_sub=auth0_sub, is_admin=is_admin)
            session.add(user)
            session.commit()
            session.refresh(user)
            return {"id": user.id, "auth0_sub": user.auth0_sub, "is_admin": user.is_admin}

    return _seed


@pytest.fixture
def seed_category(session_factory):
    def _seed(*, name: str) -> dict:
        with session_factory() as session:
            category = Category(name=name)
            session.add(category)
            session.commit()
            session.refresh(category)
            return {"id": category.id, "name": category.name}

    return _seed


@pytest.fixture
def seed_product(session_factory):
    def _seed(
        *,
        name: str,
        category_id: uuid.UUID,
        price: float = 10.0,
        stock: int = 10,
        description: str | None = None,
        image_url: str | None = None,
    ) -> dict:
        with session_factory() as session:
            product = Product(
                name=name,
                description=description,
                price=price,
                category_id=category_id,
                stock=stock,
                image_url=image_url,
            )
            session.add(product)
            session.commit()
            session.refresh(product)
            return {
                "id": product.id,
                "name": product.name,
                "category_id": product.category_id,
                "price": product.price,
                "stock": product.stock,
            }

    return _seed


@pytest.fixture
def seed_order(session_factory):
    def _seed(
        *,
        user_id: uuid.UUID,
        total_amount: float = 50.0,
        status: str = "confirmed",
    ) -> dict:
        with session_factory() as session:
            order = Order(user_id=user_id, total_amount=total_amount, status=status)
            session.add(order)
            session.commit()
            session.refresh(order)
            return {
                "id": order.id,
                "user_id": order.user_id,
                "total_amount": order.total_amount,
                "status": order.status,
            }

    return _seed


@pytest.fixture
def seed_order_item(session_factory):
    def _seed(
        *,
        order_id: uuid.UUID,
        product_id: uuid.UUID,
        quantity: int = 1,
        price_at_purchase: float = 10.0,
    ) -> dict:
        with session_factory() as session:
            order_item = OrderItem(
                order_id=order_id,
                product_id=product_id,
                quantity=quantity,
                price_at_purchase=price_at_purchase,
            )
            session.add(order_item)
            session.commit()
            session.refresh(order_item)
            return {
                "id": order_item.id,
                "order_id": order_item.order_id,
                "product_id": order_item.product_id,
            }

    return _seed


@pytest.fixture
def create_admin_and_customers(seed_user):
    def _create() -> dict:
        admin_id = uuid.uuid4()
        customer_a_id = uuid.uuid4()
        customer_b_id = uuid.uuid4()

        seed_user(user_id=admin_id, auth0_sub="auth0|admin", is_admin=True)
        seed_user(user_id=customer_a_id, auth0_sub="auth0|customer-a", is_admin=False)
        seed_user(user_id=customer_b_id, auth0_sub="auth0|customer-b", is_admin=False)

        return {
            "admin_id": admin_id,
            "customer_a_id": customer_a_id,
            "customer_b_id": customer_b_id,
        }

    return _create


@pytest.fixture
def users(create_admin_and_customers):
    return create_admin_and_customers()


@pytest.fixture
def act_as(users, set_actor):
    def _act_as(actor: str) -> None:
        actors = {
            "admin": (
                users["admin_id"],
                "admin",
                "auth0|admin",
            ),
            "customer_a": (
                users["customer_a_id"],
                "customer",
                "auth0|customer-a",
            ),
            "customer_b": (
                users["customer_b_id"],
                "customer",
                "auth0|customer-b",
            ),
        }

        if actor not in actors:
            raise ValueError(f"Unknown actor '{actor}'")

        user_id, role, auth0_sub = actors[actor]
        set_actor(user_id=user_id, role=role, auth0_sub=auth0_sub)

    return _act_as


@pytest.fixture
def create_category(client):
    def _create(name: str) -> dict:
        response = client.post("/categories/", json={"name": name})
        assert response.status_code == 200
        return response.json()

    return _create


@pytest.fixture
def create_product(client):
    def _create(
        *,
        name: str,
        category_id: str,
        price: float = 10.0,
        stock: int = 10,
        description: str | None = None,
        image_url: str | None = None,
    ) -> dict:
        response = client.post(
            "/products/",
            json={
                "name": name,
                "description": description,
                "price": price,
                "category_id": category_id,
                "stock": stock,
                "image_url": image_url,
            },
        )
        assert response.status_code == 200
        return response.json()

    return _create
