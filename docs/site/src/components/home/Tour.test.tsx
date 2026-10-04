import { renderToReadableStream } from "react-dom/server.browser";
import { describe, expect, it } from "vitest";
import { CHAPTERS, nextBar, STAGES } from "@/lib/tour";
import Tour from "./Tour";
import TourScenes from "./TourScenes";

async function render(): Promise<string> {
  const stream = await renderToReadableStream(<Tour />);
  await stream.allReady;
  return new Response(stream).text();
}

const text = (html: string) => html.replace(/<[^>]+>/g, " ").replaceAll("&#x27;", "'").replace(/\s+/g, " ");

describe("the tour", () => {
  it("tells every chapter, with the five steps of a task in the App", async () => {
    const html = await render();
    for (const chapter of CHAPTERS) {
      expect(html).toContain(`id="${chapter.id}"`);
      expect(text(html)).toContain(chapter.title);
    }
    for (const stage of STAGES) expect(text(html)).toContain(stage);
  });

  it("keeps the anchors the header and other pages link to, each once", async () => {
    const html = await render();
    for (const id of ["tour", "team", "setup"]) expect(html.match(new RegExp(`id="${id}"`, "g"))).toHaveLength(1);
  });

  it("starts Implement from a command the user types after approving the plan", () => {
    const plan = CHAPTERS.findIndex((c) => c.id === "plan");
    expect(nextBar(plan, 6).code).toMatch(/^\/ql implement /);
    expect(nextBar(plan, 0).buttons.map(([label]) => label)).toContain("Approve");
  });

  it("renders a single scene for a chapter's inline window", async () => {
    const stream = await renderToReadableStream(<TourScenes ch={3} step={99} tries={2} onRetry={() => {}} only />);
    await stream.allReady;
    const html = await new Response(stream).text();
    expect(html.match(/class="sx-sc/g)).toHaveLength(1);
    expect(html).toContain('class="sx-sc on"');
  });

  it("names the App by its name only", async () => {
    expect(await render()).not.toMatch(/cockpit/i);
  });
});
