import { lazy, Suspense } from "react";
import { BrowserRouter, Routes, Route, useLocation } from "react-router-dom";
import { HelmetProvider } from "react-helmet-async";
import { Analytics } from "@vercel/analytics/react";
import { SpeedInsights } from "@vercel/speed-insights/react";
import ScrollToTop from "@/components/ScrollToTop";
import ScrollToHash from "@/components/ScrollToHash";
import Index from "./pages/Index";

const Pricing = lazy(() => import("./pages/Pricing"));
const Shared = lazy(() => import("./pages/Shared"));
const NotFound = lazy(() => import("./pages/NotFound"));
const Open = lazy(() => import("./pages/Open"));
const Download = lazy(() => import("./pages/Download"));

/** Page statistics everywhere but on the page a Slack DM opens, which reads its link and sends nothing. */
export const Metrics = () => {
  const { pathname } = useLocation();
  if (pathname.startsWith("/open/")) return null;
  return (
    <>
      <Analytics />
      <SpeedInsights />
    </>
  );
};

const App = () => (
  <HelmetProvider>
    <BrowserRouter>
      <ScrollToTop />
      <ScrollToHash />
      <Suspense fallback={null}>
        <Routes>
          <Route path="/" element={<Index />} />
          <Route path="/pricing" element={<Pricing />} />
          <Route path="/s/:id" element={<Shared />} />
          <Route path="/open/*" element={<Open />} />
          <Route path="/download" element={<Download />} />
          {/* /docs is served by Docusaurus static files */}
          {/* ADD ALL CUSTOM ROUTES ABOVE THE CATCH-ALL "*" ROUTE */}
          <Route path="*" element={<NotFound />} />
        </Routes>
      </Suspense>
      <Metrics />
    </BrowserRouter>
  </HelmetProvider>
);

export default App;
