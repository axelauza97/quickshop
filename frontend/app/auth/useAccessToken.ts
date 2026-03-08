"use client";

import { useAuth0 } from "@auth0/auth0-react";
import { useCallback } from "react";

export function useAccessToken() {
  const { getAccessTokenSilently, isAuthenticated, isLoading, error } =
    useAuth0();

  const getAccessToken = useCallback(async () => {
    return getAccessTokenSilently();
  }, [getAccessTokenSilently]);

  return { getAccessToken, isAuthenticated, isLoading, error };
}
