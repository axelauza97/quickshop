"use client";

import { useCallback, useEffect, useState } from "react";
import {
  Alert,
  Box,
  Button,
  CircularProgress,
  Container,
  Snackbar,
  Tab,
  Tabs,
  Typography,
  type AlertColor,
} from "@mui/material";
import { useAuth0 } from "@auth0/auth0-react";
import { useAccessToken } from "@/auth/useAccessToken";
import CategoriesTab from "@/admin/categories-tab";
import OrdersTab from "@/admin/orders-tab";
import ProductsTab from "@/admin/products-tab";
import { getCategories } from "@/services/product-service";
import type { Category, User } from "@/services/types";
import { getCurrentUser } from "@/services/user-service";
import { getErrorMessage } from "@/utils/error-helpers";

interface TabPanelProps {
  children?: React.ReactNode;
  index: number;
  value: number;
}

interface FeedbackState {
  severity: AlertColor;
  message: string;
}

function TabPanel(props: TabPanelProps) {
  const { children, value, index, ...other } = props;
  return (
    <div role="tabpanel" hidden={value !== index} {...other}>
      {value === index && <Box sx={{ py: 3 }}>{children}</Box>}
    </div>
  );
}

export default function AdminDashboard() {
  const {
    isAuthenticated,
    isLoading: auth0Loading,
    loginWithRedirect,
  } = useAuth0();
  const { getAccessToken } = useAccessToken();

  const [backendUser, setBackendUser] = useState<User | null>(null);
  const [authLoading, setAuthLoading] = useState(true);
  const [accessDenied, setAccessDenied] = useState(false);
  const [currentTab, setCurrentTab] = useState(0);
  const [categories, setCategories] = useState<Category[]>([]);
  const [categoriesLoading, setCategoriesLoading] = useState(false);
  const [productsRefreshToken, setProductsRefreshToken] = useState(0);
  const [ordersRefreshToken, setOrdersRefreshToken] = useState(0);
  const [feedback, setFeedback] = useState<FeedbackState | null>(null);

  const showFeedback = useCallback((severity: AlertColor, message: string) => {
    setFeedback({ severity, message });
  }, []);

  const requestProductsRefresh = useCallback(() => {
    setProductsRefreshToken((token) => token + 1);
  }, []);

  const requestOrdersRefresh = useCallback(() => {
    setOrdersRefreshToken((token) => token + 1);
  }, []);

  const refreshCategories = useCallback(
    async (options: { notifyOnError?: boolean } = {}) => {
      const { notifyOnError = true } = options;
      setCategoriesLoading(true);
      try {
        const data = await getCategories();
        setCategories(data);
      } catch (err) {
        if (notifyOnError) {
          showFeedback(
            "error",
            getErrorMessage(err, "Failed to refresh categories.")
          );
        }
        throw err;
      } finally {
        setCategoriesLoading(false);
      }
    },
    [showFeedback]
  );

  useEffect(() => {
    if (auth0Loading) {
      return;
    }

    if (!isAuthenticated) {
      setBackendUser(null);
      setAccessDenied(false);
      setAuthLoading(false);
      return;
    }

    let isActive = true;
    setAuthLoading(true);
    setAccessDenied(false);

    (async () => {
      try {
        const token = await getAccessToken();
        const user = await getCurrentUser(token);

        if (!isActive) {
          return;
        }

        setBackendUser(user);
        setAccessDenied(!user.is_admin);
      } catch {
        if (!isActive) {
          return;
        }

        setBackendUser(null);
        setAccessDenied(true);
      } finally {
        if (isActive) {
          setAuthLoading(false);
        }
      }
    })();

    return () => {
      isActive = false;
    };
  }, [auth0Loading, getAccessToken, isAuthenticated]);

  useEffect(() => {
    if (!backendUser?.is_admin) {
      return;
    }
    refreshCategories({ notifyOnError: false }).catch(() => {
      // Initial load errors are already surfaced by auth and can be retried by user actions.
    });
  }, [backendUser, refreshCategories]);

  if (auth0Loading || authLoading) {
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
          Please log in to access the admin dashboard
        </Typography>
        <Button variant="contained" onClick={() => loginWithRedirect()} sx={{ mt: 2 }}>
          Login
        </Button>
      </Container>
    );
  }

  if (accessDenied) {
    return (
      <Container maxWidth="lg" sx={{ py: 4 }}>
        <Alert severity="error" sx={{ mt: 2 }}>
          <Typography variant="h6">Access Denied</Typography>
          <Typography variant="body2">
            You do not have admin privileges to access this page.
          </Typography>
        </Alert>
      </Container>
    );
  }

  return (
    <Container maxWidth="lg" sx={{ py: 4 }}>
      <Typography variant="h4" gutterBottom>
        Admin Dashboard
      </Typography>

      <Box sx={{ borderBottom: 1, borderColor: "divider" }}>
        <Tabs
          value={currentTab}
          onChange={(_: React.SyntheticEvent, newValue: number) => setCurrentTab(newValue)}
        >
          <Tab label="Products" />
          <Tab label="Categories" />
          <Tab label="Orders" />
        </Tabs>
      </Box>

      <TabPanel value={currentTab} index={0}>
        <ProductsTab
          categories={categories}
          getAccessToken={getAccessToken}
          showFeedback={showFeedback}
          refreshCategories={refreshCategories}
          requestProductsRefresh={requestProductsRefresh}
          refreshToken={productsRefreshToken}
        />
      </TabPanel>

      <TabPanel value={currentTab} index={1}>
        <CategoriesTab
          categories={categories}
          categoriesLoading={categoriesLoading}
          getAccessToken={getAccessToken}
          showFeedback={showFeedback}
          refreshCategories={refreshCategories}
          requestProductsRefresh={requestProductsRefresh}
        />
      </TabPanel>

      <TabPanel value={currentTab} index={2}>
        <OrdersTab
          getAccessToken={getAccessToken}
          showFeedback={showFeedback}
          requestOrdersRefresh={requestOrdersRefresh}
          refreshToken={ordersRefreshToken}
        />
      </TabPanel>

      {feedback ? (
        <Snackbar open autoHideDuration={4000} onClose={() => setFeedback(null)}>
          <Alert
            onClose={() => setFeedback(null)}
            severity={feedback.severity}
            variant="filled"
            sx={{ width: "100%" }}
          >
            {feedback.message}
          </Alert>
        </Snackbar>
      ) : null}
    </Container>
  );
}
