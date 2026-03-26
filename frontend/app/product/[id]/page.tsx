"use client";

import { useState, useEffect, use } from "react";
import Link from "next/link";
import {
  Container,
  Typography,
  Button,
  TextField,
  Chip,
  Box,
  Breadcrumbs,
  CircularProgress,
  Snackbar,
  Alert,
} from "@mui/material";
import { NavigateNext as NavigateNextIcon } from "@mui/icons-material";
import { useAuth0 } from "@auth0/auth0-react";
import { useAccessToken } from "@/auth/useAccessToken";
import { useCart } from "@/cart-context";
import { addToCart } from "@/services/cart-service";
import { ApiError } from "@/services/api-client";
import { getProduct, getCategories } from "@/services/product-service";
import type { Product, Category } from "@/services/types";

export default function ProductDetail({
  params,
}: {
  params: Promise<{ id: string }>;
}) {
  const { id } = use(params);
  const [quantity, setQuantity] = useState(1);
  const [product, setProduct] = useState<Product | null>(null);
  const [categories, setCategories] = useState<Category[]>([]);
  const [loading, setLoading] = useState(true);
  const [snackOpen, setSnackOpen] = useState(false);

  const { isAuthenticated, loginWithRedirect } = useAuth0();
  const { getAccessToken } = useAccessToken();
  const { refreshCart } = useCart();

  useEffect(() => {
    async function fetchData() {
      try {
        const [productData, categoriesData] = await Promise.all([
          getProduct(id),
          getCategories(),
        ]);
        setProduct(productData);
        setCategories(categoriesData);
      } catch (error) {
        if (
          !(error instanceof ApiError) ||
          (error.status !== 404 && error.status !== 422)
        ) {
          console.error("Failed to fetch product data:", error);
        }
      } finally {
        setLoading(false);
      }
    }
    fetchData();
  }, [id]);

  if (loading) {
    return (
      <Container
        maxWidth="lg"
        sx={{ py: 4, display: "flex", justifyContent: "center" }}
      >
        <CircularProgress />
      </Container>
    );
  }

  if (!product) {
    return (
      <Container maxWidth="lg" sx={{ py: 4 }}>
        <Typography variant="h5">Product not found</Typography>
        <Button component={Link} href="/" sx={{ mt: 2 }}>
          Back to Home
        </Button>
      </Container>
    );
  }

  const categoryName =
    categories.find((c) => c.id === product.category_id)?.name;

  const handleAddToCart = async () => {
    if (!isAuthenticated) {
      loginWithRedirect();
      return;
    }
    try {
      const token = await getAccessToken();
      await addToCart(token, product.id, quantity);
      await refreshCart();
      setSnackOpen(true);
    } catch (error) {
      console.error("Failed to add to cart:", error);
    }
  };

  const handleQuantityChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    const value = parseInt(e.target.value);
    if (value > 0 && value <= product.stock) {
      setQuantity(value);
    }
  };

  return (
    <Container maxWidth="lg" sx={{ py: 4 }}>
      <Breadcrumbs
        separator={<NavigateNextIcon fontSize="small" />}
        sx={{ mb: 3 }}
      >
        <Link href="/" style={{ textDecoration: "none", color: "inherit" }}>
          Home
        </Link>
        <Link href="/" style={{ textDecoration: "none", color: "inherit" }}>
          {categoryName}
        </Link>
        <Typography color="text.primary">{product.name}</Typography>
      </Breadcrumbs>

      <Box
        sx={{
          display: "grid",
          gridTemplateColumns: { xs: "1fr", md: "1fr 1fr" },
          gap: 4,
        }}
      >
        <Box>
          <Box
            component="img"
            src={product.image_url ?? undefined}
            alt={product.name}
            sx={{
              width: "100%",
              height: "auto",
              maxHeight: 500,
              objectFit: "cover",
              borderRadius: 1,
            }}
          />
        </Box>

        <Box>
          <Typography variant="h4" component="h1" gutterBottom>
            {product.name}
          </Typography>

          <Typography variant="h5" color="primary" gutterBottom>
            ${product.price.toFixed(2)}
          </Typography>

          <Box sx={{ my: 2 }}>
            <Chip
              label={categoryName}
              color="primary"
              variant="outlined"
            />
          </Box>

          <Typography variant="body1" paragraph sx={{ mt: 3 }}>
            {product.description}
          </Typography>

          <Box sx={{ my: 3 }}>
            <Typography
              variant="body2"
              color={product.stock > 0 ? "success.main" : "error.main"}
            >
              {product.stock > 0
                ? `In Stock (${product.stock} available)`
                : "Out of Stock"}
            </Typography>
          </Box>

          <Box
            sx={{ display: "flex", gap: 2, alignItems: "center", my: 3 }}
          >
            <TextField
              type="number"
              label="Quantity"
              value={quantity}
              onChange={handleQuantityChange}
              inputProps={{ min: 1, max: product.stock }}
              sx={{ width: 100 }}
            />
            <Button
              variant="contained"
              size="large"
              onClick={handleAddToCart}
              disabled={product.stock === 0}
              sx={{ flexGrow: 1 }}
            >
              Add to Cart
            </Button>
          </Box>

          <Button component={Link} href="/" variant="outlined" fullWidth>
            Continue Shopping
          </Button>
        </Box>
      </Box>

      <Snackbar open={snackOpen} autoHideDuration={3000} onClose={() => setSnackOpen(false)}>
        <Alert onClose={() => setSnackOpen(false)} severity="success" variant="filled">
          Added to cart!
        </Alert>
      </Snackbar>
    </Container>
  );
}
