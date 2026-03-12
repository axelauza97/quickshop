

import uuid


def test_category_workflow_crud(client, users, act_as):
    act_as("admin")

    create_resp = client.post("/categories/", json={"name": "Electronics"})
    assert create_resp.status_code == 200
    created = create_resp.json()

    get_resp = client.get(f"/categories/{created['id']}")
    assert get_resp.status_code == 200
    assert get_resp.json()["name"] == "Electronics"

    list_resp = client.get("/categories/")
    assert list_resp.status_code == 200
    assert any(category["id"] == created["id"] for category in list_resp.json())

    update_resp = client.put(f"/categories/{created['id']}", json={"name": "Gadgets"})
    assert update_resp.status_code == 200
    assert update_resp.json()["name"] == "Gadgets"

    delete_resp = client.delete(f"/categories/{created['id']}")
    assert delete_resp.status_code == 200
    assert delete_resp.json()["deleted"] is True

    missing_resp = client.get(f"/categories/{created['id']}")
    assert missing_resp.status_code == 404


def test_product_workflow_crud_search_and_invalid_category(
    client, users, act_as, create_category
):
    act_as("admin")

    category = create_category("Phones")

    bad_category_resp = client.post(
        "/products/",
        json={
            "name": "Ghost Product",
            "description": "Should fail",
            "price": 99.0,
            "category_id": str(uuid.uuid4()),
            "stock": 5,
            "image_url": None,
        },
    )
    assert bad_category_resp.status_code == 400
    assert "Invalid category_id" in bad_category_resp.json()["detail"]

    create_resp = client.post(
        "/products/",
        json={
            "name": "Phone X",
            "description": "Flagship",
            "price": 999.99,
            "category_id": category["id"],
            "stock": 20,
            "image_url": None,
        },
    )
    assert create_resp.status_code == 200
    created = create_resp.json()

    get_resp = client.get(f"/products/{created['id']}")
    assert get_resp.status_code == 200
    assert get_resp.json()["name"] == "Phone X"

    list_resp = client.get("/products/")
    assert list_resp.status_code == 200
    assert any(product["id"] == created["id"] for product in list_resp.json())

    search_resp = client.get("/products/", params={"search": "phone"})
    assert search_resp.status_code == 200
    assert any(product["id"] == created["id"] for product in search_resp.json())

    update_resp = client.put(
        f"/products/{created['id']}",
        json={"stock": 7, "price": 899.99},
    )
    assert update_resp.status_code == 200
    updated = update_resp.json()
    assert updated["stock"] == 7
    assert updated["price"] == 899.99

    delete_resp = client.delete(f"/products/{created['id']}")
    assert delete_resp.status_code == 200
    assert delete_resp.json()["deleted"] is True

    missing_resp = client.get(f"/products/{created['id']}")
    assert missing_resp.status_code == 404


def test_cart_workflow_add_update_delete_and_total(
    client, users, act_as, create_category, create_product
):
    act_as("admin")

    category = create_category("Cart Category")
    product = create_product(
        name="Cart Product",
        category_id=category["id"],
        price=10.0,
        stock=10,
    )

    act_as("customer_a")

    empty_cart_resp = client.get("/cart/")
    assert empty_cart_resp.status_code == 200
    assert empty_cart_resp.json() == {"items": [], "total": 0}

    add_resp = client.post(
        "/cart/items",
        json={"product_id": product["id"], "quantity": 2},
    )
    assert add_resp.status_code == 200
    assert add_resp.json()["quantity"] == 2

    add_again_resp = client.post(
        "/cart/items",
        json={"product_id": product["id"], "quantity": 1},
    )
    assert add_again_resp.status_code == 200
    assert add_again_resp.json()["quantity"] == 3

    cart_resp = client.get("/cart/")
    assert cart_resp.status_code == 200
    assert cart_resp.json()["total"] == 30.0

    update_resp = client.put(
        f"/cart/items/{product['id']}",
        json={"quantity": 5},
    )
    assert update_resp.status_code == 200
    assert update_resp.json()["quantity"] == 5

    delete_via_update_resp = client.put(
        f"/cart/items/{product['id']}",
        json={"quantity": 0},
    )
    assert delete_via_update_resp.status_code == 200
    assert delete_via_update_resp.json()["product_id"] == product["id"]
    assert delete_via_update_resp.json()["quantity"] == 0

    final_cart_resp = client.get("/cart/")
    assert final_cart_resp.status_code == 200
    assert final_cart_resp.json() == {"items": [], "total": 0}


def test_cart_workflow_remove_and_clear(
    client, users, act_as, create_category, create_product
):
    act_as("admin")

    category = create_category("Cart Actions")
    product_one = create_product(
        name="Item One",
        category_id=category["id"],
        price=4.0,
        stock=10,
    )
    product_two = create_product(
        name="Item Two",
        category_id=category["id"],
        price=6.0,
        stock=10,
    )

    act_as("customer_a")
    client.post("/cart/items", json={"product_id": product_one["id"], "quantity": 1})
    client.post("/cart/items", json={"product_id": product_two["id"], "quantity": 2})

    remove_resp = client.delete(f"/cart/items/{product_one['id']}")
    assert remove_resp.status_code == 200
    assert remove_resp.json()["deleted"] is True

    cart_after_remove = client.get("/cart/")
    assert cart_after_remove.status_code == 200
    assert len(cart_after_remove.json()["items"]) == 1

    clear_resp = client.delete("/cart/")
    assert clear_resp.status_code == 200
    assert clear_resp.json()["cleared"] is True

    cart_after_clear = client.get("/cart/")
    assert cart_after_clear.status_code == 200
    assert cart_after_clear.json() == {"items": [], "total": 0}


def test_checkout_empty_cart_returns_400(client, users, act_as):
    act_as("customer_a")

    checkout_resp = client.post("/checkout", json={})
    assert checkout_resp.status_code == 400
    assert checkout_resp.json()["detail"] == "Cart is empty"


def test_checkout_success_creates_order_and_clears_cart(
    client, users, act_as, create_category, create_product
):
    act_as("admin")

    category = create_category("Checkout Category")
    product = create_product(
        name="Checkout Product",
        category_id=category["id"],
        price=12.5,
        stock=5,
    )

    act_as("customer_a")
    add_resp = client.post(
        "/cart/items",
        json={"product_id": product["id"], "quantity": 2},
    )
    assert add_resp.status_code == 200

    checkout_resp = client.post(
        "/checkout",
        json={"shipping_address": "123 Test St"},
    )
    assert checkout_resp.status_code == 200
    checkout_body = checkout_resp.json()
    assert checkout_body["message"] == "Order placed successfully"
    order_id = checkout_body["order"]["id"]

    cart_resp = client.get("/cart/")
    assert cart_resp.status_code == 200
    assert cart_resp.json() == {"items": [], "total": 0}

    order_resp = client.get(f"/orders/{order_id}")
    assert order_resp.status_code == 200
    order_data = order_resp.json()
    assert order_data["user_id"] == str(users["customer_a_id"])
    assert order_data["total_amount"] == 25.0
    assert len(order_data["order_items"]) == 1
    assert order_data["order_items"][0]["quantity"] == 2

    act_as("admin")
    product_resp = client.get(f"/products/{product['id']}")
    assert product_resp.status_code == 200
    assert product_resp.json()["stock"] == 3


def test_checkout_insufficient_stock_returns_400(
    client, users, act_as, create_category, create_product
):
    act_as("admin")

    category = create_category("Stock Race")
    product = create_product(
        name="Stocked Product",
        category_id=category["id"],
        price=7.0,
        stock=1,
    )

    act_as("customer_a")
    add_resp = client.post(
        "/cart/items",
        json={"product_id": product["id"], "quantity": 1},
    )
    assert add_resp.status_code == 200

    act_as("admin")
    update_stock_resp = client.put(f"/products/{product['id']}", json={"stock": 0})
    assert update_stock_resp.status_code == 200

    act_as("customer_a")
    checkout_resp = client.post("/checkout", json={})
    assert checkout_resp.status_code == 400
    assert "Insufficient stock" in checkout_resp.json()["detail"]


def test_orders_visibility_and_forbidden_access(
    client, users, act_as, seed_order
):
    order_a = seed_order(user_id=users["customer_a_id"], total_amount=40.0, status="confirmed")
    order_b = seed_order(user_id=users["customer_b_id"], total_amount=60.0, status="confirmed")

    act_as("customer_a")
    customer_orders_resp = client.get("/orders")
    assert customer_orders_resp.status_code == 200
    customer_orders = customer_orders_resp.json()
    assert len(customer_orders) == 1
    assert customer_orders[0]["id"] == str(order_a["id"])

    forbidden_resp = client.get(f"/orders/{order_b['id']}")
    assert forbidden_resp.status_code == 403

    act_as("admin")
    admin_orders_resp = client.get("/orders")
    assert admin_orders_resp.status_code == 200
    admin_order_ids = {order["id"] for order in admin_orders_resp.json()}
    assert str(order_a["id"]) in admin_order_ids
    assert str(order_b["id"]) in admin_order_ids


def test_orders_update_validation_and_delete(
    client, users, act_as, seed_order
):
    order = seed_order(user_id=users["customer_a_id"], total_amount=30.0, status="confirmed")

    act_as("admin")

    update_resp = client.put(f"/orders/{order['id']}", json={"status": "shipped"})
    assert update_resp.status_code == 200
    assert update_resp.json()["status"] == "shipped"

    invalid_status_resp = client.put(
        f"/orders/{order['id']}",
        json={"status": "not-a-real-status"},
    )
    assert invalid_status_resp.status_code == 400
    assert "Invalid status" in invalid_status_resp.json()["detail"]

    delete_resp = client.delete(f"/orders/{order['id']}")
    assert delete_resp.status_code == 200
    assert delete_resp.json()["deleted"] is True

    get_deleted_resp = client.get(f"/orders/{order['id']}")
    assert get_deleted_resp.status_code == 404


def test_order_items_crud_workflow(
    client,
    users, act_as,
    seed_category,
    seed_product,
    seed_order,
):
    category = seed_category(name="Order Items")
    product = seed_product(
        name="Orderable Product",
        category_id=category["id"],
        price=15.0,
        stock=12,
    )
    order = seed_order(user_id=users["customer_a_id"], total_amount=15.0, status="confirmed")

    act_as("admin")

    create_resp = client.post(
        "/order-items",
        json={
            "order_id": str(order["id"]),
            "product_id": str(product["id"]),
            "quantity": 2,
            "price_at_purchase": 15.0,
        },
    )
    assert create_resp.status_code == 200
    order_item = create_resp.json()

    list_resp = client.get("/order-items")
    assert list_resp.status_code == 200
    assert any(item["id"] == order_item["id"] for item in list_resp.json())

    get_resp = client.get(f"/order-items/{order_item['id']}")
    assert get_resp.status_code == 200
    assert get_resp.json()["quantity"] == 2

    update_resp = client.put(
        f"/order-items/{order_item['id']}",
        json={"quantity": 5},
    )
    assert update_resp.status_code == 200
    assert update_resp.json()["quantity"] == 5

    delete_resp = client.delete(f"/order-items/{order_item['id']}")
    assert delete_resp.status_code == 200
    assert delete_resp.json()["deleted"] is True

    missing_resp = client.get(f"/order-items/{order_item['id']}")
    assert missing_resp.status_code == 404


def test_order_items_invalid_foreign_keys_and_missing(
    client,
    users, act_as,
    seed_category,
    seed_product,
    seed_order,
):
    category = seed_category(name="FK Category")
    product = seed_product(
        name="FK Product",
        category_id=category["id"],
        price=20.0,
        stock=5,
    )
    order = seed_order(user_id=users["customer_a_id"], total_amount=20.0, status="confirmed")

    act_as("admin")

    bad_order_resp = client.post(
        "/order-items",
        json={
            "order_id": str(uuid.uuid4()),
            "product_id": str(product["id"]),
            "quantity": 1,
            "price_at_purchase": 20.0,
        },
    )
    assert bad_order_resp.status_code == 400
    assert "Invalid order_id" in bad_order_resp.json()["detail"]

    bad_product_resp = client.post(
        "/order-items",
        json={
            "order_id": str(order["id"]),
            "product_id": str(uuid.uuid4()),
            "quantity": 1,
            "price_at_purchase": 20.0,
        },
    )
    assert bad_product_resp.status_code == 400
    assert "Invalid product_id" in bad_product_resp.json()["detail"]

    missing_resp = client.get(f"/order-items/{uuid.uuid4()}")
    assert missing_resp.status_code == 404


def test_users_me_and_list_visibility(
    client, users, act_as
):
    
    act_as("customer_a")
    me_resp = client.get("/users/me")
    assert me_resp.status_code == 200
    assert me_resp.json()["id"] == str(users["customer_a_id"])

    customer_list_resp = client.get("/users/")
    assert customer_list_resp.status_code == 200
    customer_list = customer_list_resp.json()
    assert len(customer_list) == 1
    assert customer_list[0]["id"] == str(users["customer_a_id"])

    act_as("admin")
    admin_list_resp = client.get("/users/")
    assert admin_list_resp.status_code == 200
    assert len(admin_list_resp.json()) == 3


def test_users_forbidden_access_and_admin_delete(
    client, users, act_as
):
    
    act_as("customer_a")
    forbidden_get_resp = client.get(f"/users/{users['customer_b_id']}")
    assert forbidden_get_resp.status_code == 403

    forbidden_delete_resp = client.delete(f"/users/{users['customer_b_id']}")
    assert forbidden_delete_resp.status_code == 403

    act_as("admin")
    delete_resp = client.delete(f"/users/{users['customer_b_id']}")
    assert delete_resp.status_code == 200
    assert delete_resp.json()["deleted"] is True

    missing_resp = client.get(f"/users/{users['customer_b_id']}")
    assert missing_resp.status_code == 404
