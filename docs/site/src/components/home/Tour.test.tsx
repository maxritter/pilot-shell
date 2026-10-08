import { renderToReadableStream } from "react-dom/server.browser";
import { describe, expect, it } from "vitest";
import { BANNED_WORDS } from "@/lib/banned-words";
import { CHAPTERS, checksPassed, committedTasks, discussAt, PARTS, STAGES } from "@/lib/tour";
import CloseUp from "./CloseUps";
import Tour from "./Tour";

async function html(node: React.ReactNode): Promise<string> {
  const stream = await renderToReadableStream(node);
  await stream.allReady;
  return new Response(stream).text();
}

const render = () => html(<Tour />);
const shot = (id: string, step = 99) => html(<CloseUp id={id} step={step} />);
const text = (s: string) => s.replace(/<[^>]+>/g, " ").replaceAll("&#x27;", "'").replaceAll("&amp;", "&").replaceAll("&quot;", '"').replace(/\s+/g, " ");

describe("the tour", () => {
  it("tells every chapter and draws a close-up of the App for each", async () => {
    const page = await render();
    for (const chapter of CHAPTERS) {
      expect(page).toContain(`id="${chapter.id}"`);
      expect(text(page)).toContain(chapter.title);
      expect(await shot(chapter.id)).toContain('class="cu"');
    }
  });

  it("keeps the anchors the header and other pages link to, each once", async () => {
    const page = await render();
    for (const name of ["tour", "designs", "team", "setup"]) expect(page.match(new RegExp(`id="${name}"`, "g"))).toHaveLength(1);
  });

  it("opens each of its four parts with a heading: the steps for you alone first, then designs, the team and the setup", () => {
    expect(PARTS.map((p) => p.label)).toEqual(["Steps", "Designs", "Team", "Setup"]);
    expect(CHAPTERS[0].act?.text).toMatch(/alone|your own/i);
    expect(CHAPTERS[PARTS[1].from].act?.id).toBe("designs");
    expect(CHAPTERS[PARTS[2].from].act?.id).toBe("team");
  });

  it("gives the steps for one person and the team's chapters about the same room", () => {
    const sentences = (from: number, to: number) =>
      CHAPTERS.slice(from, to + 1).reduce((n, c) => n + [c.title, c.text, ...c.bullets, ...(c.act ? [c.act.title, c.act.text] : [])].join(" ").split(/[.!?](?:\s|$)/).filter(Boolean).length, 0);
    const [steps, team] = [sentences(PARTS[0].from, PARTS[0].to), sentences(PARTS[2].from, PARTS[2].to)];
    expect(team / steps).toBeGreaterThan(0.5);
    expect(team / steps).toBeLessThan(1.33);
  });

  it("draws the App's top bar on a task: the five steps, the current one marked, and the agent chip", async () => {
    const plan = await shot("plan", 0);
    for (const stage of STAGES) expect(text(plan)).toContain(stage);
    expect(plan).toMatch(/<li class="cur">Plan<\/li>/);
    expect(plan).toContain("cu-chip");
    expect(text(plan)).toContain("Claude Code");
  });

  it("asks one Discuss question at a time with numbered choices, the recommendation and the own-words field", async () => {
    expect(discussAt(0)).toEqual({ shown: 0, answered: 0, picked: false });
    expect(discussAt(6)).toMatchObject({ shown: 3, answered: 3 });
    const first = text(await shot("discuss", 0));
    expect(first).toContain("How many tries before it stops?");
    expect(first).toContain("recommended");
    expect(first).toContain("Or write your own answer");
    expect(first).toContain("Your turn · 3 questions");
    const second = text(await shot("discuss", 2));
    expect(second).toContain("Sent to Claude Code");
    expect(second).toContain("Who hears about it when it stops?");
    const done = text(await shot("discuss", 6));
    expect(done).toContain("Writing Done means from your answers");
    expect(done).toContain("Nothing needs you now");
  });

  it("keeps everything that waits for the person in the one amber Your turn card", async () => {
    for (const [id, step] of [["discuss", 0], ["plan", 0], ["start", 0], ["review", 0], ["draw", 2], ["answer", 0], ["together", 0]] as const) {
      expect((await shot(id, step)).match(/class="cu-yt"/g), id).toHaveLength(1);
    }
    for (const [id, step] of [["implement", 2], ["verify", 2]] as const) expect(await shot(id, step), id).not.toContain('class="cu-yt"');
  });

  it("shows a decision as a diagram, the words that changed, and Approve after everything is settled", async () => {
    expect(await shot("plan", 0)).toContain("cu-dgm");
    expect(text(await shot("plan", 2))).toContain("When the endpoint recovers, who starts a new attempt?");
    expect(text(await shot("plan", 4))).toContain("Approve Plan");
    expect(await shot("plan", 4)).not.toContain('class="cu-yt"');
    expect(text(await shot("plan", 4))).toContain("Give feedback");
  });

  it("starts the build from one line of Build defaults and one command", async () => {
    const start = text(await shot("start"));
    expect(start).toContain("Opus 5.5");
    expect(start).toContain("Sonnet 5.5");
    expect(start).toContain("/ql implement retry-webhooks");
    expect(start).not.toContain("/goal /ql implement");
  });

  it("builds on its own, test first, and counts the committed tasks", async () => {
    expect(committedTasks(4)).toBe(3);
    const build = text(await shot("implement", 4));
    expect(build).toContain("3 of 5 tasks committed");
    expect(build).toContain("Ask why");
    expect(text(await shot("implement", 5))).toContain("Checked by agents");
  });

  it("fills Verify in point by point, then hands what only a person can settle to Review", async () => {
    expect(checksPassed(99)).toBe(12);
    expect(text(await shot("verify", 2))).toMatch(/\d+ of 12/);
    const done = text(await shot("verify", 7));
    expect(done).toContain("12 of 12 passed");
    expect(done).toContain("Your turn · 2 in Review");
  });

  it("draws Review with what only you can confirm, then Approve and the ways to ship", async () => {
    expect(text(await shot("review", 0))).toContain("Only you can confirm");
    expect(text(await shot("review", 0))).toContain("I confirm");
    const last = text(await shot("review", 5));
    expect(last).toContain("Approve the change?");
    expect(last).toContain("Approve and open a pull request");
  });

  it("shows the design inside the question it belongs to, and keeps the full-size design clickable", async () => {
    expect(await shot("draw", 2)).toContain("cu-dz");
    expect(await shot("comment", 6)).toContain("cu-dpb");
    expect(text(await shot("comment", 6))).toContain("Each failed row now says when it tries next");
  });

  it("draws the team's chapters in the App's words", async () => {
    expect(text(await shot("ask", 0))).toContain("Ask the team about this passage");
    expect(text(await shot("ask", 5))).toContain("via Claude Code");
    expect(text(await shot("answer", 3))).toContain("Draft by your Claude Code · not sent yet");
    expect(text(await shot("space"))).toContain("Working now");
    expect(text(await shot("together", 5))).toContain("Ready to approve");
  });

  it("draws Settings with Planning and Build defaults and the cost of each step, and New task with one command", async () => {
    const settings = text(await shot("settings"));
    for (const words of ["Planning defaults", "Build defaults", "$20.95", "estimated at list price"]) expect(settings).toContain(words);
    expect(text(await shot("agents"))).toContain('claude --model opus --effort high');
  });

  it("paints red only for a delivery that stopped, never for a planned step", async () => {
    for (const chapter of CHAPTERS) {
      const page = await shot(chapter.id);
      for (const match of page.matchAll(/class="red"[^<]*>([^<]*)/g)) expect(match[1]).toMatch(/Stopped/);
    }
  });

  it("never uses the App's internal words, and never sends the person to the terminal to answer", async () => {
    const all = text(await render()) + CHAPTERS.map((c) => JSON.stringify(c)).join(" ") + (await Promise.all(CHAPTERS.map((c) => shot(c.id, 0)))).map(text).join(" ");
    expect(all).not.toMatch(BANNED_WORDS);
    expect(all).not.toMatch(/for the agent|quality pass|claude design|cockpit/i);
    expect(all).not.toMatch(/(answer|approve|asks?)[^.]{0,40}in the (terminal|chat)/i);
  });
});
