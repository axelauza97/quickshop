from uuid import UUID

from pydantic import BaseModel


class CreateProductRequest(BaseModel):
    name: str
    description: str | None = None
    price: float
    category_id: UUID
    stock: int = 0
    image_url: str | None = None


class UpdateProductRequest(BaseModel):
    name: str | None = None
    description: str | None = None
    price: float | None = None
    category_id: UUID | None = None
    stock: int | None = None
    image_url: str | None = None


class CreateCategoryRequest(BaseModel):
    name: str


class UpdateCategoryRequest(BaseModel):
    name: str | None = None


class UpdateOrderRequest(BaseModel):
    total_amount: float | None = None
    status: str | None = None


class CreateOrderItemRequest(BaseModel):
    order_id: UUID
    product_id: UUID
    quantity: int
    price_at_purchase: float


class UpdateOrderItemRequest(BaseModel):
    quantity: int | None = None
    price_at_purchase: float | None = None


class AddCartItemRequest(BaseModel):
    product_id: UUID
    quantity: int = 1


class UpdateCartItemRequest(BaseModel):
    quantity: int


class CheckoutRequest(BaseModel):
    shipping_address: str | None = None
