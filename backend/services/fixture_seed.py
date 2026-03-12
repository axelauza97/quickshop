import os
from collections.abc import Sequence
from dataclasses import dataclass

from sqlalchemy import select
from sqlalchemy.orm import Session

from models.db.category import Category
from models.db.product import Product


@dataclass(frozen=True)
class ProductFixture:
    name: str
    description: str
    price: float
    stock: int
    image_url: str


@dataclass(frozen=True)
class CategoryFixture:
    name: str
    products: tuple[ProductFixture, ...]


FIXTURE_CATALOG: tuple[CategoryFixture, ...] = (
    CategoryFixture(
        name="Electronics",
        products=(
            ProductFixture(
                name="Noise-Canceling Headphones",
                description="Over-ear wireless headphones with ANC.",
                price=149.99,
                stock=25,
                image_url="https://picsum.photos/id/180/800/800",
            ),
            ProductFixture(
                name="4K Action Camera",
                description="Compact camera for travel and outdoor clips.",
                price=219.0,
                stock=12,
                image_url="https://picsum.photos/id/250/800/800",
            ),
        ),
    ),
    CategoryFixture(
        name="Home & Kitchen",
        products=(
            ProductFixture(
                name="Pour-Over Coffee Set",
                description="Glass dripper with reusable steel filter.",
                price=39.5,
                stock=40,
                image_url="https://picsum.photos/id/292/800/800",
            ),
            ProductFixture(
                name="Cast Iron Skillet",
                description="Pre-seasoned 10-inch skillet for stovetop and oven.",
                price=54.0,
                stock=18,
                image_url="https://picsum.photos/id/425/800/800",
            ),
        ),
    ),
)

def is_fixture_seeding_enabled() -> bool:
    value = os.getenv("SEED_FIXTURES", "")
    return value.strip().lower() == "true"


def seed_catalog_fixtures(
    session: Session, catalog: Sequence[CategoryFixture] = FIXTURE_CATALOG
) -> dict[str, int]:
    category_count = 0
    product_count = 0

    for category_fixture in catalog:
        category = session.scalar(
            select(Category).where(Category.name == category_fixture.name)
        )
        if category is None:
            category = Category(name=category_fixture.name)
            session.add(category)
            session.flush()
            category_count += 1

        for product_fixture in category_fixture.products:
            product = session.scalar(
                select(Product).where(
                    Product.category_id == category.id,
                    Product.name == product_fixture.name,
                )
            )
            if product is None:
                product = Product(
                    name=product_fixture.name,
                    description=product_fixture.description,
                    price=product_fixture.price,
                    stock=product_fixture.stock,
                    image_url=product_fixture.image_url,
                    category_id=category.id,
                )
                session.add(product)
                session.flush()
                product_count += 1
            else:
                product.description = product_fixture.description
                product.price = product_fixture.price
                product.stock = product_fixture.stock
                product.image_url = product_fixture.image_url
                session.flush()

    return {"categories_created": category_count, "products_created": product_count}


def maybe_seed_catalog_fixtures(
    session: Session,
    enabled: bool | None = None,
    catalog: Sequence[CategoryFixture] = FIXTURE_CATALOG,
) -> bool:
    should_seed = is_fixture_seeding_enabled() if enabled is None else enabled
    if not should_seed:
        return False
    seed_catalog_fixtures(session, catalog)
    return True