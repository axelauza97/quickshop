"use client";

import { useEffect, useState } from "react";
import {
  Chip,
  CircularProgress,
  FormControl,
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
  type AlertColor,
} from "@mui/material";
import { updateOrder } from "@/services/admin-service";
import { getOrders } from "@/services/order-service";
import type { Order } from "@/services/types";
import { getErrorMessage } from "@/utils/error-helpers";
import { formatOrderDate, getStatusColor } from "@/utils/order-helpers";

interface OrdersTabProps {
  getAccessToken: () => Promise<string>;
  showFeedback: (severity: AlertColor, message: string) => void;
  requestOrdersRefresh: () => void;
  refreshToken: number;
}

type OrderSortBy = "created_at" | "total_amount" | "status";

export default function OrdersTab({
  getAccessToken,
  showFeedback,
  requestOrdersRefresh,
  refreshToken,
}: OrdersTabProps) {
  const [orders, setOrders] = useState<Order[]>([]);
  const [loadingOrders, setLoadingOrders] = useState(true);
  const [updatingOrderId, setUpdatingOrderId] = useState<string | null>(null);
  const [orderBy, setOrderBy] = useState<OrderSortBy>("created_at");
  const [sortDir, setSortDir] = useState<"asc" | "desc">("desc");

  useEffect(() => {
    let isActive = true;

    (async () => {
      setLoadingOrders(true);
      try {
        const token = await getAccessToken();
        const response = await getOrders(token, {
          sort_by: orderBy,
          order: sortDir,
          skip: 0,
          limit: 100,
        });
        if (isActive) {
          setOrders(response.items);
        }
      } catch (err) {
        console.error("Failed to fetch orders:", err);
        if (isActive) {
          showFeedback("error", getErrorMessage(err, "Failed to fetch orders."));
        }
      } finally {
        if (isActive) {
          setLoadingOrders(false);
        }
      }
    })();

    return () => {
      isActive = false;
    };
  }, [getAccessToken, orderBy, refreshToken, showFeedback, sortDir]);

  const handleSort = (property: OrderSortBy) => {
    const isAscending = orderBy === property && sortDir === "asc";
    setOrderBy(property);
    setSortDir(isAscending ? "desc" : "asc");
  };

  const handleOrderStatusChange = async (orderId: string, nextStatus: string) => {
    setUpdatingOrderId(orderId);
    try {
      const token = await getAccessToken();
      await updateOrder(token, orderId, { status: nextStatus });
      showFeedback("success", `Order status updated to ${nextStatus}.`);
      requestOrdersRefresh();
    } catch (err) {
      console.error("Failed to update order status:", err);
      showFeedback(
        "error",
        getErrorMessage(err, "Failed to update order status.")
      );
    } finally {
      setUpdatingOrderId(null);
    }
  };

  return (
    <TableContainer component={Paper} elevation={1}>
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
            <TableCell>Update Status</TableCell>
          </TableRow>
        </TableHead>
        <TableBody>
          {loadingOrders ? (
            <TableRow>
              <TableCell colSpan={5} align="center">
                <CircularProgress size={24} />
              </TableCell>
            </TableRow>
          ) : (
            orders.map((order) => (
              <TableRow key={order.id}>
                <TableCell sx={{ fontFamily: "monospace", fontSize: "0.8rem" }}>
                  {order.id.slice(0, 8)}...
                </TableCell>
                <TableCell>{formatOrderDate(order.created_at)}</TableCell>
                <TableCell align="right">${order.total_amount.toFixed(2)}</TableCell>
                <TableCell>
                  <Chip
                    label={order.status.charAt(0).toUpperCase() + order.status.slice(1)}
                    color={getStatusColor(order.status)}
                    size="small"
                  />
                </TableCell>
                <TableCell>
                  <FormControl
                    size="small"
                    sx={{ minWidth: 150 }}
                    disabled={updatingOrderId === order.id}
                  >
                    <Select
                      value={order.status}
                      onChange={(event) =>
                        handleOrderStatusChange(order.id, event.target.value)
                      }
                    >
                      <MenuItem value="pending">Pending</MenuItem>
                      <MenuItem value="confirmed">Confirmed</MenuItem>
                      <MenuItem value="shipped">Shipped</MenuItem>
                      <MenuItem value="delivered">Delivered</MenuItem>
                      <MenuItem value="cancelled">Cancelled</MenuItem>
                    </Select>
                  </FormControl>
                </TableCell>
              </TableRow>
            ))
          )}
        </TableBody>
      </Table>
    </TableContainer>
  );
}
