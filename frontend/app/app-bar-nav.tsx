"use client";

import Link from "next/link";
import { useRouter } from "next/navigation";
import { useAuth0 } from "@auth0/auth0-react";
import { useState, useEffect } from "react";
import {
  AppBar,
  Toolbar,
  Typography,
  Button,
  IconButton,
  Badge,
  Avatar,
  Menu,
  MenuItem,
} from "@mui/material";
import {
  ShoppingCart as ShoppingCartIcon,
  Storefront as StorefrontIcon,
} from "@mui/icons-material";
import { useAccessToken } from "./auth/useAccessToken";
import { getCurrentUser } from "./services/user-service";
import { useCart } from "./cart-context";

export default function AppBarNav() {
  const router = useRouter();
  const { loginWithRedirect, logout, user, isAuthenticated, isLoading } =
    useAuth0();
  const { getAccessToken } = useAccessToken();
  const { cartCount } = useCart();
  const [anchorEl, setAnchorEl] = useState<null | HTMLElement>(null);
  const [isAdmin, setIsAdmin] = useState(false);

  useEffect(() => {
    if (!isAuthenticated) {
      return;
    }

    let isActive = true;

    (async () => {
      try {
        const token = await getAccessToken();
        const userData = await getCurrentUser(token);

        if (isActive) {
          setIsAdmin(userData.is_admin);
        }
      } catch (err) {
        console.error("Failed to fetch user data:", err);
      }
    })();

    return () => {
      isActive = false;
    };
  }, [getAccessToken, isAuthenticated]);

  const handleMenuOpen = (event: React.MouseEvent<HTMLElement>) => {
    setAnchorEl(event.currentTarget);
  };

  const handleMenuClose = () => {
    setAnchorEl(null);
  };

  const handleLogout = () => {
    handleMenuClose();
    logout({ logoutParams: { returnTo: window.location.origin } });
  };

  const initials = user?.name
    ? user.name
        .split(" ")
        .map((n) => n[0])
        .join("")
        .toUpperCase()
    : "U";

  return (
    <AppBar position="static" elevation={1}>
      <Toolbar>
        <StorefrontIcon sx={{ mr: 1 }} />
        <Typography
          variant="h6"
          component={Link}
          href="/"
          sx={{
            flexGrow: 0,
            mr: 3,
            textDecoration: "none",
            color: "inherit",
          }}
        >
          QuickShop
        </Typography>

        <Button color="inherit" component={Link} href="/">
          Home
        </Button>

        {isAuthenticated && (
          <Button color="inherit" component={Link} href="/orders">
            Orders
          </Button>
        )}

        {isAuthenticated && isAdmin && (
          <Button color="inherit" component={Link} href="/admin">
            Admin
          </Button>
        )}

        <div style={{ flexGrow: 1 }} />

        <IconButton color="inherit" component={Link} href="/cart">
          <Badge badgeContent={cartCount} color="error" invisible={cartCount === 0}>
            <ShoppingCartIcon />
          </Badge>
        </IconButton>

        {isLoading ? null : !isAuthenticated ? (
          <Button color="inherit" onClick={() => loginWithRedirect()}>
            Login
          </Button>
        ) : (
          <>
            <IconButton onClick={handleMenuOpen} sx={{ ml: 1 }}>
              <Avatar sx={{ bgcolor: "secondary.main" }}>{initials}</Avatar>
            </IconButton>
            <Menu
              anchorEl={anchorEl}
              open={Boolean(anchorEl)}
              onClose={handleMenuClose}
            >
              <MenuItem
                onClick={() => {
                  router.push("/orders");
                  handleMenuClose();
                }}
              >
                My Orders
              </MenuItem>
              <MenuItem
                onClick={() => {
                  router.push("/profile");
                  handleMenuClose();
                }}
              >
                Profile
              </MenuItem>
              <MenuItem onClick={handleLogout}>Logout</MenuItem>
            </Menu>
          </>
        )}
      </Toolbar>
    </AppBar>
  );
}
