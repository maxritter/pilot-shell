import { defineConfig, type Plugin } from "vite";
import react from "@vitejs/plugin-react-swc";
import path from "path";
import { componentTagger } from "lovable-tagger";
import sitemapPlugin from "./vite-plugin-sitemap";
import indexNowPlugin from "./vite-plugin-indexnow";

const DOCUSAURUS_DEV_URL = "http://localhost:3000";

function docusaurusRedirect(): Plugin {
  return {
    name: "docusaurus-redirect",
    configureServer(server) {
      server.middlewares.use((req, res, next) => {
        if (req.url?.startsWith("/docs") || req.url?.startsWith("/blog")) {
          res.writeHead(302, { Location: `${DOCUSAURUS_DEV_URL}${req.url}` });
          res.end();
          return;
        }
        next();
      });
    },
  };
}

// https://vitejs.dev/config/
export default defineConfig(({ mode }) => ({
  server: {
    host: "::",
    port: 8080,
  },
  plugins: [
    react(),
    mode === "development" && componentTagger(),
    mode === "development" && docusaurusRedirect(),
    sitemapPlugin(),
    indexNowPlugin(),
  ].filter(Boolean),
  resolve: {
    alias: {
      "@": path.resolve(__dirname, "./src"),
    },
  },
}));
