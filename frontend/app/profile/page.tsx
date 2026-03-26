"use client";

import { useState, useEffect } from "react";
import {
  Container,
  Typography,
  Card,
  CardContent,
  Box,
  CircularProgress,
  Button,
  Chip,
} from "@mui/material";
import { useAuth0 } from "@auth0/auth0-react";
import { useAccessToken } from "@/auth/useAccessToken";
import { getCurrentUser } from "@/services/user-service";
import type { User } from "@/services/types";

export default function UserProfile() {
  const { user: auth0User, isAuthenticated, loginWithRedirect } = useAuth0();
  const { getAccessToken } = useAccessToken();
  const [backendUser, setBackendUser] = useState<User | null>(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    if (!isAuthenticated) {
      setLoading(false);
      return;
    }
    (async () => {
      try {
        const token = await getAccessToken();
        const data = await getCurrentUser(token);
        setBackendUser(data);
      } catch (err) {
        console.error("Failed to fetch user:", err);
      } finally {
        setLoading(false);
      }
    })();
  }, [isAuthenticated]);

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
          Please log in to view your profile
        </Typography>
        <Button variant="contained" onClick={() => loginWithRedirect()} sx={{ mt: 2 }}>
          Login
        </Button>
      </Container>
    );
  }

  return (
    <Container maxWidth="md" sx={{ py: 4 }}>
      <Typography variant="h4" gutterBottom>
        User Profile
      </Typography>

      <Card elevation={1} sx={{ mt: 3 }}>
        <CardContent>
          <Box sx={{ mb: 3 }}>
            <Typography variant="body2" color="text.secondary">
              Name
            </Typography>
            <Typography variant="h6">{auth0User?.name || "N/A"}</Typography>
          </Box>

          <Box sx={{ mb: 3 }}>
            <Typography variant="body2" color="text.secondary">
              Email
            </Typography>
            <Typography variant="h6">{auth0User?.email || "N/A"}</Typography>
          </Box>

          {backendUser && (
            <>
              <Box sx={{ mb: 3 }}>
                <Typography variant="body2" color="text.secondary">
                  Role
                </Typography>
                <Chip
                  label={backendUser.is_admin ? "Admin" : "Customer"}
                  color={backendUser.is_admin ? "error" : "primary"}
                  size="small"
                  sx={{ mt: 0.5 }}
                />
              </Box>

              <Box sx={{ mb: 3 }}>
                <Typography variant="body2" color="text.secondary">
                  Member Since
                </Typography>
                <Typography variant="h6">
                  {new Date(backendUser.created_at).toLocaleDateString("en-US", {
                    year: "numeric",
                    month: "long",
                    day: "numeric",
                  })}
                </Typography>
              </Box>
            </>
          )}
        </CardContent>
      </Card>
    </Container>
  );
}
