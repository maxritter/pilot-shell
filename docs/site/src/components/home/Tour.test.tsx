import { renderToReadableStream } from "react-dom/server.browser";
import { describe, expect, it } from "vitest";
import { BANNED_WORDS } from "@/lib/banned-words";
import { CHAPTERS, PARTS, sidebarOf, stepLine, STAGES, tabsOf } from "@/lib/tour";
import Tour from "./Tour";
import TourScenes from "./TourScenes";

async function render(): Promise<string> {
  const stream = await renderToReadableStream(<Tour />);
  await stream.allReady;
  return new Response(stream).text();
}

async function scene(ch: number, step = 99): Promise<string> {
  const stream = await renderToReadableStream(<TourScenes ch={ch} step={step} tries={2} onRetry={() => {}} only />);
  await stream.allReady;
  return new Response(stream).text();
}

const text = (html: string) => html.replace(/<[^>]+>/g, " ").replaceAll("&#x27;", "'").replaceAll("&amp;", "&").replace(/\s+/g, " ");
const id = (name: string) => CHAPTERS.findIndex((c) => c.id === name);

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
    for (const name of ["tour", "team", "setup"]) expect(html.match(new RegExp(`id="${name}"`, "g"))).toHaveLength(1);
  });

  it("opens each of the three parts with a heading, the steps for you alone first", () => {
    expect(PARTS.map((p) => p.label)).toEqual(["Steps", "Team", "Setup"]);
    expect(CHAPTERS[0].act?.text).toMatch(/alone|your own/i);
    expect(CHAPTERS[PARTS[1].from].act?.id).toBe("team");
  });

  it("gives the steps for one person and the team's chapters about the same room", () => {
    const sentences = (from: number, to: number) =>
      CHAPTERS.slice(from, to + 1).reduce((n, c) => n + [c.title, c.text, ...c.bullets, ...(c.act ? [c.act.title, c.act.text] : [])].join(" ").split(/[.!?](?:\s|$)/).filter(Boolean).length, 0);
    const [steps, team] = [sentences(PARTS[0].from, PARTS[0].to), sentences(PARTS[1].from, PARTS[1].to)];
    expect(team / steps).toBeGreaterThan(0.75);
    expect(team / steps).toBeLessThan(1.33);
  });

  it("starts Implement from a command the user types after approving the plan", () => {
    const plan = id("plan");
    expect(stepLine(plan, 99).code).toMatch(/^\/ql implement /);
    expect(stepLine(plan, 0).buttons.map(([label]) => label)).toEqual(["Request changes…", "Approve"]);
  });

  it("renders a single scene for a chapter's inline window", async () => {
    const html = await scene(id("verify"));
    expect(html.match(/class="sx-sc/g)).toHaveLength(1);
    expect(html).toContain('class="sx-sc on"');
  });

  it("shows each step with the parts of the anatomy: whose turn it is, Needs you, the violet line", async () => {
    const heads = ["discuss", "plan", "implement", "verify", "review"].map((name) => stepLine(id(name), 0).head);
    expect(heads).toEqual(["Waits for your answer", "Waits for your approval", "Agents are building", "Agents are checking", "Waits for your review"]);
    expect(text(await scene(id("plan"), 5))).toContain("Needs you");
    expect(text(await scene(id("review")))).toContain("Needs you");
    for (const name of ["plan", "implement", "review"]) expect(text(await scene(id(name)))).toContain("Checked by agents");
  });

  it("draws the Plan with its mockup, an engineering decision with its diagram, Done means and Extra review", async () => {
    const html = text(await scene(id("plan"), 5));
    for (const word of ["Mockup", "Engineering decision", "Done means", "Decided by the agent", "Extra review", "Agree", "Looks right"]) expect(html).toContain(word);
  });

  it("draws Implement with slices and what the agent decided while building, answered Fine or Ask why", async () => {
    const html = text(await scene(id("implement")));
    for (const word of ["Decided by the agent while building", "Fine", "Ask why", "The build", "committed"]) expect(html).toContain(word);
  });

  it("draws Verify as one checklist that fills in, then ends passed with the list for Review", async () => {
    expect(text(await scene(id("verify"), 3))).toMatch(/\d+ of 12 checks passed/);
    expect(stepLine(id("verify"), 7).text).toContain("All 12 checks passed");
    const done = text(await scene(id("verify")));
    expect(done).toContain("Waiting for you in Review");
    expect(done).toContain("Only you can confirm");
  });

  it("draws Review with what only you can confirm, the result to look at, and the Approve menu with its pull request", async () => {
    const html = text(await scene(id("review")));
    for (const word of ["Only you can confirm", "Look at the result", "Found while checking", "Approve and open a pull request", "Approve only", "Copy the git commands"]) expect(html).toContain(word);
  });

  it("draws the team's chapters in the App's words: a question on a passage, Slack, Questions for you, review together", async () => {
    expect(text(await scene(id("ask")))).toContain("Ask about this passage");
    expect(text(await scene(id("ask")))).toContain("Open the question in the QualityLayer App");
    const answer = text(await scene(id("answer"), 4));
    for (const word of ["Questions for you", "Draft with my agent", "Send the draft", "Hand to someone else"]) expect(answer).toContain(word);
    expect(text(await scene(id("together")))).toContain("Comment from");
  });

  const counts = (ch: string, step: number) => tabsOf(id(ch), step).map((t) => t.count).filter((c) => c !== undefined);
  const sideSubs = (ch: string, step: number) => sidebarOf(id(ch), step).flatMap((g) => g.items.filter((i) => i.on).map((i) => i.sub));

  it("counts nothing once you have answered: the finished frames carry no count of what you settled", () => {
    // The Plan once approved: Plan 1b's line, "start" in the sidebar, no count on any tab.
    expect(counts("plan", 99)).toEqual([]);
    expect(sideSubs("plan", 99)).toEqual(["start"]);
    expect(stepLine(id("plan"), 99).head).toBe("Start the build");
    expect(stepLine(id("plan"), 99).seg).toEqual(["Claude Code", "Codex"]);
    // Review together once Ben's comment is answered.
    expect(counts("together", 4)).toEqual([]);
    expect(sideSubs("together", 4)).toEqual(["Review"]);
    expect(counts("together", 1)).toEqual([1]);
    // Discuss once the question is answered, and the Answer chapter once Dana has sent hers.
    expect(counts("discuss", 3)).toEqual([]);
    expect(sidebarOf(id("answer"), 5)[0].count).toBe(1);
    expect(sidebarOf(id("answer"), 0)[0].count).toBe(2);
  });

  it("moves the task to Needs you with its three items once Verify has passed, as the tabs do", () => {
    expect(sideSubs("verify", 99)).toEqual(["Review · 3"]);
    expect(sidebarOf(id("verify"), 99)[0].count).toBe(1);
    expect(counts("verify", 99)).toEqual([3]);
    expect(sidebarOf(id("verify"), 3)[0].count).toBe(0);
  });

  it("counts tasks done on the Implement tab and in the sidebar, and checks passed on the Verify tab", () => {
    expect(counts("implement", 99)).toEqual(["3/5"]);
    expect(sideSubs("implement", 99)).toEqual(["3/5"]);
    expect(counts("verify", 3)).toEqual(["8/12"]);
  });

  it("draws the Plan once approved as Plan 1b does", async () => {
    const html = text(await scene(id("plan")));
    for (const word of ["Approved by you at 13:27 · 5 items settled", "In Codex the command is $ql implement", "For another agent"]) expect(html).toContain(word);
    expect(html).not.toContain("Engineering decision");
  });

  it("settles Discuss's card once the question is answered", async () => {
    expect(text(await scene(id("discuss"), 2))).toContain("2 answered so far");
    const html = text(await scene(id("discuss"), 3));
    expect(html).toContain("3 answered so far");
    expect(html).toContain("Answered in Claude Code");
    expect(stepLine(id("discuss"), 3).who).toBe("ag");
  });

  it("settles a teammate's question once it is sent", async () => {
    const html = text(await scene(id("answer"), 5));
    expect(html).toContain("Answered by you");
    expect(html).toContain("1 open");
  });

  it("shows teammates what the team can see: a point of the review and its proof, never a diff or source", async () => {
    const html = text(await scene(id("together"), 5));
    expect(html).toContain("Done means · 3");
    expect(html).not.toMatch(/\bdiff\b|line \d+|\.tsx|row\.event/i);
    expect(CHAPTERS[id("together")].text).toContain("The code itself is reviewed in your pull request");
    expect(stepLine(id("together"), 0).text).not.toMatch(/line/);
  });

  it("splits Settings into Workers and Checking, and draws the last chapter in one moment: the review", async () => {
    const settings = text(await scene(id("settings")));
    expect(settings).toContain("Checking");
    const agents = text(await scene(id("agents")));
    expect(agents).toContain("Retry failed webhooks needs your review");
    expect(agents).toContain("waits for your review");
    expect(agents).not.toMatch(/Plan is ready|Plan ready/);
  });

  it("paints no planned step as a failure: red is for failures only", async () => {
    expect(await scene(id("plan"), 5)).not.toContain("sx-node stop");
  });

  it("never uses the App's internal words or the elements the redesign removed", async () => {
    const all = text(await render()) + CHAPTERS.map((c) => JSON.stringify(c)).join(" ");
    for (const scenes of await Promise.all(CHAPTERS.map((_, i) => scene(i)))) expect(text(scenes)).not.toMatch(BANNED_WORDS);
    expect(all).not.toMatch(BANNED_WORDS);
    expect(all).not.toMatch(/for you \/ for the agent|quality pass|links/i);
  });

  it("names the App by its name only", async () => {
    expect(await render()).not.toMatch(/cockpit/i);
  });
});
