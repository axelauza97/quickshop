// ── Response types (match backend response_schemas) ──

export interface Product {
  id: string;
  name: string;
  description: string | null;
  price: number;
  category_id: string;
  stock: number;
  image_url: string | null;
  created_at: string;
}

export interface PaginatedProducts {
  items: Product[];
  total: number;
}

export interface Category {
  id: string;
  name: string;
  created_at: string;
  products: Product[];
}

export interface User {
  id: string;
  auth0_sub: string;
  is_admin: boolean;
  created_at: string;
}

export interface OrderItem {
  id: string;
  order_id: string;
  product_id: string;
  product_name: string;
  quantity: number;
  price_at_purchase: number;
  created_at: string;
}

export interface Order {
  id: string;
  user_id: string;
  total_amount: number;
  status: string;
  created_at: string;
  order_items: OrderItem[];
}

export interface PaginatedOrders {
  items: Order[];
  total: number;
}

export interface CartItem {
  id: string;
  product_id: string;
  quantity: number;
  created_at: string;
  product: Product | null;
}

export interface CartResponse {
  items: CartItem[];
  total: number;
}

export interface CheckoutResponse {
  order: Order;
  message: string;
}

// ── Request types (match backend request_schemas) ──

export interface CreateProductRequest {
  name: string;
  description?: string;
  price: number;
  category_id: string;
  stock?: number;
  image_url?: string;
}

export interface UpdateProductRequest {
  name?: string;
  description?: string;
  price?: number;
  category_id?: string;
  stock?: number;
  image_url?: string;
}

export interface CreateCategoryRequest {
  name: string;
}

export interface UpdateCategoryRequest {
  name?: string;
}

export interface AddCartItemRequest {
  product_id: string;
  quantity?: number;
}

export interface UpdateCartItemRequest {
  quantity: number;
}

export interface UpdateOrderRequest {
  total_amount?: number;
  status?: string;
}

export interface CheckoutRequest {
  shipping_address?: string;
}
