import type { Metadata } from "next";
import "./globals.css";
import Auth0ProviderWithConfig from "./auth0-provider";
import MuiThemeProvider from "./theme-provider";
import AppBarNav from "./app-bar-nav";
import { CartProvider } from "./cart-context";

export const metadata: Metadata = {
  title: "QuickShop",
  description: "Simple e-commerce web app",
};

export default function RootLayout({
  children,
}: Readonly<{
  children: React.ReactNode;
}>) {
  return (
    <html lang="en">
      <body>
        <Auth0ProviderWithConfig>
          <MuiThemeProvider>
            <CartProvider>
              <AppBarNav />
              <main>{children}</main>
            </CartProvider>
          </MuiThemeProvider>
        </Auth0ProviderWithConfig>
      </body>
    </html>
  );
}
