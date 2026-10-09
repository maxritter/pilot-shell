import { renderToReadableStream } from "react-dom/server.browser";
import { HelmetProvider } from "react-helmet-async";
import { MemoryRouter, Route, Routes } from "react-router-dom";
import { afterEach, describe, expect, it, vi } from "vitest";
import { Metrics } from "@/App";
import { isPhone } from "@/lib/device";
import { type AttemptTarget, startAttempt } from "@/lib/open-attempt";
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

  it("maps a step link to the step of the task, in the App, the browser page and the App link, for the seven step names only", () => {
    expect(openLinks("/open/step/abc/verify")).toEqual({
      path: "step/abc/verify",
      app: "qualitylayer://step/abc/verify",
      browser: "http://127.0.0.1:41888/#/step/abc/verify",
    });
    for (const step of ["discuss", "research", "plan", "outline", "implement", "verify", "review"]) {
      expect(openLinks(`/open/step/abc/${step}`), step).toMatchObject({ app: `qualitylayer://step/abc/${step}` });
    }
    for (const bad of ["/open/step/abc/deploy", "/open/step/abc/Verify", "/open/step/abc", "/open/step/abc/verify/x", "/open/step/..%2f/verify", "/open/step/../verify", "/open/step/abc/%2e%2e"]) {
      expect(openLinks(bad), bad).toBeNull();
    }
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
    expect(shown).toContain("Nothing happened? Pick one:");
    expect(fetchFn).not.toHaveBeenCalled();
  });

  it("makes Open in the App the one filled button, the browser a plain one and the download a link", async () => {
    const shown = await html(<OpenView links={openLinks("/open/ask/t_9c2/7f3a")!} device="computer" phase="offer" />);
    expect(shown).toMatch(/<a [^>]*data-slot="button" data-variant="default"[^>]*>Open in the App<\/a>/);
    expect(shown).toMatch(/<a [^>]*data-slot="button" data-variant="outline"[^>]*>Open in this browser<\/a>/);
    expect(shown).toMatch(/<a class="ap-link" href="\/download">Get the QualityLayer App<\/a>/);
  });

  it("says it is trying the App while the attempt runs, and shows no buttons yet", async () => {
    const shown = await html(<OpenView links={openLinks("/open/ask/t_9c2/7f3a")!} device="computer" phase="trying" />);
    expect(shown).toContain("Opening the question in the QualityLayer App");
    expect(shown).not.toContain("Open in this browser");
    expect(shown).not.toContain("Nothing happened?");
  });

  it("says the App opened once it did, tells the reader to close the tab, and keeps the options one press away", async () => {
    const shown = await html(<OpenView links={openLinks("/open/ask/t_9c2/7f3a")!} device="computer" phase="opened" />);
    expect(shown).toContain("Opened in the QualityLayer App");
    expect(shown).toContain("You can close this tab.");
    expect(shown).toContain("Nothing opened?");
    expect(shown).not.toContain('href="http://127.0.0.1:41888');
    expect(shown).not.toContain("Open in this browser");
  });

  it("names an ask link a question and a team link a task", async () => {
    const shown = await html(<OpenView links={openLinks("/open/team/t_9c2")!} device="computer" phase="trying" />);
    expect(shown).toContain("Opening the task in the QualityLayer App");
    expect(shown).not.toContain("question");
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
    expect(shown).toContain("Opening the question in the QualityLayer App");
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
    expect(shown).toContain("Questions are answered in the QualityLayer App, where the Plan and your agent are.");
    expect(shown).toMatch(/<button data-slot="button" data-variant="outline"[^>]*type="button">Copy the link<\/button>/);
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

  it("says tasks open in the App for a team link", async () => {
    const shown = await html(<OpenView links={openLinks("/open/team/t_9c2")!} device="phone" phase="offer" />);
    expect(shown).toContain("Tasks open in the QualityLayer App, where the Plan and your agent are.");
  });
});

/** The attempt: the App gets 1.5 s to open, which the page sees as the browser losing focus. */
describe("the attempt to open the App", () => {
  afterEach(() => vi.useRealTimers());

  const setup = () => {
    vi.useFakeTimers();
    const win = new EventTarget();
    const doc = Object.assign(new EventTarget(), { visibilityState: "visible" as DocumentVisibilityState });
    const seen: string[] = [];
    const stop = startAttempt({ win: win as unknown as AttemptTarget["win"], doc: doc as unknown as AttemptTarget["doc"], ms: 1500, onPhase: (phase) => seen.push(phase) });
    return { win, doc, seen, stop };
  };

  it("offers the three ways on when nothing happened within 1.5 seconds", () => {
    const { seen } = setup();
    vi.advanceTimersByTime(1499);
    expect(seen).toEqual([]);
    vi.advanceTimersByTime(1);
    expect(seen).toEqual(["offer"]);
  });

  it("calls the App open when the window loses focus within the time, and then never offers the buttons by itself", () => {
    const { win, seen } = setup();
    vi.advanceTimersByTime(600);
    win.dispatchEvent(new Event("blur"));
    expect(seen).toEqual(["opened"]);
    vi.advanceTimersByTime(5000);
    expect(seen).toEqual(["opened"]);
  });

  it("takes the page being hidden for the App opening as well", () => {
    const { doc, seen } = setup();
    doc.visibilityState = "hidden";
    doc.dispatchEvent(new Event("visibilitychange"));
    expect(seen).toEqual(["opened"]);
  });

  it("does not take the page becoming visible again for it, and ignores a blur after the time is over", () => {
    const { doc, win, seen } = setup();
    doc.dispatchEvent(new Event("visibilitychange"));
    expect(seen).toEqual([]);
    vi.advanceTimersByTime(1500);
    win.dispatchEvent(new Event("blur"));
    expect(seen).toEqual(["offer"]);
  });

  it("stops listening and counting when the page goes away", () => {
    const { win, seen, stop } = setup();
    stop();
    win.dispatchEvent(new Event("blur"));
    vi.advanceTimersByTime(5000);
    expect(seen).toEqual([]);
  });
});
