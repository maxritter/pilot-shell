import dates from "../plugins/publication-date.cjs";

export function publicationLoader(fetcher) {
  let request;
  return () => request ??= fetcher("/app/releases.json", { signal: AbortSignal.timeout(8000) })
    .then((response) => response.ok ? response.json() : {})
    .then((body) => body.releases ?? {})
    .catch(() => ({}));
}

const load = publicationLoader((...args) => fetch(...args));

export async function refreshPublicationDates(root = document, publications = load) {
  const nodes = root.querySelectorAll("[data-release-version]");
  if (nodes.length === 0) return;
  const releases = await publications();
  for (const node of nodes) {
    const published = releases[node.getAttribute("data-release-version")];
    const text = dates.publicationDate(published);
    if (text === null) continue;
    node.textContent = text;
    node.setAttribute("datetime", published);
  }
}

export function onRouteDidUpdate({ location }) {
  if (location.pathname.replace(/\/$/, "") === "/docs/changelog") return refreshPublicationDates();
}
