import os
from uuid import UUID

from dotenv import load_dotenv
from fastapi import Depends, FastAPI, HTTPException
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
import jwt

from request_schemas.schemas import (
    CreateCategoryRequest,
    CreateOrderItemRequest,
    CreateOrderRequest,
    CreateProductRequest,
    UpdateCategoryRequest,
    UpdateOrderItemRequest,
    UpdateOrderRequest,
    UpdateProductRequest,
    UpdateUserRequest,
)
from response_schemas.schemas import Category, Order, OrderItem, Product, User


load_dotenv()

AUTH0_DOMAIN = os.getenv("AUTH0_DOMAIN")
AUTH0_API_AUDIENCE = os.getenv("AUTH0_API_AUDIENCE")
AUTH0_ISSUER = os.getenv("AUTH0_ISSUER")

if not AUTH0_DOMAIN or not AUTH0_API_AUDIENCE or not AUTH0_ISSUER:
    raise RuntimeError(
        "Missing AUTH0_DOMAIN, AUTH0_API_AUDIENCE, or AUTH0_ISSUER environment variables."
    )


PERMISSION_TO_ROLES = {
    "read:category": {"admin"},
    "create:category": {"admin"},
    "update:category": {"admin"},
    "delete:category": {"admin"},
    "read:product": {"admin"},
    "create:product": {"admin"},
    "update:product": {"admin"},
    "delete:product": {"admin"},
    "read:order": {"admin"},
    "create:order": {"admin", "customer"},
    "update:order": {"admin"},
    "delete:order": {"admin"},
    "read:order_item": {"admin"},
    "create:order_item": {"admin"},
    "update:order_item": {"admin"},
    "delete:order_item": {"admin"},
    "read:user": {"admin", "customer"},
    "update:user": {"admin"},
    "delete:user": {"admin"},
}


security = HTTPBearer()


def _extract_roles(payload: dict) -> list[str]:
    roles = payload.get("roles") or payload.get(f"https://{AUTH0_DOMAIN}/roles") or []
    if isinstance(roles, str):
        roles = [roles]
    return [role for role in roles if isinstance(role, str)]


def _decode_token(token: str) -> dict:
    jwks_client = jwt.PyJWKClient(f"https://{AUTH0_DOMAIN}/.well-known/jwks.json")
    signing_key = jwks_client.get_signing_key_from_jwt(token).key
    try:
        return jwt.decode(
            token,
            signing_key,
            algorithms=["RS256"],
            audience=AUTH0_API_AUDIENCE,
            issuer=AUTH0_ISSUER,
        )
    except jwt.PyJWTError as exc:
        raise HTTPException(status_code=401, detail="Invalid token") from exc


def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(security),
) -> dict:
    payload = _decode_token(credentials.credentials)
    roles = _extract_roles(payload)
    if not roles:
        raise HTTPException(
            status_code=403,
            detail="No roles found. Add roles to the token via an Auth0 Action.",
        )

    role = "admin" if "admin" in roles else "customer"
    if role not in {"admin", "customer"}:
        raise HTTPException(status_code=403, detail="Unsupported role.")

    # TODO: Replace with DB lookup by auth0_sub when persistence is added.
    return {
        "id": None,
        "auth0_sub": payload.get("sub"),
        "created_at": None,
        "role": role,
    }


def require_permission(permission: str):
    def checker(user: dict = Depends(get_current_user)) -> dict:
        if user["role"] == "admin":
            return user

        allowed_roles = PERMISSION_TO_ROLES.get(permission, set())
        if user["role"] not in allowed_roles:
            raise HTTPException(status_code=403, detail="Forbidden")
        return user

    return checker


app = FastAPI()


@app.get("/health")
def health() -> dict:
    return {"status": "ok"}


@app.get("/products", response_model=list[Product])
def list_products(
    user: dict = Depends(require_permission("read:product")),
):
    pass


@app.get("/products/{product_id}", response_model=Product)
def get_product(
    product_id: UUID,
    user: dict = Depends(require_permission("read:product")),
):
    pass


@app.post("/products", response_model=Product)
def create_product(
    payload: CreateProductRequest,
    user: dict = Depends(require_permission("create:product")),
):
    pass


@app.put("/products/{product_id}", response_model=Product)
def update_product(
    product_id: UUID,
    payload: UpdateProductRequest,
    user: dict = Depends(require_permission("update:product")),
):
    pass


@app.delete("/products/{product_id}", response_model=dict)
def delete_product(
    product_id: UUID,
    user: dict = Depends(require_permission("delete:product")),
):
    pass


@app.get("/categories", response_model=list[Category])
def list_categories(
    user: dict = Depends(require_permission("read:category")),
):
    pass


@app.get("/categories/{category_id}", response_model=Category)
def get_category(
    category_id: UUID,
    user: dict = Depends(require_permission("read:category")),
):
    pass


@app.post("/categories", response_model=Category)
def create_category(
    payload: CreateCategoryRequest,
    user: dict = Depends(require_permission("create:category")),
):
    pass


@app.put("/categories/{category_id}", response_model=Category)
def update_category(
    category_id: UUID,
    payload: UpdateCategoryRequest,
    user: dict = Depends(require_permission("update:category")),
):
    pass


@app.delete("/categories/{category_id}", response_model=dict)
def delete_category(
    category_id: UUID,
    user: dict = Depends(require_permission("delete:category")),
):
    pass


@app.get("/orders", response_model=list[Order])
def list_orders(user: dict = Depends(require_permission("read:order"))):
    pass


@app.get("/orders/{order_id}", response_model=Order)
def get_order(
    order_id: UUID,
    user: dict = Depends(require_permission("read:order")),
):
    pass


@app.post("/orders", response_model=Order)
def create_order(
    payload: CreateOrderRequest,
    user: dict = Depends(require_permission("create:order")),
):
    pass


@app.put("/orders/{order_id}", response_model=Order)
def update_order(
    order_id: UUID,
    payload: UpdateOrderRequest,
    user: dict = Depends(require_permission("update:order")),
):
    pass


@app.delete("/orders/{order_id}", response_model=dict)
def delete_order(
    order_id: UUID,
    user: dict = Depends(require_permission("delete:order")),
):
    pass


@app.get("/order-items", response_model=list[OrderItem])
def list_order_items(
    user: dict = Depends(require_permission("read:order_item")),
):
    pass


@app.get("/order-items/{order_item_id}", response_model=OrderItem)
def get_order_item(
    order_item_id: UUID,
    user: dict = Depends(require_permission("read:order_item")),
):
    pass


@app.post("/order-items", response_model=OrderItem)
def create_order_item(
    payload: CreateOrderItemRequest,
    user: dict = Depends(require_permission("create:order_item")),
):
    pass


@app.put("/order-items/{order_item_id}", response_model=OrderItem)
def update_order_item(
    order_item_id: UUID,
    payload: UpdateOrderItemRequest,
    user: dict = Depends(require_permission("update:order_item")),
):
    pass


@app.delete("/order-items/{order_item_id}", response_model=dict)
def delete_order_item(
    order_item_id: UUID,
    user: dict = Depends(require_permission("delete:order_item")),
):
    pass


@app.get("/users", response_model=list[User])
def list_users(
    user: dict = Depends(require_permission("read:user")),
):
    pass


@app.get("/users/{user_id}", response_model=User)
def get_user(
    user_id: UUID,
    user: dict = Depends(require_permission("read:user")),
):
    pass


@app.put("/users/{user_id}", response_model=User)
def update_user(
    user_id: UUID,
    payload: UpdateUserRequest,
    user: dict = Depends(require_permission("update:user")),
):
    pass


@app.delete("/users/{user_id}", response_model=dict)
def delete_user(
    user_id: UUID,
    user: dict = Depends(require_permission("delete:user")),
):
    pass


if __name__ == "__main__":
    import uvicorn

    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)


# docker
# renderer
# railway(backend)
# vercel(frontend)
# neon(database)
# https://chatgpt.com/?utm_source=google&utm_medium=paid_search&utm_campaign=GOOG_C_SEM_GBR_Core_CHT_BAU_ACQ_PER_MIX_ALL_NAMER_CA_EN_032525&c_id=22376911868&c_agid=175413814965&c_crid=741707849652&c_kwid={keywordid}&c_ims=&c_pms=9001561&c_nw=g&c_dvc=c&gad_source=1&gad_campaignid=22376911868&gbraid=0AAAAA-I0E5fRL-dMmHWymBIoX3AVN4RG_&gclid=Cj0KCQiAp-zLBhDkARIsABcYc6tpRzbLXila7Wilt5Xw3aDSY8xcWa4hm4htbisnLjKHkU9cksHQp48aAsNKEALw_wcB
