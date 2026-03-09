"use client";

import { useAuth0 } from "@auth0/auth0-react";
import { useState } from "react";
import { useAccessToken } from "../auth/useAccessToken";

export default function AuthControls() {
  const { loginWithRedirect, logout, user, isAuthenticated, isLoading } =
    useAuth0();
  const { getAccessToken } = useAccessToken();
  const [tokenPreview, setTokenPreview] = useState<string | null>(null);

  const handleGetToken = async () => {
    try {
      const token = await getAccessToken();
      setTokenPreview(`${token.slice(0, 24)}...`);

      console.log("Access token:", token);
    } catch (err) {
      // eslint-disable-next-line no-console
      console.error("Failed to get access token", err);
      setTokenPreview("Failed to get token");
    }
  };

  if (isLoading) {
    return <p className="text-sm text-zinc-500">Loading auth…</p>;
  }

  return (
    <div className="flex flex-col gap-3 text-sm text-zinc-700">
      {isAuthenticated ? (
        <>
          <div className="flex flex-col gap-1">
            <span className="font-medium text-zinc-900">Signed in</span>
            {user?.name ? <span>{user.name}</span> : null}
            {user?.email ? <span>{user.email}</span> : null}
          </div>
          <div className="flex flex-wrap gap-2">
            <button
              type="button"
              className="rounded-full border border-zinc-300 px-4 py-2 text-xs font-semibold text-zinc-800 hover:border-zinc-400"
              onClick={handleGetToken}
            >
              Get Token
            </button>
            <button
              type="button"
              className="rounded-full bg-zinc-900 px-4 py-2 text-xs font-semibold text-white hover:bg-zinc-800"
              onClick={() =>
                logout({ logoutParams: { returnTo: window.location.origin } })
              }
            >
              Logout
            </button>
          </div>
          {tokenPreview ? (
            <p className="text-xs text-zinc-500">
              Token preview: {tokenPreview}
            </p>
          ) : null}
        </>
      ) : (
        <div className="flex flex-wrap gap-2">
          <button
            type="button"
            className="rounded-full bg-zinc-900 px-4 py-2 text-xs font-semibold text-white hover:bg-zinc-800"
            onClick={() => loginWithRedirect()}
          >
            Login
          </button>
        </div>
      )}
    </div>
  );
}
