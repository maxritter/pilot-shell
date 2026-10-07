import { defineConfig, type Plugin } from "vite";
import react from "@vitejs/plugin-react-swc";
import tailwindcss from "@tailwindcss/vite";
import path from "path";
import sitemapPlugin from "./vite-plugin-sitemap";
import indexNowPlugin from "./vite-plugin-indexnow";

const DOCUSAURUS_DEV_URL = "http://localhost:3000";
const COCKPIT_SOURCE = path.resolve(__dirname, "../../qualitylayer/src/ui");

/** The demo uses the production Cockpit. Each app keeps its own shadcn imports. */
function cockpitDemo(): Plugin {
  return {
    name: "qualitylayer-cockpit-demo",
    enforce: "pre",
    async resolveId(source, importer) {
      if (source === "/qualitylayer-cockpit-demo.tsx") return path.join(COCKPIT_SOURCE, "demo/main.tsx");
      if (!source.startsWith("@/")) return null;
      const base = importer?.startsWith(COCKPIT_SOURCE) ? COCKPIT_SOURCE : path.resolve(__dirname, "src");
      return this.resolve(path.join(base, source.slice(2)), importer, { skipSelf: true });
    },
  };
}

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
    fs: { allow: [__dirname, path.resolve(__dirname, "../../qualitylayer/src"), path.resolve(__dirname, "../../qualitylayer/node_modules")] },
    // The release list is an edge function in production; in development it comes from the live site, so the cards download directly.
    proxy: { "/app/downloads.json": { target: "https://qualitylayer.dev", changeOrigin: true } },
  },
  plugins: [
    cockpitDemo(),
    react(),
    tailwindcss(),
    mode === "development" && docusaurusRedirect(),
    sitemapPlugin(),
    indexNowPlugin(),
  ].filter(Boolean),
  resolve: {
    // The lifecycle names its routes and optional steps from the product's own tables.
    alias: { "@ql": path.resolve(__dirname, "../../qualitylayer/src") },
    dedupe: ["react", "react-dom", "cn", "lucide-react", "radix-ui", "class-variance-authority", "clsx", "tailwind-merge", "dompurify", "marked", "mermaid", "sonner", "tailwindcss", "tw-animate-css", "shadcn"],
  },
  build: {
    target: "es2020",
    cssMinify: true,
    chunkSizeWarningLimit: 800,
    // Polar's checkout is only reachable through a lazy import on /pricing:
    // keep it out of the home page's preloads.
    modulePreload: {
      polyfill: false,
      resolveDependencies(_filename, deps) {
        return deps.filter((d) => !d.includes("polar-"));
      },
    },
    rollupOptions: {
      input: { website: path.resolve(__dirname, "index.html"), app: path.resolve(__dirname, "app-demo/index.html") },
      output: {
        // Split only feature-specific deps into their own chunks. Anything that
        // chains back through react/react-dom stays in the default vendor chunk
        // so we don't create import cycles.
        manualChunks: (id) => {
          if (!id.includes("node_modules")) return undefined;
          if (id.includes("@polar-sh")) return "polar";
          return undefined;
        },
      },
    },
  },
}));
