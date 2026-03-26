"use client";

import { useEffect, useState } from "react";
import {
  Box,
  Button,
  CircularProgress,
  Dialog,
  DialogActions,
  DialogContent,
  DialogTitle,
  FormControl,
  IconButton,
  InputLabel,
  MenuItem,
  Paper,
  Select,
  Table,
  TableBody,
  TableCell,
  TableContainer,
  TableHead,
  TableRow,
  TableSortLabel,
  TextField,
  type AlertColor,
} from "@mui/material";
import {
  Add as AddIcon,
  Delete as DeleteIcon,
  Edit as EditIcon,
} from "@mui/icons-material";
import {
  createProduct,
  deleteProduct,
  updateProduct,
} from "@/services/admin-service";
import { ApiError } from "@/services/api-client";
import { getProducts } from "@/services/product-service";
import type { Category, Product } from "@/services/types";
import { getErrorMessage } from "@/utils/error-helpers";

type ProductSortBy = "name" | "category" | "price" | "stock";

const PRODUCT_DELETE_BLOCKED_MESSAGE =
  "This product can't be deleted because it is part of an existing order.";

interface ProductsTabProps {
  categories: Category[];
  getAccessToken: () => Promise<string>;
  showFeedback: (severity: AlertColor, message: string) => void;
  refreshCategories: (options?: { notifyOnError?: boolean }) => Promise<void>;
  requestProductsRefresh: () => void;
  refreshToken: number;
}

export default function ProductsTab({
  categories,
  getAccessToken,
  showFeedback,
  refreshCategories,
  requestProductsRefresh,
  refreshToken,
}: ProductsTabProps) {
  const [products, setProducts] = useState<Product[]>([]);
  const [loadingProducts, setLoadingProducts] = useState(true);
  const [productDialogOpen, setProductDialogOpen] = useState(false);
  const [editingProduct, setEditingProduct] = useState<Product | null>(null);
  const [savingProduct, setSavingProduct] = useState(false);
  const [deletingProductId, setDeletingProductId] = useState<string | null>(null);
  const [orderBy, setOrderBy] = useState<ProductSortBy>("name");
  const [sortDir, setSortDir] = useState<"asc" | "desc">("asc");
  const [productForm, setProductForm] = useState({
    name: "",
    price: "",
    description: "",
    category_id: "",
    stock: "",
    image_url: "",
  });

  const parsedPrice = Number.parseFloat(productForm.price);
  const parsedStock =
    productForm.stock.trim() === ""
      ? 0
      : Number.parseInt(productForm.stock, 10);

  const productFormError = !productForm.name.trim()
    ? "Product name is required."
    : !productForm.category_id
      ? "Choose a category."
      : Number.isNaN(parsedPrice) || parsedPrice < 0
        ? "Enter a valid price."
        : Number.isNaN(parsedStock) || parsedStock < 0
          ? "Enter a valid stock quantity."
          : null;

  useEffect(() => {
    let isActive = true;

    (async () => {
      setLoadingProducts(true);
      try {
        const response = await getProducts({
          skip: 0,
          limit: 100,
          sort_by: orderBy,
          order: sortDir,
        });
        if (isActive) {
          setProducts(response.items);
        }
      } catch (err) {
        console.error("Failed to fetch products:", err);
        if (isActive) {
          showFeedback("error", getErrorMessage(err, "Failed to fetch products."));
        }
      } finally {
        if (isActive) {
          setLoadingProducts(false);
        }
      }
    })();

    return () => {
      isActive = false;
    };
  }, [orderBy, refreshToken, showFeedback, sortDir]);

  const getCategoryName = (categoryId: string) =>
    categories.find((category) => category.id === categoryId)?.name || "-";

  const handleAddProduct = () => {
    setEditingProduct(null);
    setProductForm({
      name: "",
      price: "",
      description: "",
      category_id: categories[0]?.id || "",
      stock: "",
      image_url: "",
    });
    setProductDialogOpen(true);
  };

  const handleEditProduct = (product: Product) => {
    setEditingProduct(product);
    setProductForm({
      name: product.name,
      price: product.price.toString(),
      description: product.description || "",
      category_id: product.category_id,
      stock: product.stock.toString(),
      image_url: product.image_url || "",
    });
    setProductDialogOpen(true);
  };

  const handleSaveProduct = async () => {
    if (productFormError) {
      showFeedback("error", productFormError);
      return;
    }

    setSavingProduct(true);
    try {
      const token = await getAccessToken();
      const data = {
        name: productForm.name.trim(),
        price: parsedPrice,
        description: productForm.description || undefined,
        category_id: productForm.category_id,
        stock: parsedStock,
        image_url: productForm.image_url || undefined,
      };

      const savedProduct = editingProduct
        ? await updateProduct(token, editingProduct.id, data)
        : await createProduct(token, data);

      setProducts((currentProducts) => {
        if (editingProduct) {
          return currentProducts.map((product) =>
            product.id === savedProduct.id ? savedProduct : product
          );
        }

        return [...currentProducts, savedProduct];
      });

      setProductDialogOpen(false);
      setEditingProduct(null);
      showFeedback(
        "success",
        editingProduct ? "Product updated." : "Product created."
      );

      requestProductsRefresh();
      try {
        await refreshCategories({ notifyOnError: false });
      } catch {
        showFeedback(
          "warning",
          "Product saved, but categories could not be refreshed."
        );
      }
    } catch (err) {
      console.error("Failed to save product:", err);
      showFeedback(
        "error",
        getErrorMessage(
          err,
          editingProduct ? "Failed to update product." : "Failed to create product."
        )
      );
    } finally {
      setSavingProduct(false);
    }
  };

  const handleDeleteProduct = async (productId: string) => {
    setDeletingProductId(productId);
    try {
      const token = await getAccessToken();
      await deleteProduct(token, productId);
      setProducts((currentProducts) =>
        currentProducts.filter((product) => product.id !== productId)
      );
      showFeedback("success", "Product deleted.");
      try {
        await refreshCategories({ notifyOnError: false });
      } catch {
        showFeedback(
          "warning",
          "Product deleted, but categories could not be refreshed."
        );
      }
    } catch (err) {
      console.error("Failed to delete product:", err);
      if (err instanceof ApiError && err.status === 409) {
        showFeedback(
          "error",
          getErrorMessage(err, PRODUCT_DELETE_BLOCKED_MESSAGE)
        );
        return;
      }

      showFeedback("error", getErrorMessage(err, "Failed to delete product."));
    } finally {
      setDeletingProductId(null);
    }
  };

  const handleSort = (property: ProductSortBy) => {
    const isAscending = orderBy === property && sortDir === "asc";
    setOrderBy(property);
    setSortDir(isAscending ? "desc" : "asc");
  };

  return (
    <>
      <Button
        variant="contained"
        startIcon={<AddIcon />}
        onClick={handleAddProduct}
        disabled={savingProduct}
        sx={{ mb: 2 }}
      >
        Add Product
      </Button>

      <TableContainer component={Paper} elevation={1}>
        <Table>
          <TableHead>
            <TableRow>
              <TableCell sx={{ width: 60 }}>Image</TableCell>
              <TableCell sortDirection={orderBy === "name" ? sortDir : false}>
                <TableSortLabel
                  active={orderBy === "name"}
                  direction={orderBy === "name" ? sortDir : "asc"}
                  onClick={() => handleSort("name")}
                >
                  Name
                </TableSortLabel>
              </TableCell>
              <TableCell sortDirection={orderBy === "category" ? sortDir : false}>
                <TableSortLabel
                  active={orderBy === "category"}
                  direction={orderBy === "category" ? sortDir : "asc"}
                  onClick={() => handleSort("category")}
                >
                  Category
                </TableSortLabel>
              </TableCell>
              <TableCell align="right" sortDirection={orderBy === "price" ? sortDir : false}>
                <TableSortLabel
                  active={orderBy === "price"}
                  direction={orderBy === "price" ? sortDir : "asc"}
                  onClick={() => handleSort("price")}
                >
                  Price
                </TableSortLabel>
              </TableCell>
              <TableCell align="right" sortDirection={orderBy === "stock" ? sortDir : false}>
                <TableSortLabel
                  active={orderBy === "stock"}
                  direction={orderBy === "stock" ? sortDir : "asc"}
                  onClick={() => handleSort("stock")}
                >
                  Stock
                </TableSortLabel>
              </TableCell>
              <TableCell align="center">Actions</TableCell>
            </TableRow>
          </TableHead>
          <TableBody>
            {loadingProducts ? (
              <TableRow>
                <TableCell colSpan={6} align="center">
                  <Box sx={{ py: 3 }}>
                    <CircularProgress size={24} />
                  </Box>
                </TableCell>
              </TableRow>
            ) : (
              products.map((product) => (
                <TableRow key={product.id}>
                  <TableCell>
                    <Box
                      component="img"
                      src={product.image_url || "/file.svg"}
                      alt={product.name}
                      sx={{ width: 40, height: 40, objectFit: "cover", borderRadius: 0.5 }}
                    />
                  </TableCell>
                  <TableCell>{product.name}</TableCell>
                  <TableCell>{getCategoryName(product.category_id)}</TableCell>
                  <TableCell align="right">${product.price.toFixed(2)}</TableCell>
                  <TableCell align="right">{product.stock}</TableCell>
                  <TableCell align="center">
                    <IconButton
                      color="primary"
                      aria-label={`Edit ${product.name}`}
                      disabled={savingProduct || deletingProductId === product.id}
                      onClick={() => handleEditProduct(product)}
                    >
                      <EditIcon />
                    </IconButton>
                    <IconButton
                      color="error"
                      aria-label={`Delete ${product.name}`}
                      disabled={deletingProductId === product.id}
                      onClick={() => handleDeleteProduct(product.id)}
                    >
                      {deletingProductId === product.id ? (
                        <CircularProgress size={18} color="inherit" />
                      ) : (
                        <DeleteIcon />
                      )}
                    </IconButton>
                  </TableCell>
                </TableRow>
              ))
            )}
          </TableBody>
        </Table>
      </TableContainer>

      <Dialog
        open={productDialogOpen}
        onClose={() => setProductDialogOpen(false)}
        maxWidth="sm"
        fullWidth
      >
        <DialogTitle>{editingProduct ? "Edit Product" : "Add Product"}</DialogTitle>
        <DialogContent>
          <TextField
            label="Product Name"
            value={productForm.name}
            onChange={(event) =>
              setProductForm({ ...productForm, name: event.target.value })
            }
            fullWidth
            sx={{ mt: 2, mb: 2 }}
          />
          <TextField
            label="Price"
            type="number"
            value={productForm.price}
            onChange={(event) =>
              setProductForm({ ...productForm, price: event.target.value })
            }
            fullWidth
            sx={{ mb: 2 }}
          />
          <TextField
            label="Description"
            value={productForm.description}
            onChange={(event) =>
              setProductForm({ ...productForm, description: event.target.value })
            }
            fullWidth
            multiline
            rows={3}
            sx={{ mb: 2 }}
          />
          <FormControl fullWidth sx={{ mb: 2 }}>
            <InputLabel>Category</InputLabel>
            <Select
              value={productForm.category_id}
              label="Category"
              onChange={(event) =>
                setProductForm({ ...productForm, category_id: event.target.value })
              }
            >
              {categories.map((category) => (
                <MenuItem key={category.id} value={category.id}>
                  {category.name}
                </MenuItem>
              ))}
            </Select>
          </FormControl>
          <TextField
            label="Stock"
            type="number"
            value={productForm.stock}
            onChange={(event) =>
              setProductForm({ ...productForm, stock: event.target.value })
            }
            fullWidth
            sx={{ mb: 2 }}
          />
          <TextField
            label="Image URL"
            value={productForm.image_url}
            onChange={(event) =>
              setProductForm({ ...productForm, image_url: event.target.value })
            }
            fullWidth
          />
        </DialogContent>
        <DialogActions>
          <Button onClick={() => setProductDialogOpen(false)} disabled={savingProduct}>
            Cancel
          </Button>
          <Button
            onClick={handleSaveProduct}
            variant="contained"
            disabled={savingProduct || Boolean(productFormError)}
          >
            {savingProduct ? "Saving..." : "Save"}
          </Button>
        </DialogActions>
      </Dialog>
    </>
  );
}
