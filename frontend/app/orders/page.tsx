"use client";

import { useState, useEffect } from "react";
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
  Chip,
  Accordion,
  AccordionSummary,
  AccordionDetails,
  List,
  ListItem,
  ListItemText,
  CircularProgress,
  Button,
  TableSortLabel,
} from "@mui/material";
import { ExpandMore as ExpandMoreIcon } from "@mui/icons-material";
import { useAuth0 } from "@auth0/auth0-react";
import { useAccessToken } from "@/auth/useAccessToken";
import { getOrders } from "@/services/order-service";
import type { Order } from "@/services/types";
import { getErrorMessage } from "@/utils/error-helpers";
import { getStatusColor, formatOrderDate } from "@/utils/order-helpers";

export default function OrderHistory() {
  type OrderSortBy = "created_at" | "total_amount" | "status";

  const { isAuthenticated, isLoading: authLoading, loginWithRedirect } = useAuth0();
  const { getAccessToken } = useAccessToken();
  const [orders, setOrders] = useState<Order[]>([]);
  const [loading, setLoading] = useState(true);
  const [orderBy, setOrderBy] = useState<OrderSortBy>("created_at");
  const [sortDir, setSortDir] = useState<"asc" | "desc">("desc");

  useEffect(() => {
    if (authLoading) {
      return;
    }

    if (!isAuthenticated) {
      setOrders([]);
      setLoading(false);
      return;
    }

    let isActive = true;
    setLoading(true);

    (async () => {
      try {
        const token = await getAccessToken();
        const data = await getOrders(token, {
          sort_by: orderBy,
          order: sortDir,
          limit: 100,
        });

        if (isActive) {
          setOrders(data.items);
        }
      } catch (err) {
        console.error(getErrorMessage(err, "Failed to fetch orders."));
      } finally {
        if (isActive) {
          setLoading(false);
        }
      }
    })();

    return () => {
      isActive = false;
    };
  }, [authLoading, getAccessToken, isAuthenticated, orderBy, sortDir]);

  const handleSort = (property: OrderSortBy) => {
    const isAsc = orderBy === property && sortDir === "asc";
    setSortDir(isAsc ? "desc" : "asc");
    setOrderBy(property);
  };

  if (authLoading || loading) {
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
          Please log in to view your orders
        </Typography>
        <Button variant="contained" onClick={() => loginWithRedirect()} sx={{ mt: 2 }}>
          Login
        </Button>
      </Container>
    );
  }

  if (orders.length === 0) {
    return (
      <Container maxWidth="lg" sx={{ py: 8, textAlign: "center" }}>
        <Typography variant="h5" gutterBottom>
          No orders yet
        </Typography>
        <Typography variant="body1" color="text.secondary">
          Start shopping to see your orders here.
        </Typography>
      </Container>
    );
  }

  return (
    <Container maxWidth="lg" sx={{ py: 4 }}>
      <Typography variant="h4" gutterBottom>
        Order History
      </Typography>

      <TableContainer component={Paper} elevation={1} sx={{ mt: 3 }}>
        <Table>
          <TableHead>
            <TableRow>
              <TableCell>Order ID</TableCell>
              <TableCell sortDirection={orderBy === "created_at" ? sortDir : false}>
                <TableSortLabel
                  active={orderBy === "created_at"}
                  direction={orderBy === "created_at" ? sortDir : "asc"}
                  onClick={() => handleSort("created_at")}
                >
                  Date
                </TableSortLabel>
              </TableCell>
              <TableCell align="right" sortDirection={orderBy === "total_amount" ? sortDir : false}>
                <TableSortLabel
                  active={orderBy === "total_amount"}
                  direction={orderBy === "total_amount" ? sortDir : "asc"}
                  onClick={() => handleSort("total_amount")}
                >
                  Total
                </TableSortLabel>
              </TableCell>
              <TableCell sortDirection={orderBy === "status" ? sortDir : false}>
                <TableSortLabel
                  active={orderBy === "status"}
                  direction={orderBy === "status" ? sortDir : "asc"}
                  onClick={() => handleSort("status")}
                >
                  Status
                </TableSortLabel>
              </TableCell>
              <TableCell>Details</TableCell>
            </TableRow>
          </TableHead>
          <TableBody>
            {orders.map((order) => (
              <TableRow key={order.id}>
                <TableCell sx={{ fontFamily: "monospace", fontSize: "0.8rem" }}>
                  {order.id.slice(0, 8)}...
                </TableCell>
                <TableCell>
                  {formatOrderDate(order.created_at)}
                </TableCell>
                <TableCell align="right">
                  ${order.total_amount.toFixed(2)}
                </TableCell>
                <TableCell>
                  <Chip
                    label={order.status.charAt(0).toUpperCase() + order.status.slice(1)}
                    color={getStatusColor(order.status)}
                    size="small"
                  />
                </TableCell>
                <TableCell>
                  <Accordion
                    elevation={0}
                    sx={{
                      border: "none",
                      boxShadow: "none",
                      "&:before": { display: "none" },
                    }}
                  >
                    <AccordionSummary expandIcon={<ExpandMoreIcon />}>
                      <Typography variant="body2">
                        View Items ({order.order_items.length})
                      </Typography>
                    </AccordionSummary>
                    <AccordionDetails>
                      <List dense>
                        {order.order_items.map((item) => (
                          <ListItem key={item.id}>
                            <ListItemText
                              primary={item.product_name}
                              secondary={`Quantity: ${item.quantity} × $${item.price_at_purchase.toFixed(2)}`}
                            />
                          </ListItem>
                        ))}
                      </List>
                    </AccordionDetails>
                  </Accordion>
                </TableCell>
              </TableRow>
            ))}
          </TableBody>
        </Table>
      </TableContainer>
    </Container>
  );
}
