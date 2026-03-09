"use client";

import { Auth0Provider } from "@auth0/auth0-react";
import type { PropsWithChildren } from "react";

export default function Auth0ProviderWithConfig({
  children,
}: PropsWithChildren) {
  const domain = process.env.NEXT_PUBLIC_AUTH0_DOMAIN;
  const clientId = process.env.NEXT_PUBLIC_AUTH0_CLIENT_ID;
  const audience = process.env.NEXT_PUBLIC_AUTH0_AUDIENCE;

  if (!domain || !clientId || !audience) {
    throw new Error(
      "Missing required Auth0 environment variables. " +
        "Check NEXT_PUBLIC_AUTH0_DOMAIN, NEXT_PUBLIC_AUTH0_CLIENT_ID, " +
        "and NEXT_PUBLIC_AUTH0_AUDIENCE in frontend/.env.local.",
    );
  }

  const redirectUri =
    process.env.NEXT_PUBLIC_AUTH0_REDIRECT_URI ?? window.location.origin;

  return (
    <Auth0Provider
      domain={domain}
      clientId={clientId}
      authorizationParams={{
        audience,
        redirect_uri: redirectUri,
      }}
    >
      {children}
    </Auth0Provider>
  );
}
