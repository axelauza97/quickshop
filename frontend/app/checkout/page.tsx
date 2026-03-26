"use client";

import { useState, useEffect } from "react";
import { useRouter } from "next/navigation";
import {
  Container,
  Typography,
  Card,
  CardContent,
  Button,
  List,
  ListItem,
  ListItemText,
  Divider,
  Alert,
  Box,
  CircularProgress,
} from "@mui/material";
import { useAuth0 } from "@auth0/auth0-react";
import { useAccessToken } from "@/auth/useAccessToken";
import { useCart } from "@/cart-context";
import { getCart } from "@/services/cart-service";
import { checkout } from "@/services/order-service";
import type { CartResponse } from "@/services/types";

export default function Checkout() {
  const router = useRouter();
  const { isAuthenticated, loginWithRedirect } = useAuth0();
  const { getAccessToken } = useAccessToken();
  const { refreshCart } = useCart();
  const [cart, setCart] = useState<CartResponse | null>(null);
  const [loading, setLoading] = useState(true);
  const [placing, setPlacing] = useState(false);
  const [orderId, setOrderId] = useState("");
  const [orderPlaced, setOrderPlaced] = useState(false);

  useEffect(() => {
    if (!isAuthenticated) {
      setLoading(false);
      return;
    }
    (async () => {
      try {
        const token = await getAccessToken();
        const data = await getCart(token);
        setCart(data);
      } catch (err) {
        console.error("Failed to fetch cart:", err);
      } finally {
        setLoading(false);
      }
    })();
  }, [isAuthenticated]);

  const handlePlaceOrder = async () => {
    setPlacing(true);
    try {
      const token = await getAccessToken();
      const result = await checkout(token);
      setOrderId(result.order.id);
      setOrderPlaced(true);
      await refreshCart();
    } catch (err) {
      console.error("Failed to place order:", err);
    } finally {
      setPlacing(false);
    }
  };

  if (loading) {
    return (
      <Container maxWidth="md" sx={{ py: 4, display: "flex", justifyContent: "center" }}>
        <CircularProgress />
      </Container>
    );
  }

  if (!isAuthenticated) {
    return (
      <Container maxWidth="md" sx={{ py: 8, textAlign: "center" }}>
        <Typography variant="h5" gutterBottom>
          Please log in to checkout
        </Typography>
        <Button variant="contained" onClick={() => loginWithRedirect()} sx={{ mt: 2 }}>
          Login
        </Button>
      </Container>
    );
  }

  if (orderPlaced) {
    return (
      <Container maxWidth="md" sx={{ py: 4 }}>
        <Alert severity="success" sx={{ mb: 3 }}>
          <Typography variant="h6">Order placed successfully!</Typography>
          <Typography variant="body2">Order ID: {orderId}</Typography>
        </Alert>

        <Card elevation={1}>
          <CardContent>
            <Typography variant="h5" gutterBottom>
              Thank you for your order!
            </Typography>
            <Typography variant="body1" paragraph>
              Your order has been confirmed and will be shipped soon.
            </Typography>
            <Box sx={{ mt: 3 }}>
              <Button
                variant="contained"
                onClick={() => router.push("/orders")}
                sx={{ mr: 2 }}
              >
                View Orders
              </Button>
              <Button variant="outlined" onClick={() => router.push("/")}>
                Continue Shopping
              </Button>
            </Box>
          </CardContent>
        </Card>
      </Container>
    );
  }

  if (!cart || cart.items.length === 0) {
    return (
      <Container maxWidth="md" sx={{ py: 8, textAlign: "center" }}>
        <Typography variant="h5" gutterBottom>
          Your cart is empty
        </Typography>
        <Button variant="contained" onClick={() => router.push("/")} sx={{ mt: 2 }}>
          Browse Products
        </Button>
      </Container>
    );
  }

  return (
    <Container maxWidth="md" sx={{ py: 4 }}>
      <Typography variant="h4" gutterBottom>
        Checkout
      </Typography>

      <Card elevation={1} sx={{ mt: 3 }}>
        <CardContent>
          <Typography variant="h6" gutterBottom>
            Order Summary
          </Typography>

          <List>
            {cart.items.map((item) => (
              <ListItem key={item.id} sx={{ py: 1 }}>
                <ListItemText
                  primary={item.product?.name || "Unknown Product"}
                  secondary={`Quantity: ${item.quantity}`}
                />
                <Typography variant="body1">
                  ${((item.product?.price || 0) * item.quantity).toFixed(2)}
                </Typography>
              </ListItem>
            ))}
          </List>

          <Divider sx={{ my: 2 }} />

          <Box sx={{ display: "flex", justifyContent: "space-between", mb: 2 }}>
            <Typography variant="h6">Total Amount:</Typography>
            <Typography variant="h6" color="primary">
              ${cart.total.toFixed(2)}
            </Typography>
          </Box>

          <Button
            variant="contained"
            size="large"
            fullWidth
            onClick={handlePlaceOrder}
            disabled={placing}
            sx={{ mt: 2 }}
          >
            {placing ? "Placing Order..." : "Place Order"}
          </Button>
        </CardContent>
      </Card>
    </Container>
  );
}
