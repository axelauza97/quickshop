import { apiClient } from "@/services/api-client";
import type { Product, Category, PaginatedProducts } from "@/services/types";

type ProductSortBy = "name" | "category" | "price" | "stock" | "created_at";
type SortOrder = "asc" | "desc";

export async function getProducts(params?: {
  search?: string;
  category_id?: string;
  skip?: number;
  limit?: number;
  sort_by?: ProductSortBy;
  order?: SortOrder;
}): Promise<PaginatedProducts> {
  const query = new URLSearchParams();
  if (params?.search) query.set("search", params.search);
  if (params?.category_id) query.set("category_id", params.category_id);
  if (params?.skip != null) query.set("skip", String(params.skip));
  if (params?.limit != null) query.set("limit", String(params.limit));
  if (params?.sort_by) query.set("sort_by", params.sort_by);
  if (params?.order) query.set("order", params.order);

  const qs = query.toString();
  return apiClient<PaginatedProducts>(`/products${qs ? `?${qs}` : ""}`);
}

export async function getProduct(id: string): Promise<Product> {
  return apiClient<Product>(`/products/${id}`);
}

export async function getCategories(): Promise<Category[]> {
  return apiClient<Category[]>("/categories");
}
