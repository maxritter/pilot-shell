/** The link a Slack DM carries to qualitylayer.dev/open, read as the same place in the QualityLayer App and in the local page. */

/** The shape of an id the CLI accepts for a shared task or an ask. */
const ID = /^[A-Za-z0-9._-]{1,80}$/;
const isId = (segment: string) => ID.test(segment) && segment !== "." && segment !== "..";

/** The seven steps of a task's flow, the only step names a link may carry. */
const STEPS = ["discuss", "research", "plan", "outline", "implement", "verify", "review"];

/** The local page's default address, where the QualityLayer server answers without an App. */
const BROWSER_PAGE = "http://127.0.0.1:41888";

export type OpenLinks = { path: string; app: string; browser: string };

/** The same place three ways, or null when the address is not an ask link, a team link or a step link made of the valid ids and a step name. */
export function openLinks(pathname: string): OpenLinks | null {
  const parts = pathname.replace(/\/$/, "").split("/");
  const [empty, open, kind, ...ids] = parts;
  const shape = kind === "ask" || kind === "step" ? 2 : kind === "team" ? 1 : -1;
  if (empty !== "" || open !== "open" || ids.length !== shape) return null;
  let decoded: string[];
  try {
    decoded = ids.map(decodeURIComponent);
  } catch {
    return null;
  }
  if (!decoded.every(isId) || (kind === "step" && !STEPS.includes(decoded[1]))) return null;
  const path = [kind, ...decoded].join("/");
  return { path, app: `qualitylayer://${path}`, browser: `${BROWSER_PAGE}/#/${path}` };
}
