from datetime import datetime
from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field


class Product(BaseModel):
    id: UUID
    name: str
    description: str | None = None
    price: float
    category_id: UUID
    stock: int
    image_url: str | None = None
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)


class Category(BaseModel):
    id: UUID
    name: str
    created_at: datetime
    products: list[Product] = Field(default_factory=list)

    model_config = ConfigDict(from_attributes=True)


class User(BaseModel):
    id: UUID
    auth0_sub: str
    is_admin: bool
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)


class OrderItem(BaseModel):
    id: UUID
    order_id: UUID
    product_id: UUID
    quantity: int
    price_at_purchase: float
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)


class Order(BaseModel):
    id: UUID
    user_id: UUID
    total_amount: float
    status: str
    created_at: datetime
    order_items: list[OrderItem] = Field(default_factory=list)

    model_config = ConfigDict(from_attributes=True)


class CartItemResponse(BaseModel):
    id: UUID
    product_id: UUID
    quantity: int
    created_at: datetime
    product: Product | None = None

    model_config = ConfigDict(from_attributes=True)


class CartResponse(BaseModel):
    items: list[CartItemResponse]
    total: float


class CheckoutResponse(BaseModel):
    order: Order
    message: str = "Order placed successfully"
