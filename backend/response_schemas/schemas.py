from datetime import datetime
from typing import List, Optional
from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field


class Product(BaseModel):
    id: UUID
    name: str
    description: Optional[str] = None
    price: float
    category_id: UUID
    stock: int
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)


class Category(BaseModel):
    id: UUID
    name: str
    created_at: datetime
    products: List[Product] = Field(default_factory=list)

    model_config = ConfigDict(from_attributes=True)


class User(BaseModel):
    id: UUID
    auth0_sub: str
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
    created_at: datetime
    order_items: List[OrderItem] = Field(default_factory=list)

    model_config = ConfigDict(from_attributes=True)


class ProductsResponseSchema(BaseModel):
    products: List[Product]


class CategoriesResponseSchema(BaseModel):
    categories: List[Category]


class UsersResponseSchema(BaseModel):
    users: List[User]


class OrdersResponseSchema(BaseModel):
    orders: List[Order]


class OrderItemsResponseSchema(BaseModel):
    order_items: List[OrderItem]
