import { renderToReadableStream } from "react-dom/server.browser";
import { HelmetProvider } from "react-helmet-async";
import { MemoryRouter, Route, Routes } from "react-router-dom";
import { afterEach, describe, expect, it, vi } from "vitest";
import { Metrics } from "@/App";
import { isPhone } from "@/lib/device";
import { openLinks } from "@/lib/open-link";
import Open, { OpenView } from "./Open";

/**
 * The page a Slack DM opens: it tries the reader's QualityLayer App, then offers the three ways
 * on. It only reads the link: no request, no key, and it never trusts what the address says
 * beyond the two id shapes the CLI itself accepts.
 */

async function html(node: React.ReactNode): Promise<string> {
  const stream = await renderToReadableStream(<HelmetProvider>{node}</HelmetProvider>);
  await stream.allReady;
  return new Response(stream).text();
}

const at = (path: string) =>
  html(
    <MemoryRouter initialEntries={[path]}>
      <Routes>
        <Route path="/open/*" element={<Open />} />
      </Routes>
    </MemoryRouter>,
  );

vi.mock("@vercel/analytics/react", () => ({ Analytics: () => <i>analytics</i> }));
vi.mock("@vercel/speed-insights/react", () => ({ SpeedInsights: () => <i>speed-insights</i> }));

afterEach(() => vi.unstubAllGlobals());

describe("the link a DM carries", () => {
  it("maps an ask and a team link to the same place in the App, in the browser page and in the App link", () => {
    expect(openLinks("/open/ask/t_9c2/7f3a")).toEqual({
      path: "ask/t_9c2/7f3a",
      app: "qualitylayer://ask/t_9c2/7f3a",
      browser: "http://127.0.0.1:41888/#/ask/t_9c2/7f3a",
    });
    expect(openLinks("/open/team/t_9c2")).toMatchObject({ path: "team/t_9c2", app: "qualitylayer://team/t_9c2" });
  });

  it("accepts nothing else: another place, a missing id, an extra segment, a path out of the folder, a long id", () => {
    for (const bad of [
      "/open/ask/..%2f/x",
      "/open/ask/../x",
      "/open/ask/t_9c2",
      "/open/team/t_9c2/extra",
      "/open/task/t_9c2/7f3a",
      "/open/ask/t_9c2/7f3a?token=x",
      "/open/ask/%E0%A4%A/x",
      `/open/team/${"a".repeat(81)}`,
      "/open/ask/t_9c2/a b",
      "/open",
    ]) {
      expect(openLinks(bad), bad).toBeNull();
    }
  });
});

describe("the landing page on a computer", () => {
  it("offers three ways on once the attempt is over: the App, the browser page on the default port, the download", async () => {
    const fetchFn = vi.fn();
    vi.stubGlobal("fetch", fetchFn);
    const links = openLinks("/open/ask/t_9c2/7f3a");
    const shown = await html(<OpenView links={links!} device="computer" phase="offer" />);

    expect(shown).toContain('href="qualitylayer://ask/t_9c2/7f3a"');
    expect(shown).toContain('href="http://127.0.0.1:41888/#/ask/t_9c2/7f3a"');
    expect(shown).toContain('href="/download"');
    expect(shown).toContain("Open in the App");
    expect(shown).toContain("Open in this browser");
    expect(shown).toContain("Get the QualityLayer App");
    expect(fetchFn).not.toHaveBeenCalled();
  });

  it("says it is trying the App while the attempt runs, and shows no buttons yet", async () => {
    const shown = await html(<OpenView links={openLinks("/open/ask/t_9c2/7f3a")!} device="computer" phase="trying" />);
    expect(shown).toContain("Opening the ask in the QualityLayer App");
    expect(shown).not.toContain("Open in this browser");
  });

  it("names a team link a task, not an ask", async () => {
    const shown = await html(<OpenView links={openLinks("/open/team/t_9c2")!} device="computer" phase="trying" />);
    expect(shown).toContain("Opening the task in the QualityLayer App");
  });

  it("says a link that is not one of ours is not valid, and offers no way on", async () => {
    const shown = await at("/open/ask/..%2f/x");
    expect(shown).toContain("This link is not valid");
    expect(shown).not.toContain("qualitylayer://");
    expect(shown).not.toContain("127.0.0.1");
  });

  it("tries the App in a hidden frame from the first moment, and makes no request", async () => {
    const fetchFn = vi.fn();
    vi.stubGlobal("fetch", fetchFn);
    const shown = await at("/open/ask/t_9c2/7f3a");
    expect(shown).toContain("Opening the ask in the QualityLayer App");
    expect(shown).toMatch(/<iframe hidden="" title="" src="qualitylayer:\/\/ask\/t_9c2\/7f3a">/);
    expect(fetchFn).not.toHaveBeenCalled();
  });
});

describe("page statistics", () => {
  const measured = (path: string) =>
    html(
      <MemoryRouter initialEntries={[path]}>
        <Metrics />
      </MemoryRouter>,
    );

  it("run on the site's pages and not on the landing page, which sends nothing", async () => {
    expect(await measured("/pricing")).toContain("analytics");
    expect(await measured("/download")).toContain("speed-insights");
    expect(await measured("/open/ask/t_9c2/7f3a")).toBe("");
  });
});

describe("the landing page on a phone", () => {
  it("sends the reader to their computer and offers the link to copy, with no attempt and no buttons for the App", async () => {
    const shown = await html(<OpenView links={openLinks("/open/ask/t_9c2/7f3a")!} device="phone" phase="offer" />);
    expect(shown).toContain("Open this on your computer");
    expect(shown).toContain("Copy the link");
    expect(shown).not.toContain("qualitylayer://");
    expect(shown).not.toContain("<iframe");
  });

  it("takes an iPhone, an iPad and an Android phone for a phone, a Mac and a PC not", () => {
    expect(isPhone("Mozilla/5.0 (iPhone; CPU iPhone OS 18_0 like Mac OS X) AppleWebKit/605.1.15")).toBe(true);
    expect(isPhone("Mozilla/5.0 (iPad; CPU OS 18_0 like Mac OS X) AppleWebKit/605.1.15")).toBe(true);
    expect(isPhone("Mozilla/5.0 (Linux; Android 15; Pixel 9) AppleWebKit/537.36 Chrome/130 Mobile Safari/537.36")).toBe(true);
    expect(isPhone("Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 Safari/605.1.15")).toBe(false);
    expect(isPhone("Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 Chrome/130 Safari/537.36")).toBe(false);
  });
});
