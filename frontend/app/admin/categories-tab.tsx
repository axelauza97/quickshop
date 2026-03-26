"use client";

import { useState } from "react";
import {
  Button,
  CircularProgress,
  Dialog,
  DialogActions,
  DialogContent,
  DialogTitle,
  IconButton,
  Paper,
  Table,
  TableBody,
  TableCell,
  TableContainer,
  TableHead,
  TableRow,
  TextField,
  type AlertColor,
} from "@mui/material";
import {
  Add as AddIcon,
  Delete as DeleteIcon,
} from "@mui/icons-material";
import { createCategory, deleteCategory } from "@/services/admin-service";
import { ApiError } from "@/services/api-client";
import type { Category } from "@/services/types";
import { getErrorMessage } from "@/utils/error-helpers";

const CATEGORY_DELETE_BLOCKED_MESSAGE =
  "This category can't be deleted because it contains products, delete all products first.";

function isCategoryDeleteBlockedError(err: unknown): boolean {
  if (!(err instanceof ApiError)) {
    return false;
  }

  const detail =
    err.body && typeof err.body === "object" && "detail" in err.body
      ? (err.body as { detail?: unknown }).detail
      : null;

  const messages = [err.body, detail]
    .filter((message): message is string => typeof message === "string" && message.trim().length > 0)
    .map((message) => message.toLowerCase());

  return messages.some(
    (message) =>
      message.includes("order_item_product_id_fkey") ||
      (message.includes("violates foreign key constraint") &&
        message.includes("order_item"))
  );
}

interface CategoriesTabProps {
  categories: Category[];
  categoriesLoading: boolean;
  getAccessToken: () => Promise<string>;
  showFeedback: (severity: AlertColor, message: string) => void;
  refreshCategories: (options?: { notifyOnError?: boolean }) => Promise<void>;
  requestProductsRefresh: () => void;
}

export default function CategoriesTab({
  categories,
  categoriesLoading,
  getAccessToken,
  showFeedback,
  refreshCategories,
  requestProductsRefresh,
}: CategoriesTabProps) {
  const [categoryDialogOpen, setCategoryDialogOpen] = useState(false);
  const [newCategoryName, setNewCategoryName] = useState("");
  const [creatingCategory, setCreatingCategory] = useState(false);
  const [deletingCategoryId, setDeletingCategoryId] = useState<string | null>(null);

  const handleAddCategory = async () => {
    const trimmedName = newCategoryName.trim();
    if (!trimmedName) {
      return;
    }

    setCreatingCategory(true);
    try {
      const token = await getAccessToken();
      await createCategory(token, { name: trimmedName });

      setNewCategoryName("");
      setCategoryDialogOpen(false);
      showFeedback("success", "Category created.");

      try {
        await refreshCategories({ notifyOnError: false });
      } catch {
        showFeedback(
          "warning",
          "Category was created, but categories could not be refreshed."
        );
      }
    } catch (err) {
      console.error("Failed to create category:", err);
      showFeedback("error", getErrorMessage(err, "Failed to create category."));
    } finally {
      setCreatingCategory(false);
    }
  };

  const handleDeleteCategory = async (categoryId: string) => {
    setDeletingCategoryId(categoryId);
    try {
      const token = await getAccessToken();
      await deleteCategory(token, categoryId);
      showFeedback("success", "Category deleted.");

      try {
        await refreshCategories({ notifyOnError: false });
      } catch {
        showFeedback(
          "warning",
          "Category was deleted, but categories could not be refreshed."
        );
      }

      requestProductsRefresh();
    } catch (err) {
      console.error("Failed to delete category:", err);
      if (isCategoryDeleteBlockedError(err)) {
        showFeedback("error", CATEGORY_DELETE_BLOCKED_MESSAGE);
        return;
      }

      showFeedback("error", getErrorMessage(err, "Failed to delete category."));
    } finally {
      setDeletingCategoryId(null);
    }
  };

  return (
    <>
      <Button
        variant="contained"
        startIcon={<AddIcon />}
        onClick={() => setCategoryDialogOpen(true)}
        disabled={creatingCategory}
        sx={{ mb: 2 }}
      >
        Add Category
      </Button>

      <TableContainer component={Paper} elevation={1}>
        <Table>
          <TableHead>
            <TableRow>
              <TableCell>Category Name</TableCell>
              <TableCell align="right">Products</TableCell>
              <TableCell align="center">Actions</TableCell>
            </TableRow>
          </TableHead>
          <TableBody>
            {categoriesLoading ? (
              <TableRow>
                <TableCell colSpan={3} align="center">
                  <CircularProgress size={24} />
                </TableCell>
              </TableRow>
            ) : (
              categories.map((category) => (
                <TableRow key={category.id}>
                  <TableCell>{category.name}</TableCell>
                  <TableCell align="right">{category.products.length}</TableCell>
                  <TableCell align="center">
                    <IconButton
                      color="error"
                      aria-label={`Delete ${category.name}`}
                      disabled={deletingCategoryId === category.id}
                      onClick={() => handleDeleteCategory(category.id)}
                    >
                      {deletingCategoryId === category.id ? (
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
        open={categoryDialogOpen}
        onClose={() => setCategoryDialogOpen(false)}
        maxWidth="xs"
        fullWidth
      >
        <DialogTitle>Add Category</DialogTitle>
        <DialogContent>
          <TextField
            label="Category Name"
            value={newCategoryName}
            onChange={(event) => setNewCategoryName(event.target.value)}
            fullWidth
            sx={{ mt: 2 }}
          />
        </DialogContent>
        <DialogActions>
          <Button onClick={() => setCategoryDialogOpen(false)} disabled={creatingCategory}>
            Cancel
          </Button>
          <Button
            onClick={handleAddCategory}
            variant="contained"
            disabled={creatingCategory || !newCategoryName.trim()}
          >
            {creatingCategory ? "Adding..." : "Add"}
          </Button>
        </DialogActions>
      </Dialog>
    </>
  );
}
