from __future__ import annotations

from typing import Optional
from uuid import UUID

from pydantic import BaseModel


class CreateProductRequest(BaseModel):
    name: str
    description: Optional[str] = None
    price: float
    category_id: UUID
    stock: int = 0


class UpdateProductRequest(BaseModel):
    name: Optional[str] = None
    description: Optional[str] = None
    price: Optional[float] = None
    category_id: Optional[UUID] = None
    stock: Optional[int] = None


class CreateCategoryRequest(BaseModel):
    name: str


class UpdateCategoryRequest(BaseModel):
    name: Optional[str] = None


class CreateOrderRequest(BaseModel):
    user_id: UUID
    total_amount: float


class UpdateOrderRequest(BaseModel):
    total_amount: Optional[float] = None


class CreateOrderItemRequest(BaseModel):
    order_id: UUID
    product_id: UUID
    quantity: int
    price_at_purchase: float


class UpdateOrderItemRequest(BaseModel):
    quantity: Optional[int] = None
    price_at_purchase: Optional[float] = None


class UpdateUserRequest(BaseModel):
    auth0_sub: Optional[str] = None
