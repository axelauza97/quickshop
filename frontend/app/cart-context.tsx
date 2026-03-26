"use client";

import { createContext, useContext, useState, useEffect, useCallback } from "react";
import type { PropsWithChildren } from "react";
import { useAuth0 } from "@auth0/auth0-react";
import { Alert, Snackbar } from "@mui/material";
import { useAccessToken } from "@/auth/useAccessToken";
import { getCart, removeCartItem } from "@/services/cart-service";
import type { CartItem } from "@/services/types";
import { getErrorMessage } from "@/utils/error-helpers";

interface CartContextValue {
  cartCount: number;
  cartItems: CartItem[];
  cartTotal: number;
  cartLoading: boolean;
  refreshCart: () => Promise<void>;
  getProductQuantity: (productId: string) => number;
  removeProduct: (productId: string) => Promise<void>;
}

const CartContext = createContext<CartContextValue>({
  cartCount: 0,
  cartItems: [],
  cartTotal: 0,
  cartLoading: true,
  refreshCart: async () => {},
  getProductQuantity: () => 0,
  removeProduct: async () => {},
});

export function CartProvider({ children }: PropsWithChildren) {
  const { isAuthenticated } = useAuth0();
  const { getAccessToken } = useAccessToken();
  const [items, setItems] = useState<CartItem[]>([]);
  const [total, setTotal] = useState(0);
  const [cartLoading, setCartLoading] = useState(true);
  const [feedback, setFeedback] = useState<string | null>(null);

  const cartCount = items.reduce((sum, item) => sum + item.quantity, 0);

  const refreshCart = useCallback(async () => {
    setCartLoading(true);
    if (!isAuthenticated) {
      setItems([]);
      setTotal(0);
      setFeedback(null);
      setCartLoading(false);
      return;
    }
    try {
      const token = await getAccessToken();
      const data = await getCart(token);
      setItems(data.items);
      setTotal(data.total);
      setFeedback(null);
    } catch (err) {
      setFeedback(getErrorMessage(err, "Failed to refresh cart."));
    } finally {
      setCartLoading(false);
    }
  }, [isAuthenticated, getAccessToken]);

  const getProductQuantity = useCallback(
    (productId: string) => {
      const item = items.find((i) => i.product_id === productId);
      return item ? item.quantity : 0;
    },
    [items]
  );

  const removeProduct = useCallback(
    async (productId: string) => {
      const token = await getAccessToken();
      await removeCartItem(token, productId);
      await refreshCart();
    },
    [getAccessToken, refreshCart]
  );

  useEffect(() => {
    void refreshCart();
  }, [refreshCart]);

  return (
    <CartContext.Provider
      value={{
        cartCount,
        cartItems: items,
        cartTotal: total,
        cartLoading,
        refreshCart,
        getProductQuantity,
        removeProduct,
      }}
    >
      {children}
      {feedback ? (
        <Snackbar open autoHideDuration={4000} onClose={() => setFeedback(null)}>
          <Alert
            onClose={() => setFeedback(null)}
            severity="error"
            variant="filled"
            sx={{ width: "100%" }}
          >
            {feedback}
          </Alert>
        </Snackbar>
      ) : null}
    </CartContext.Provider>
  );
}

export function useCart() {
  return useContext(CartContext);
}
