"use client";

import createCache, { type EmotionCache } from "@emotion/cache";
import { CacheProvider } from "@emotion/react";
import CssBaseline from "@mui/material/CssBaseline";
import { ThemeProvider, createTheme } from "@mui/material/styles";
import { useServerInsertedHTML } from "next/navigation";
import type { PropsWithChildren } from "react";
import { useState } from "react";

const theme = createTheme({
  palette: {
    primary: {
      main: "#0097a7",
    },
  },
});

function createEmotionCache() {
  const cache = createCache({ key: "mui" });
  cache.compat = true;

  const prevInsert = cache.insert;
  let inserted: string[] = [];

  cache.insert = (...args: Parameters<EmotionCache["insert"]>) => {
    const [, serialized] = args;

    if (cache.inserted[serialized.name] === undefined) {
      inserted.push(serialized.name);
    }

    return prevInsert(...args);
  };

  const flush = () => {
    const names = inserted;
    inserted = [];
    return names;
  };

  return { cache, flush };
}

export default function MuiThemeProvider({ children }: PropsWithChildren) {
  const [{ cache, flush }] = useState(createEmotionCache);

  useServerInsertedHTML(() => {
    const names = flush();

    if (names.length === 0) {
      return null;
    }

    let styles = "";

    for (const name of names) {
      const style = cache.inserted[name];

      if (typeof style === "string") {
        styles += style;
      }
    }

    return (
      <style
        data-emotion={`${cache.key} ${names.join(" ")}`}
        dangerouslySetInnerHTML={{ __html: styles }}
      />
    );
  });

  return (
    <CacheProvider value={cache}>
      <ThemeProvider theme={theme}>
        <CssBaseline />
        {children}
      </ThemeProvider>
    </CacheProvider>
  );
}
