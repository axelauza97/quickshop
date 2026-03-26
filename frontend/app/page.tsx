"use client";

import { useState, useEffect } from "react";
import Link from "next/link";
import {
  Container,
  TextField,
  Select,
  MenuItem,
  FormControl,
  InputLabel,
  Card,
  CardMedia,
  CardContent,
  CardActions,
  Button,
  Typography,
  Pagination,
  Box,
  CircularProgress,
  Chip,
  IconButton,
} from "@mui/material";
import { Snackbar, Alert } from "@mui/material";
import DeleteOutlineIcon from "@mui/icons-material/DeleteOutline";
import { getProducts, getCategories } from "./services/product-service";
import { addToCart } from "./services/cart-service";
import type { Product, Category } from "./services/types";
import { useAuth0 } from "@auth0/auth0-react";
import { useAccessToken } from "./auth/useAccessToken";
import { useCart } from "./cart-context";

export default function HomePage() {
  const [searchQuery, setSearchQuery] = useState("");
  const [debouncedSearchQuery, setDebouncedSearchQuery] = useState("");
  const [selectedCategory, setSelectedCategory] = useState("");
  const [page, setPage] = useState(1);
  const [products, setProducts] = useState<Product[]>([]);
  const [totalProducts, setTotalProducts] = useState(0);
  const [categories, setCategories] = useState<Category[]>([]);
  const [loading, setLoading] = useState(true);
  const itemsPerPage = 8;

  const { loginWithRedirect } = useAuth0();
  const { getAccessToken, isAuthenticated } = useAccessToken();
  const { refreshCart, getProductQuantity, removeProduct } = useCart();
  const [snackOpen, setSnackOpen] = useState(false);
  const [addingId, setAddingId] = useState<string | null>(null);
  const [removingId, setRemovingId] = useState<string | null>(null);

  // Fetch categories on mount
  useEffect(() => {
    getCategories()
      .then((data) => setCategories(data))
      .catch((err) => console.error("Failed to fetch categories:", err));
  }, []);

  useEffect(() => {
    const timeoutId = setTimeout(() => {
      setDebouncedSearchQuery(searchQuery);
      setPage(1);
    }, 300);

    return () => clearTimeout(timeoutId);
  }, [searchQuery]);

  // Fetch products when search, category, or page changes
  useEffect(() => {
    let isActive = true;

    setLoading(true);

    getProducts({
      search: debouncedSearchQuery || undefined,
      category_id: selectedCategory || undefined,
      skip: (page - 1) * itemsPerPage,
      limit: itemsPerPage,
    })
      .then((data) => {
        if (!isActive) {
          return;
        }

        setProducts(data.items);
        setTotalProducts(data.total);
      })
      .catch((err) => console.error("Failed to fetch products:", err))
      .finally(() => {
        if (isActive) {
          setLoading(false);
        }
      });

    return () => {
      isActive = false;
    };
  }, [debouncedSearchQuery, selectedCategory, page]);

  const totalPages = Math.ceil(totalProducts / itemsPerPage);

  const handleAddToCart = async (productId: string) => {
    if (!isAuthenticated) {
      loginWithRedirect();
      return;
    }
    setAddingId(productId);
    try {
      const token = await getAccessToken();
      await addToCart(token, productId);
      await refreshCart();
      setSnackOpen(true);
    } catch (err) {
      console.error("Failed to add to cart:", err);
    } finally {
      setAddingId(null);
    }
  };

  const handleRemoveFromCart = async (productId: string) => {
    setRemovingId(productId);
    try {
      await removeProduct(productId);
    } catch (err) {
      console.error("Failed to remove from cart:", err);
    } finally {
      setRemovingId(null);
    }
  };

  return (
    <Container maxWidth="lg" sx={{ py: 4 }}>
      <Box sx={{ mb: 4, display: "flex", gap: 2, flexWrap: "wrap" }}>
        <TextField
          label="Search products"
          variant="outlined"
          value={searchQuery}
          onChange={(e) => setSearchQuery(e.target.value)}
          sx={{ flexGrow: 1, minWidth: 200 }}
        />
        <FormControl sx={{ minWidth: 200 }}>
          <InputLabel>Category</InputLabel>
          <Select
            value={selectedCategory}
            label="Category"
            onChange={(e) => {
              setSelectedCategory(e.target.value);
              setPage(1);
            }}
          >
            <MenuItem value="">All</MenuItem>
            {categories.map((cat) => (
              <MenuItem key={cat.id} value={cat.id}>
                {cat.name}
              </MenuItem>
            ))}
          </Select>
        </FormControl>
      </Box>

      {loading ? (
        <Box sx={{ display: "flex", justifyContent: "center", py: 8 }}>
          <CircularProgress />
        </Box>
      ) : (
        <>
          <Box
            sx={{
              display: "grid",
              gridTemplateColumns: {
                xs: "1fr",
                sm: "repeat(2, 1fr)",
                md: "repeat(3, 1fr)",
                lg: "repeat(4, 1fr)",
              },
              gap: 3,
            }}
          >
            {products.map((product) => (
              <Card
                key={product.id}
                elevation={1}
                sx={{ height: "100%", display: "flex", flexDirection: "column" }}
              >
                <CardMedia
                  component="img"
                  height="200"
                  image={product.image_url || "/placeholder.png"}
                  alt={product.name}
                  sx={{ objectFit: "cover" }}
                />
                <CardContent sx={{ flexGrow: 1 }}>
                  <Typography
                    variant="h6"
                    component={Link}
                    href={`/product/${product.id}`}
                    sx={{ textDecoration: "none", color: "inherit" }}
                  >
                    {product.name}
                  </Typography>
                  <Typography variant="h6" color="primary" sx={{ mt: 1 }}>
                    ${product.price.toFixed(2)}
                  </Typography>
                  <Typography
                    variant="body2"
                    color="text.secondary"
                    sx={{ mt: 1 }}
                  >
                    {product.description
                      ? product.description.substring(0, 80) + "..."
                      : ""}
                  </Typography>
                </CardContent>
                <CardActions sx={{ gap: 1 }}>
                  <Button
                    size="small"
                    variant="contained"
                    sx={{ flexGrow: 1 }}
                    disabled={addingId === product.id}
                    onClick={() => handleAddToCart(product.id)}
                  >
                    {addingId === product.id ? "Adding..." : "Add to Cart"}
                  </Button>
                  {getProductQuantity(product.id) > 0 && (
                    <>
                      <Chip
                        label={`×${getProductQuantity(product.id)}`}
                        size="small"
                        color="primary"
                        variant="outlined"
                      />
                      <IconButton
                        size="small"
                        color="error"
                        disabled={removingId === product.id}
                        onClick={() => handleRemoveFromCart(product.id)}
                      >
                        <DeleteOutlineIcon fontSize="small" />
                      </IconButton>
                    </>
                  )}
                </CardActions>
              </Card>
            ))}
          </Box>

          {totalPages > 1 && (
            <Box sx={{ display: "flex", justifyContent: "center", mt: 4 }}>
              <Pagination
                count={totalPages}
                page={page}
                onChange={(e, value) => setPage(value)}
                color="primary"
              />
            </Box>
          )}

          {products.length === 0 && (
            <Box sx={{ textAlign: "center", py: 8 }}>
              <Typography variant="h6" color="text.secondary">
                No products found
              </Typography>
            </Box>
          )}
        </>
      )}
      <Snackbar open={snackOpen} autoHideDuration={3000} onClose={() => setSnackOpen(false)}>
        <Alert onClose={() => setSnackOpen(false)} severity="success" variant="filled">
          Added to cart!
        </Alert>
      </Snackbar>
    </Container>
  );
}
