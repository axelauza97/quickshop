"use client";

import Link from "next/link";
import { useRouter } from "next/navigation";
import {
  Container,
  Typography,
  Table,
  TableBody,
  TableCell,
  TableContainer,
  TableHead,
  TableRow,
  Paper,
  TextField,
  IconButton,
  Button,
  Box,
  CircularProgress,
} from "@mui/material";
import { Delete as DeleteIcon } from "@mui/icons-material";
import { useAuth0 } from "@auth0/auth0-react";
import { useAccessToken } from "@/auth/useAccessToken";
import { useCart } from "@/cart-context";
import { updateCartItem, removeCartItem } from "@/services/cart-service";

export default function ShoppingCart() {
  const router = useRouter();
  const { isAuthenticated, loginWithRedirect } = useAuth0();
  const { getAccessToken } = useAccessToken();
  const { cartItems, cartTotal, cartLoading, refreshCart } = useCart();

  const handleQuantityChange = async (productId: string, newQuantity: number) => {
    if (newQuantity < 1) return;
    try {
      const token = await getAccessToken();
      await updateCartItem(token, productId, newQuantity);
      await refreshCart();
    } catch (err) {
      console.error("Failed to update quantity:", err);
    }
  };

  const handleRemove = async (productId: string) => {
    try {
      const token = await getAccessToken();
      await removeCartItem(token, productId);
      await refreshCart();
    } catch (err) {
      console.error("Failed to remove item:", err);
    }
  };

  if (isAuthenticated && cartLoading) {
    return (
      <Container maxWidth="lg" sx={{ py: 4, display: "flex", justifyContent: "center" }}>
        <CircularProgress />
      </Container>
    );
  }

  if (!isAuthenticated) {
    return (
      <Container maxWidth="lg" sx={{ py: 8, textAlign: "center" }}>
        <Typography variant="h5" gutterBottom>
          Please log in to view your cart
        </Typography>
        <Button variant="contained" onClick={() => loginWithRedirect()} sx={{ mt: 2 }}>
          Login
        </Button>
      </Container>
    );
  }

  if (cartItems.length === 0) {
    return (
      <Container maxWidth="lg" sx={{ py: 8, textAlign: "center" }}>
        <Typography variant="h5" gutterBottom>
          Your cart is empty
        </Typography>
        <Button variant="contained" component={Link} href="/" sx={{ mt: 2 }}>
          Browse Products
        </Button>
      </Container>
    );
  }

  return (
    <Container maxWidth="lg" sx={{ py: 4 }}>
      <Typography variant="h4" gutterBottom>
        Shopping Cart
      </Typography>

      <TableContainer component={Paper} elevation={1} sx={{ mt: 3 }}>
        <Table>
          <TableHead>
            <TableRow>
              <TableCell>Product</TableCell>
              <TableCell>Name</TableCell>
              <TableCell align="right">Quantity</TableCell>
              <TableCell align="right">Unit Price</TableCell>
              <TableCell align="right">Total</TableCell>
              <TableCell align="center">Action</TableCell>
            </TableRow>
          </TableHead>
          <TableBody>
            {cartItems.map((item) => (
              <TableRow key={item.id}>
                <TableCell>
                  <Box
                    component="img"
                    src={item.product?.image_url || "/placeholder.png"}
                    alt={item.product?.name || "Product"}
                    sx={{ width: 60, height: 60, objectFit: "cover", borderRadius: 1 }}
                  />
                </TableCell>
                <TableCell>
                  <Typography variant="body1">
                    {item.product?.name || "Unknown Product"}
                  </Typography>
                </TableCell>
                <TableCell align="right">
                  <TextField
                    type="number"
                    value={item.quantity}
                    onChange={(e) =>
                      handleQuantityChange(item.product_id, parseInt(e.target.value))
                    }
                    inputProps={{ min: 1 }}
                    size="small"
                    sx={{ width: 80 }}
                  />
                </TableCell>
                <TableCell align="right">
                  ${item.product?.price.toFixed(2) || "0.00"}
                </TableCell>
                <TableCell align="right">
                  ${((item.product?.price || 0) * item.quantity).toFixed(2)}
                </TableCell>
                <TableCell align="center">
                  <IconButton
                    color="error"
                    onClick={() => handleRemove(item.product_id)}
                  >
                    <DeleteIcon />
                  </IconButton>
                </TableCell>
              </TableRow>
            ))}
          </TableBody>
        </Table>
      </TableContainer>

      <Box sx={{ mt: 3, display: "flex", justifyContent: "flex-end" }}>
        <Box sx={{ minWidth: 300 }}>
          <Box sx={{ display: "flex", justifyContent: "space-between", mb: 3 }}>
            <Typography variant="h5">Total:</Typography>
            <Typography variant="h5" color="primary">
              ${cartTotal.toFixed(2)}
            </Typography>
          </Box>
          <Button
            variant="contained"
            size="large"
            fullWidth
            onClick={() => router.push("/checkout")}
          >
            Proceed to Checkout
          </Button>
        </Box>
      </Box>
    </Container>
  );
}
