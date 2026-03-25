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
            ProductFixture(
                name="Bluetooth Speaker",
                description="Portable waterproof speaker with 12-hour battery life.",
                price=59.99,
                stock=45,
                image_url="https://picsum.photos/id/60/800/800",
            ),
            ProductFixture(
                name="Wireless Keyboard",
                description="Slim mechanical keyboard with backlit keys and USB-C charging.",
                price=89.99,
                stock=30,
                image_url="https://picsum.photos/id/201/800/800",
            ),
            ProductFixture(
                name="USB-C Hub Adapter",
                description="7-in-1 hub with HDMI, USB 3.0, SD card reader and PD charging.",
                price=45.99,
                stock=50,
                image_url="https://picsum.photos/id/2/800/800",
            ),
            ProductFixture(
                name="Wireless Earbuds",
                description="True wireless earbuds with touch controls and 8-hour battery.",
                price=69.99,
                stock=60,
                image_url="https://picsum.photos/id/3/800/800",
            ),
            ProductFixture(
                name="Portable Charger",
                description="20000mAh power bank with dual USB-C ports and fast charging.",
                price=39.99,
                stock=70,
                image_url="https://picsum.photos/id/119/800/800",
            ),
        ),
    ),
    CategoryFixture(
        name="Home & Kitchen",
        products=(
            ProductFixture(
                name="Pour-Over Coffee Set",
                description="Glass dripper with reusable steel filter.",
                price=39.50,
                stock=40,
                image_url="https://picsum.photos/id/292/800/800",
            ),
            ProductFixture(
                name="Cast Iron Skillet",
                description="Pre-seasoned 10-inch skillet for stovetop and oven.",
                price=54.00,
                stock=18,
                image_url="https://picsum.photos/id/425/800/800",
            ),
            ProductFixture(
                name="Bamboo Cutting Board",
                description="Large organic bamboo board with juice groove.",
                price=29.99,
                stock=55,
                image_url="https://picsum.photos/id/312/800/800",
            ),
            ProductFixture(
                name="Stainless Steel Thermos",
                description="Double-wall vacuum insulated, keeps drinks hot 12 hours.",
                price=34.99,
                stock=60,
                image_url="https://picsum.photos/id/225/800/800",
            ),
            ProductFixture(
                name="Ceramic Mug Set",
                description="Set of 4 handmade 12oz mugs in earth-tone glazes.",
                price=28.00,
                stock=35,
                image_url="https://picsum.photos/id/30/800/800",
            ),
            ProductFixture(
                name="Electric Kettle",
                description="1.7L stainless steel kettle with temperature presets.",
                price=49.99,
                stock=22,
                image_url="https://picsum.photos/id/165/800/800",
            ),
        ),
    ),
    CategoryFixture(
        name="Clothing",
        products=(
            ProductFixture(
                name="Classic Denim Jacket",
                description="Timeless medium-wash denim jacket with brass buttons.",
                price=79.99,
                stock=20,
                image_url="https://picsum.photos/id/399/800/800",
            ),
            ProductFixture(
                name="Merino Wool Beanie",
                description="Soft, breathable beanie for all-season comfort.",
                price=24.99,
                stock=75,
                image_url="https://picsum.photos/id/355/800/800",
            ),
            ProductFixture(
                name="Canvas Sneakers",
                description="Lightweight low-top sneakers with vulcanized sole.",
                price=49.99,
                stock=35,
                image_url="https://picsum.photos/id/21/800/800",
            ),
            ProductFixture(
                name="Cotton Crew Socks (6-pack)",
                description="Breathable everyday socks with reinforced heel and toe.",
                price=14.99,
                stock=100,
                image_url="https://picsum.photos/id/325/800/800",
            ),
            ProductFixture(
                name="Linen Button-Down Shirt",
                description="Relaxed-fit linen shirt, perfect for warm weather.",
                price=59.99,
                stock=28,
                image_url="https://picsum.photos/id/334/800/800",
            ),
        ),
    ),
    CategoryFixture(
        name="Books",
        products=(
            ProductFixture(
                name="JavaScript: The Good Parts",
                description="Douglas Crockford's essential guide to JavaScript.",
                price=29.99,
                stock=50,
                image_url="https://picsum.photos/id/24/800/800",
            ),
            ProductFixture(
                name="Clean Code",
                description="Robert C. Martin's handbook of agile software craftsmanship.",
                price=34.99,
                stock=40,
                image_url="https://picsum.photos/id/367/800/800",
            ),
            ProductFixture(
                name="The Design of Everyday Things",
                description="Don Norman's classic on user-centered design principles.",
                price=19.99,
                stock=65,
                image_url="https://picsum.photos/id/380/800/800",
            ),
            ProductFixture(
                name="Pragmatic Programmer",
                description="Andy Hunt and Dave Thomas's tips for modern software development.",
                price=42.99,
                stock=30,
                image_url="https://picsum.photos/id/46/800/800",
            ),
            ProductFixture(
                name="Refactoring",
                description="Martin Fowler's guide to improving the design of existing code.",
                price=38.99,
                stock=25,
                image_url="https://picsum.photos/id/48/800/800",
            ),
        ),
    ),
    CategoryFixture(
        name="Sports & Outdoors",
        products=(
            ProductFixture(
                name="Yoga Mat",
                description="Extra-thick non-slip mat with carrying strap.",
                price=32.00,
                stock=40,
                image_url="https://picsum.photos/id/110/800/800",
            ),
            ProductFixture(
                name="Stainless Steel Water Bottle",
                description="1-liter insulated bottle, keeps cold 24 hours.",
                price=22.99,
                stock=80,
                image_url="https://picsum.photos/id/160/800/800",
            ),
            ProductFixture(
                name="Resistance Bands Set",
                description="5 latex bands with handles for home workouts, light to heavy.",
                price=18.99,
                stock=90,
                image_url="https://picsum.photos/id/116/800/800",
            ),
            ProductFixture(
                name="Hiking Backpack",
                description="35L daypack with rain cover and hydration sleeve.",
                price=64.99,
                stock=15,
                image_url="https://picsum.photos/id/129/800/800",
            ),
            ProductFixture(
                name="Camping Headlamp",
                description="Rechargeable LED headlamp, 600 lumens with red-light mode.",
                price=27.99,
                stock=45,
                image_url="https://picsum.photos/id/157/800/800",
            ),
        ),
    ),
    CategoryFixture(
        name="Office & Stationery",
        products=(
            ProductFixture(
                name="Hardcover Notebook",
                description="A5 dotted notebook with 192 pages and lay-flat binding.",
                price=12.99,
                stock=120,
                image_url="https://picsum.photos/id/68/800/800",
            ),
            ProductFixture(
                name="Desk Organizer",
                description="Walnut wood organizer with phone slot and pen holder.",
                price=34.99,
                stock=30,
                image_url="https://picsum.photos/id/82/800/800",
            ),
            ProductFixture(
                name="Gel Pen Set (10-pack)",
                description="Smooth-writing 0.5mm gel pens in assorted colors.",
                price=9.99,
                stock=150,
                image_url="https://picsum.photos/id/50/800/800",
            ),
            ProductFixture(
                name="Monitor Stand",
                description="Bamboo riser with storage drawer and cable management.",
                price=44.99,
                stock=20,
                image_url="https://picsum.photos/id/96/800/800",
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
