import { apiClient } from "@/services/api-client";
import type {
  Product,
  Category,
  Order,
  CreateProductRequest,
  UpdateProductRequest,
  CreateCategoryRequest,
  UpdateOrderRequest,
} from "@/services/types";

// ── Products ──

export async function createProduct(
  token: string,
  data: CreateProductRequest
): Promise<Product> {
  return apiClient<Product>(
    "/products",
    { method: "POST", body: JSON.stringify(data) },
    token
  );
}

export async function updateProduct(
  token: string,
  id: string,
  data: UpdateProductRequest
): Promise<Product> {
  return apiClient<Product>(
    `/products/${id}`,
    { method: "PUT", body: JSON.stringify(data) },
    token
  );
}

export async function deleteProduct(
  token: string,
  id: string
): Promise<void> {
  await apiClient(`/products/${id}`, { method: "DELETE" }, token);
}

// ── Categories ──

export async function createCategory(
  token: string,
  data: CreateCategoryRequest
): Promise<Category> {
  return apiClient<Category>(
    "/categories",
    { method: "POST", body: JSON.stringify(data) },
    token
  );
}

export async function deleteCategory(
  token: string,
  id: string
): Promise<void> {
  await apiClient(`/categories/${id}`, { method: "DELETE" }, token);
}

// ── Orders ──

export async function updateOrder(
  token: string,
  id: string,
  data: UpdateOrderRequest
): Promise<Order> {
  return apiClient<Order>(
    `/orders/${id}`,
    { method: "PUT", body: JSON.stringify(data) },
    token
  );
}

export async function deleteOrder(
  token: string,
  id: string
): Promise<void> {
  await apiClient(`/orders/${id}`, { method: "DELETE" }, token);
}
