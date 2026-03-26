import { apiClient } from "@/services/api-client";
import type { Order, CheckoutResponse, PaginatedOrders } from "@/services/types";

type OrderSortBy = "created_at" | "total_amount" | "status";
type SortOrder = "asc" | "desc";

export async function getOrders(
  token: string,
  params?: {
    sort_by?: OrderSortBy;
    order?: SortOrder;
    skip?: number;
    limit?: number;
  }
): Promise<PaginatedOrders> {
  const query = new URLSearchParams();
  if (params?.sort_by) query.set("sort_by", params.sort_by);
  if (params?.order) query.set("order", params.order);
  if (params?.skip != null) query.set("skip", String(params.skip));
  if (params?.limit != null) query.set("limit", String(params.limit));

  const qs = query.toString();
  return apiClient<PaginatedOrders>(`/orders${qs ? `?${qs}` : ""}`, {}, token);
}

export async function getOrder(token: string, id: string): Promise<Order> {
  return apiClient<Order>(`/orders/${id}`, {}, token);
}

export async function checkout(
  token: string,
  shippingAddress?: string
): Promise<CheckoutResponse> {
  return apiClient<CheckoutResponse>(
    "/checkout",
    {
      method: "POST",
      body: JSON.stringify({ shipping_address: shippingAddress }),
    },
    token
  );
}
