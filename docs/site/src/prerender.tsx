import { renderToReadableStream, renderToStaticMarkup } from "react-dom/server";
import { StaticRouter } from "react-router-dom";
import { HelmetProvider } from "react-helmet-async";
import { parseFragment, serialize, serializeOuter, type DefaultTreeAdapterMap } from "parse5";
import Index from "./pages/Index";
import Pricing from "./pages/Pricing";
import Download from "./pages/Download";
import NotFound from "./components/NotFound";
import SEO from "./components/SEO";

const pages = { "/": Index, "/pricing": Pricing, "/download": Download, "/404": NotFound };

export async function render(pathname: string) {
  const Page = pages[pathname as keyof typeof pages];
  const tree = (
    <HelmetProvider>
      <StaticRouter location={pathname}>{Page ? <Page /> : <SEO />}</StaticRouter>
    </HelmetProvider>
  );
  const stream = await renderToReadableStream(tree);
  await stream.allReady;
  await stream.cancel();
  // Lazy imports are now resolved. Static markup needs neither streaming scripts
  // nor hidden Suspense payloads, so it also works under the existing CSP.
  // React 19 emits metadata directly instead of populating Helmet's legacy context.
  const fragment = parseFragment(renderToStaticMarkup(tree));
  const head: string[] = [];
  function extract(node: DefaultTreeAdapterMap["parentNode"]) {
    node.childNodes = node.childNodes.filter((child) => {
      if ("tagName" in child && (["title", "meta", "link"].includes(child.tagName)
        || (child.tagName === "script" && child.attrs.some((attr) => attr.name === "type" && attr.value === "application/ld+json")))) {
        child.attrs.push({ name: "data-prerendered-head", value: "" });
        head.push(serializeOuter(child));
        return false;
      }
      if ("childNodes" in child) extract(child);
      return true;
    });
  }
  extract(fragment);
  return { body: serialize(fragment), head: head.join("\n") };
}
