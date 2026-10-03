/** The link a Slack DM carries to qualitylayer.dev/open, read as the same place in the QualityLayer App and in the local page. */

/** The shape of an id the CLI accepts for a shared task or an ask. */
const ID = /^[A-Za-z0-9._-]{1,80}$/;
const isId = (segment: string) => ID.test(segment) && segment !== "." && segment !== "..";

/** The local page's default address, where the QualityLayer server answers without an App. */
const BROWSER_PAGE = "http://127.0.0.1:41888";

export type OpenLinks = { path: string; app: string; browser: string };

/** The same place three ways, or null when the address is not an ask link or a team link made of the valid ids. */
export function openLinks(pathname: string): OpenLinks | null {
  const parts = pathname.replace(/\/$/, "").split("/");
  const [empty, open, kind, ...ids] = parts;
  if (empty !== "" || open !== "open" || (kind === "ask" ? ids.length !== 2 : kind !== "team" || ids.length !== 1)) return null;
  let decoded: string[];
  try {
    decoded = ids.map(decodeURIComponent);
  } catch {
    return null;
  }
  if (!decoded.every(isId)) return null;
  const path = [kind, ...decoded].join("/");
  return { path, app: `qualitylayer://${path}`, browser: `${BROWSER_PAGE}/#/${path}` };
}
