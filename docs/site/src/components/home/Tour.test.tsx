import { renderToReadableStream } from "react-dom/server.browser";
import { describe, expect, it } from "vitest";
import { BANNED_WORDS } from "@/lib/banned-words";
import { CHAPTERS, PARTS, sidebarOf, statusOf, STAGES, tabsOf } from "@/lib/tour";
import Tour from "./Tour";
import TourScenes, { RightSide } from "./TourScenes";

async function html(node: React.ReactNode): Promise<string> {
  const stream = await renderToReadableStream(node);
  await stream.allReady;
  return new Response(stream).text();
}

const render = () => html(<Tour />);
const scene = (ch: number, step = 99) => html(<TourScenes ch={ch} step={step} tries={2} onRetry={() => {}} only />);
const side = (ch: number, tab: "comments" | "designs", step = 99) => html(<RightSide ch={ch} step={step} tab={tab} />);

const text = (s: string) => s.replace(/<[^>]+>/g, " ").replaceAll("&#x27;", "'").replaceAll("&amp;", "&").replaceAll("&quot;", '"').replace(/\s+/g, " ");
const id = (name: string) => CHAPTERS.findIndex((c) => c.id === name);

describe("the tour", () => {
  it("tells every chapter, with the five steps of a task in the App", async () => {
    const page = await render();
    for (const chapter of CHAPTERS) {
      expect(page).toContain(`id="${chapter.id}"`);
      expect(text(page)).toContain(chapter.title);
    }
    for (const stage of STAGES) expect(text(page)).toContain(stage);
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
    expect(team / steps).toBeGreaterThan(0.6);
    expect(team / steps).toBeLessThan(1.33);
  });

  it("draws each task's header with its step's file and the live status pill, in place of the old step line", async () => {
    const files = ["discuss", "plan", "start", "verify", "review"].map((name) => CHAPTERS[id(name)].win.file?.[0]);
    expect(files).toEqual(["01-discuss.md", "02-plan.md", "03-implement.md", "04-verify.md", "05-review.md"]);
    const page = await render();
    expect(page).toContain("sx-pill");
    expect(page).toContain("sx-fchip");
    expect(page).not.toMatch(/"sx-line[ "]/);
    expect(statusOf(id("discuss"), 0).pill).toMatchObject({ kind: "you", head: "Needs you", text: "question 3" });
    expect(statusOf(id("start"), 0).pill).toMatchObject({ kind: "move", head: "Your move", text: "start the build" });
    expect(statusOf(id("implement"), 0).pill.kind).toBe("ag");
    expect(statusOf(id("verify"), 0).pill.head).toBe("Claude Code");
  });

  it("names what needs you in one line at the top of the step, and drops the line when nothing does", () => {
    expect(statusOf(id("plan"), 0).index).toEqual({ count: "2 things need you", to: ["Decision 2", "The design"], then: "Approve" });
    expect(statusOf(id("implement"), 99).index).toBeUndefined();
    expect(statusOf(id("together"), 99).index).toBeUndefined();
  });

  it("puts “+ New” beside the logo", async () => {
    expect(text(await render())).toContain("QualityLayer New");
  });

  it("asks in the App: the question card takes a choice, your own answer, Tell me more, or your recommendation", async () => {
    const first = text(await scene(id("discuss"), 2));
    for (const word of ["How many tries before it stops?", "question 3 · about 2 to come", "Claude Code waits", "Recommended", "Your own answer", "Tell me more", "Not sure, use your recommendation"]) expect(first).toContain(word);
    const after = text(await scene(id("discuss")));
    expect(after).toContain("Answered");
    expect(after).toContain("Who hears about it when it stops?");
    expect(after).toContain("Decided with you");
    expect(after).not.toMatch(/in the chat|in the terminal/i);
  });

  it("reviews the Plan in the same card, decision by decision, then asks “Approve the Plan?”", async () => {
    const asking = text(await scene(id("plan"), 2));
    for (const word of ["Three tries, then one mail. Agree?", "decision 2 of 3, then Approve the Plan?", "Agree", "Codex read the Plan"]) expect(asking).toContain(word);
    const approve = text(await scene(id("plan")));
    for (const word of ["Approve the Plan?", "Decision 1", "The design", "Approve", "Your call"]) expect(approve).toContain(word);
  });

  it("starts the build from Implement Start: the Build defaults as an orchestrator and its workers, one effort for both, one command", async () => {
    const html2 = text(await scene(id("start")));
    for (const word of ["Start the build", "Build with", "Claude Code", "Codex", "Another agent", "Orchestrator", "Opus 5.5", "Workers", "Sonnet 5.5", "Effort for both", "/clear", "/goal /ql implement retry-webhooks"]) expect(html2).toContain(word);
  });

  it("builds on its own: slices test first, what the agent decided while building answered with Ask why", async () => {
    const html2 = text(await scene(id("implement")));
    for (const word of ["Slice 2 of 3", "committed", "Nothing waits for you", "Decided while building", "Ask why", "Checked by agents"]) expect(html2).toContain(word);
  });

  it("draws Verify as one checklist that fills in, then ends passed with the list for Review", async () => {
    expect(text(await scene(id("verify"), 3))).toMatch(/\d+ of 12 checks passed/);
    const done = text(await scene(id("verify")));
    expect(done).toContain("Waiting for you in Review");
    expect(done).toContain("Only you can confirm");
  });

  it("draws Review with what is settled with you, the proof and “Approve the change?” with the ways to ship", async () => {
    const html2 = text(await scene(id("review")));
    for (const word of ["Settled with you", "Only you can confirm", "Look at the result", "Found while checking", "Approve the change?", "Approve and open a pull request", "Approve only", "Copy the git commands"]) expect(html2).toContain(word);
  });

  it("draws designs: the Plan's preview with Open full size, the Designs tab that never shares, a design open full size with a comment on a spot", async () => {
    const plan = text(await scene(id("draw")));
    for (const word of ["Interface", "Preview", "Open full size", "Is this how failed deliveries should look?", "Failed deliveries was updated"]) expect(plan).toContain(word);
    const tab = text(await side(id("draw"), "designs"));
    for (const word of ["Comments", "Designs", "Only on this computer.", "Never shared.", "This task", "In this project", "Shown in the Plan", "Ask your agent to draw one"]) expect(tab).toContain(word);
    const full = text(await scene(id("comment"), 2));
    for (const word of ["Click a spot on the design", "this spot", "Say when it tries next."]) expect(full).toContain(word);
    expect(text(await scene(id("comment")))).toContain("Each failed row now says when it tries next.");
    expect(CHAPTERS[id("comment")].win.view).toBe("design");
    expect(CHAPTERS[id("draw")].win.right).toBe("designs");
  });

  it("says what designs never do: leave the computer, reach a share link, the website or a pull request", () => {
    const words = CHAPTERS.filter((c) => c.id === "draw" || c.id === "together").map((c) => [c.text, ...c.bullets, c.act?.text ?? ""].join(" ")).join(" ");
    expect(CHAPTERS[id("draw")].act?.text).toMatch(/never leaves your computer/);
    expect(words).toMatch(/Never on a share link, the website or a pull request/);
    expect(words).toMatch(/never your code or your designs/);
  });

  it("draws the team's chapters in the App's words: a question on a passage, Slack, Questions for you, review together with Comments", async () => {
    expect(text(await scene(id("ask")))).toContain("Ask about this passage");
    expect(text(await scene(id("ask")))).toContain("Open the question in the QualityLayer App");
    const answer = text(await scene(id("answer"), 4));
    for (const word of ["Questions for you", "Draft with my agent", "Send the draft", "Hand to someone else"]) expect(answer).toContain(word);
    const comments = text(await side(id("together"), "comments", 3));
    for (const word of ["Open on Review", "Ben Chen", "Done means · point 3", "Claude Code", "Reply", "Resolve"]) expect(comments).toContain(word);
  });

  it("explains that opening or reloading the link reads the latest shared copy, and keeps designs local", async () => {
    const together = text(await scene(id("together")));
    expect(together).toContain("Open the link to read the latest shared copy. Reload to see later changes.");
    expect(together).not.toContain("as of the time on it");
    expect(together).toContain("Designs stay on your computer");
  });

  const counts = (ch: string, step: number) => tabsOf(id(ch), step).map((t) => t.count).filter((c) => c !== undefined);
  const sideSubs = (ch: string, step: number) => sidebarOf(id(ch), step).flatMap((g) => g.items.filter((i) => i.on).map((i) => i.sub));

  it("counts nothing once you have answered: the finished frames carry no count of what you settled", () => {
    expect(counts("together", 4)).toEqual([]);
    expect(sideSubs("together", 4)).toEqual(["Review · ready to approve"]);
    expect(counts("together", 1)).toEqual([1]);
    expect(counts("plan", 0)).toEqual([2]);
    expect(counts("plan", 99)).toEqual([1]);
    expect(counts("review", 99)).toEqual([]);
    expect(sidebarOf(id("answer"), 5)[0].count).toBe(1);
    expect(sidebarOf(id("answer"), 0)[0].count).toBe(2);
  });

  it("moves the task to Needs you with its three items once Verify has passed, as the tabs do", () => {
    expect(sideSubs("verify", 99)).toEqual(["Review · 3 to answer"]);
    expect(sidebarOf(id("verify"), 99)[0].count).toBe(1);
    expect(counts("verify", 99)).toEqual([3]);
    expect(sidebarOf(id("verify"), 3)[0].count).toBe(0);
  });

  it("counts tasks done on the Implement tab and in the sidebar, and checks passed on the Verify tab", () => {
    expect(counts("implement", 99)).toEqual(["3/5"]);
    expect(sideSubs("implement", 99)).toEqual(["3/5"]);
    expect(counts("verify", 3)).toEqual(["8/12"]);
    expect(tabsOf(id("start"), 0)[2].mark).toBe("you");
    expect(tabsOf(id("start"), 0)[1].lit).toBe(true);
  });

  it("shows teammates what the team can see: a point of the review and its proof, never a diff or source", async () => {
    const html2 = text(await scene(id("together"), 5));
    expect(html2).toContain("Done means · 3");
    expect(html2).not.toMatch(/\bdiff\b|line \d+|\.tsx|row\.event/i);
    expect(CHAPTERS[id("together")].text).toContain("The code itself is reviewed in your pull request");
  });

  it("draws Settings with Planning and Build defaults per agent and the independent review, and “+ New” with one command", async () => {
    const settings = text(await scene(id("settings")));
    for (const word of ["Planning defaults", "Build defaults", "Orchestrator", "Workers", "Effort for both", "Independent review", "estimated at list price"]) expect(settings).toContain(word);
    const agents = text(await scene(id("agents")));
    for (const word of ["New task", "What do you want to build or fix?", "Claude Code", "Codex", "Another agent", "Copied", "Retry failed webhooks needs your review"]) expect(agents).toContain(word);
  });

  it("paints no planned step as a failure: red is for failures only", async () => {
    expect(await scene(id("plan"), 2)).not.toContain("sx-node stop");
  });

  it("never uses the App's internal words or the elements the redesign removed", async () => {
    const all = text(await render()) + CHAPTERS.map((c) => JSON.stringify(c)).join(" ");
    for (const scenes of await Promise.all(CHAPTERS.map((_, i) => scene(i)))) expect(text(scenes)).not.toMatch(BANNED_WORDS);
    expect(all).not.toMatch(BANNED_WORDS);
    expect(all).not.toMatch(/for you \/ for the agent|for the agent|quality pass|files tab|claude design|links\b|frames?\b|versions?\b/i);
  });

  it("never sends the person to the terminal to answer", async () => {
    const all = text(await render()) + CHAPTERS.map((c) => JSON.stringify(c)).join(" ");
    expect(all).not.toMatch(/(answer|approve|asks?)[^.]{0,40}in the (terminal|chat)/i);
  });

  it("names the App by its name only", async () => {
    expect(await render()).not.toMatch(/cockpit/i);
  });
});
