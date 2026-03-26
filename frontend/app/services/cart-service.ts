import { apiClient } from "@/services/api-client";
import type { CartResponse, CartItem } from "@/services/types";

export async function getCart(token: string): Promise<CartResponse> {
  return apiClient<CartResponse>("/cart", {}, token);
}

export async function addToCart(
  token: string,
  product_id: string,
  quantity: number = 1
): Promise<CartItem> {
  return apiClient<CartItem>(
    "/cart/items",
    { method: "POST", body: JSON.stringify({ product_id, quantity }) },
    token
  );
}

export async function updateCartItem(
  token: string,
  product_id: string,
  quantity: number
): Promise<CartItem> {
  return apiClient<CartItem>(
    `/cart/items/${product_id}`,
    { method: "PUT", body: JSON.stringify({ quantity }) },
    token
  );
}

export async function removeCartItem(
  token: string,
  product_id: string
): Promise<void> {
  await apiClient(`/cart/items/${product_id}`, { method: "DELETE" }, token);
}

export async function clearCart(token: string): Promise<void> {
  await apiClient("/cart", { method: "DELETE" }, token);
}
